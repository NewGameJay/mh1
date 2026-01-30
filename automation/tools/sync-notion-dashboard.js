#!/usr/bin/env node

/**
 * Sync Notion Dashboard
 *
 * Orchestrates syncing all data types to Notion dashboard.
 * Runs posts sync, leads sync, and performance sync in sequence.
 *
 * Usage:
 *     node tools/sync-notion-dashboard.js --all
 *     node tools/sync-notion-dashboard.js --posts
 *     node tools/sync-notion-dashboard.js --leads
 *     node tools/sync-notion-dashboard.js --performance
 *     node tools/sync-notion-dashboard.js --all --dry-run
 *
 * Environment:
 *     NOTION_API_TOKEN - Notion integration token (from .env)
 *
 * Output (JSON):
 *     {
 *       "success": true,
 *       "synced": {
 *         "posts": { "uploaded": N, "skipped": N, "failed": N },
 *         "leads": { "uploaded": N, "skipped": N, "failed": N },
 *         "performance": { "updated": N }
 *       }
 *     }
 */

require('dotenv').config();
const { Client } = require('@notionhq/client');
const admin = require('firebase-admin');
const fs = require('fs');
const path = require('path');
const { execSync, spawn } = require('child_process');

// Paths
const SCRIPT_DIR = __dirname;
const PROJECT_ROOT = path.join(SCRIPT_DIR, '..');
const CONFIG_PATH = path.join(PROJECT_ROOT, 'config.md');

let db = null;
let notion = null;

/**
 * Load configuration from config.md
 */
function loadConfig() {
  if (!fs.existsSync(CONFIG_PATH)) {
    throw new Error(`Config file not found: ${CONFIG_PATH}`);
  }

  const content = fs.readFileSync(CONFIG_PATH, 'utf-8');
  const config = {};

  // Parse Service Account
  let match = content.match(/\*\*Service Account:\*\*\s*`([^`]+)`/);
  if (match) {
    config.serviceAccount = match[1];
  }

  // Parse Collection
  match = content.match(/\*\*Collection:\*\*\s*`([^`]+)`/);
  if (match) {
    config.collection = match[1];
  }

  // Parse Client ID
  match = content.match(/\*\*Client ID:\*\*\s*`([^`]+)`/);
  if (match) {
    config.clientId = match[1];
  }

  // Validate required fields
  const required = ['serviceAccount', 'collection', 'clientId'];
  const missing = required.filter(f => !config[f]);
  if (missing.length > 0) {
    throw new Error(`Missing config fields: ${missing.join(', ')}`);
  }

  return config;
}

/**
 * Initialize Firebase Admin SDK
 */
function initializeFirebase(serviceAccountFile) {
  if (admin.apps.length > 0) {
    return admin.firestore();
  }

  const serviceAccountPath = path.join(PROJECT_ROOT, serviceAccountFile);
  if (!fs.existsSync(serviceAccountPath)) {
    throw new Error(`Service account file not found: ${serviceAccountPath}`);
  }

  const serviceAccount = require(serviceAccountPath);
  admin.initializeApp({
    credential: admin.credential.cert(serviceAccount)
  });

  return admin.firestore();
}

/**
 * Initialize Notion client
 */
function initializeNotion() {
  const token = process.env.NOTION_API_TOKEN;
  if (!token) {
    throw new Error('NOTION_API_TOKEN not found in environment. Add it to .env file.');
  }

  return new Client({ auth: token });
}

/**
 * Run a tool script and return parsed JSON output
 */
function runTool(scriptPath, args = []) {
  return new Promise((resolve, reject) => {
    const fullPath = path.join(PROJECT_ROOT, scriptPath);

    if (!fs.existsSync(fullPath)) {
      reject(new Error(`Tool not found: ${fullPath}`));
      return;
    }

    try {
      const result = execSync(`node "${fullPath}" ${args.join(' ')}`, {
        cwd: PROJECT_ROOT,
        encoding: 'utf-8',
        maxBuffer: 10 * 1024 * 1024 // 10MB buffer
      });

      try {
        resolve(JSON.parse(result));
      } catch (e) {
        // Return raw output if not JSON
        resolve({ success: true, raw: result });
      }
    } catch (error) {
      // Try to parse stderr as JSON
      try {
        const errorOutput = error.stderr || error.stdout || error.message;
        const parsed = JSON.parse(errorOutput);
        reject(new Error(parsed.error || 'Tool execution failed'));
      } catch (e) {
        reject(new Error(error.message));
      }
    }
  });
}

/**
 * Sync posts to Notion
 */
async function syncPosts(dryRun = false) {
  console.error('📝 Syncing posts to Notion...');

  const args = ['--all'];
  if (dryRun) args.push('--dry-run');

  try {
    const result = await runTool('tools/upload-posts-to-notion.js', args);

    return {
      success: result.success,
      uploaded: result.uploaded?.length || 0,
      skipped: result.skipped?.length || 0,
      failed: result.failed?.length || 0,
      details: result
    };
  } catch (error) {
    return {
      success: false,
      error: error.message,
      uploaded: 0,
      skipped: 0,
      failed: 0
    };
  }
}

/**
 * Sync leads to Notion
 * Fetches leads from Firestore and uploads to Notion
 */
async function syncLeads(collection, clientId, dryRun = false) {
  console.error('👥 Syncing leads to Notion...');

  try {
    // Fetch leads from Firestore
    const leadsRef = db
      .collection(collection)
      .doc(clientId)
      .collection('leads');

    const snapshot = await leadsRef.get();

    if (snapshot.empty) {
      return {
        success: true,
        uploaded: 0,
        skipped: 0,
        failed: 0,
        message: 'No leads in Firestore'
      };
    }

    const leads = [];
    snapshot.forEach(doc => {
      leads.push({
        id: doc.id,
        ...doc.data()
      });
    });

    // Write to temp file
    const tempFile = path.join(PROJECT_ROOT, '.tmp-leads-sync.json');
    fs.writeFileSync(tempFile, JSON.stringify(leads, null, 2));

    // Run upload tool
    const args = ['--file', tempFile];
    if (dryRun) args.push('--dry-run');

    const result = await runTool('tools/upload-leads-to-notion.js', args);

    // Cleanup temp file
    if (fs.existsSync(tempFile)) {
      fs.unlinkSync(tempFile);
    }

    return {
      success: result.success,
      uploaded: result.uploaded?.length || 0,
      skipped: result.skipped?.length || 0,
      failed: result.failed?.length || 0,
      details: result
    };
  } catch (error) {
    return {
      success: false,
      error: error.message,
      uploaded: 0,
      skipped: 0,
      failed: 0
    };
  }
}

/**
 * Sync performance metrics to Notion
 * Updates existing Notion pages with engagement data
 */
async function syncPerformance(collection, clientId, dryRun = false) {
  console.error('📊 Syncing performance metrics to Notion...');

  try {
    // Get Notion database ID for posts
    const moduleRef = db
      .collection(collection)
      .doc(clientId)
      .collection('modules')
      .doc('linkedin-ghostwriter');

    const moduleDoc = await moduleRef.get();
    if (!moduleDoc.exists) {
      return {
        success: false,
        error: 'linkedin-ghostwriter module not found',
        updated: 0
      };
    }

    const databaseId = moduleDoc.data().notionDatabaseId;
    if (!databaseId) {
      return {
        success: false,
        error: 'notionDatabaseId not configured',
        updated: 0
      };
    }

    // Fetch posts with performance data from Firestore
    const postsRef = db
      .collection(collection)
      .doc(clientId)
      .collection('modules')
      .doc('linkedin-ghostwriter')
      .collection('posts')
      .where('status', '==', 'published');

    const snapshot = await postsRef.get();

    if (snapshot.empty) {
      return {
        success: true,
        updated: 0,
        message: 'No published posts to update'
      };
    }

    let updated = 0;
    let failed = 0;

    for (const doc of snapshot.docs) {
      const postData = doc.data();

      // Skip if no performance data
      if (!postData.performance) continue;

      // Find corresponding Notion page
      try {
        const queryResponse = await notion.databases.query({
          database_id: databaseId,
          filter: {
            property: 'Post ID',
            rich_text: {
              equals: postData.id || doc.id
            }
          }
        });

        if (queryResponse.results.length === 0) continue;

        const pageId = queryResponse.results[0].id;

        if (dryRun) {
          updated++;
          continue;
        }

        // Update Notion page with performance data
        await notion.pages.update({
          page_id: pageId,
          properties: {
            'Impressions': {
              number: postData.performance.impressions || 0
            },
            'Reactions': {
              number: postData.performance.reactions || 0
            },
            'Comments': {
              number: postData.performance.comments || 0
            },
            'Shares': {
              number: postData.performance.shares || 0
            },
            'Engagement Rate': {
              number: postData.performance.engagementRate || 0
            },
            'Last Updated': {
              date: { start: new Date().toISOString() }
            }
          }
        });

        updated++;
      } catch (error) {
        console.error(`Failed to update post ${doc.id}: ${error.message}`);
        failed++;
      }
    }

    return {
      success: true,
      updated,
      failed,
      total_posts: snapshot.size
    };
  } catch (error) {
    return {
      success: false,
      error: error.message,
      updated: 0
    };
  }
}

/**
 * Main execution
 */
async function main() {
  const args = process.argv.slice(2);

  const syncAll = args.includes('--all');
  const syncPostsFlag = args.includes('--posts');
  const syncLeadsFlag = args.includes('--leads');
  const syncPerformanceFlag = args.includes('--performance');
  const dryRun = args.includes('--dry-run');

  // Default to --all if no specific flags
  const runPosts = syncAll || syncPostsFlag || (!syncPostsFlag && !syncLeadsFlag && !syncPerformanceFlag);
  const runLeads = syncAll || syncLeadsFlag;
  const runPerformance = syncAll || syncPerformanceFlag;

  console.error('🔄 NOTION DASHBOARD SYNC');
  console.error('='.repeat(50));
  console.error(`Sync posts: ${runPosts}`);
  console.error(`Sync leads: ${runLeads}`);
  console.error(`Sync performance: ${runPerformance}`);
  console.error(`Dry run: ${dryRun}`);
  console.error('='.repeat(50));

  try {
    // Initialize clients
    const config = loadConfig();
    db = initializeFirebase(config.serviceAccount);
    notion = initializeNotion();

    const results = {
      posts: null,
      leads: null,
      performance: null
    };

    // Run syncs
    if (runPosts) {
      results.posts = await syncPosts(dryRun);
      console.error(`  Posts: ${results.posts.uploaded} uploaded, ${results.posts.skipped} skipped, ${results.posts.failed} failed`);
    }

    if (runLeads) {
      results.leads = await syncLeads(config.collection, config.clientId, dryRun);
      console.error(`  Leads: ${results.leads.uploaded} uploaded, ${results.leads.skipped} skipped, ${results.leads.failed} failed`);
    }

    if (runPerformance) {
      results.performance = await syncPerformance(config.collection, config.clientId, dryRun);
      console.error(`  Performance: ${results.performance.updated} updated`);
    }

    // Output results
    const output = {
      success: true,
      dry_run: dryRun,
      timestamp: new Date().toISOString(),
      synced: {}
    };

    if (results.posts) {
      output.synced.posts = {
        uploaded: results.posts.uploaded,
        skipped: results.posts.skipped,
        failed: results.posts.failed
      };
    }

    if (results.leads) {
      output.synced.leads = {
        uploaded: results.leads.uploaded,
        skipped: results.leads.skipped,
        failed: results.leads.failed
      };
    }

    if (results.performance) {
      output.synced.performance = {
        updated: results.performance.updated,
        failed: results.performance.failed || 0
      };
    }

    console.log(JSON.stringify(output, null, 2));
    process.exit(0);

  } catch (error) {
    console.error(JSON.stringify({
      success: false,
      error: error.message
    }));
    process.exit(1);
  }
}

main().catch(error => {
  console.error(JSON.stringify({
    success: false,
    error: error.message
  }));
  process.exit(1);
});
