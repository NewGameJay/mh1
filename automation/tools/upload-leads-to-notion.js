#!/usr/bin/env node

/**
 * Upload Qualified Leads to Notion Database
 *
 * This script uploads qualified leads to a Notion Leads database.
 * The database ID is retrieved from Firebase (clients/{clientId}/modules/leads-database.notionDatabaseId).
 *
 * Usage:
 *     node tools/upload-leads-to-notion.js --file leads.json
 *     node tools/upload-leads-to-notion.js --stdin < leads.json
 *     node tools/upload-leads-to-notion.js --dry-run --file leads.json
 *
 * Input JSON Schema:
 *     [
 *       {
 *         "name": "John Doe",
 *         "company": "Acme Corp",
 *         "role": "VP of Marketing",
 *         "linkedin_url": "https://linkedin.com/in/johndoe",
 *         "icp_type": "Primary",
 *         "rationale": "High-intent signal from LinkedIn post",
 *         "draft_msg": "Hi John, I noticed your post about...",
 *         "source_signal": "https://linkedin.com/posts/...",
 *         "score": 85
 *       }
 *     ]
 *
 * Environment:
 *     NOTION_API_TOKEN - Notion integration token (from .env)
 *
 * Output (JSON):
 *     {"success": true, "uploaded": [...], "failed": [...]}
 *     {"success": false, "error": "..."}
 */

require('dotenv').config();
const { Client } = require('@notionhq/client');
const admin = require('firebase-admin');
const fs = require('fs');
const path = require('path');

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
 * Get Notion database ID from Firebase
 * Path: clients/{clientId}/modules/leads-database
 */
async function getNotionDatabaseId(collection, clientId) {
  const docRef = db.collection(collection).doc(clientId).collection('modules').doc('leads-database');
  const doc = await docRef.get();

  if (!doc.exists) {
    throw new Error(`Module document not found: ${collection}/${clientId}/modules/leads-database`);
  }

  const data = doc.data();
  const databaseId = data.notionDatabaseId;

  if (!databaseId) {
    throw new Error(`notionDatabaseId not found in ${collection}/${clientId}/modules/leads-database`);
  }

  return databaseId;
}

/**
 * Build Notion page properties from lead data
 * Maps to Notion Leads database schema
 */
function buildNotionProperties(lead) {
  const properties = {};

  // Name (Title) - Required title property
  if (lead.name) {
    properties['Name'] = {
      title: [{ text: { content: lead.name } }]
    };
  }

  // Company (Rich Text)
  if (lead.company) {
    properties['Company'] = {
      rich_text: [{ text: { content: lead.company } }]
    };
  }

  // Role (Rich Text)
  if (lead.role) {
    properties['Role'] = {
      rich_text: [{ text: { content: lead.role } }]
    };
  }

  // LinkedIn URL (URL)
  if (lead.linkedin_url) {
    properties['LinkedIn URL'] = {
      url: lead.linkedin_url
    };
  }

  // ICP Type (Select)
  if (lead.icp_type) {
    properties['ICP Type'] = {
      select: { name: lead.icp_type }
    };
  }

  // Rationale (Rich Text)
  if (lead.rationale) {
    properties['Rationale'] = {
      rich_text: [{ text: { content: lead.rationale.substring(0, 2000) } }]
    };
  }

  // Draft Message (Rich Text)
  if (lead.draft_msg) {
    properties['Draft Message'] = {
      rich_text: [{ text: { content: lead.draft_msg.substring(0, 2000) } }]
    };
  }

  // Source Signal (URL)
  if (lead.source_signal) {
    properties['Source Signal'] = {
      url: lead.source_signal
    };
  }

  // Score (Number)
  if (typeof lead.score === 'number') {
    properties['Score'] = {
      number: lead.score
    };
  }

  // Status (Status) - Default to "New"
  properties['Status'] = {
    status: { name: lead.status || 'New' }
  };

  // Added At (Date)
  properties['Added At'] = {
    date: { start: new Date().toISOString() }
  };

  // Email (Email) - if provided
  if (lead.email) {
    properties['Email'] = {
      email: lead.email
    };
  }

  // Location (Rich Text)
  if (lead.location) {
    properties['Location'] = {
      rich_text: [{ text: { content: lead.location } }]
    };
  }

  // Headline (Rich Text)
  if (lead.headline) {
    properties['Headline'] = {
      rich_text: [{ text: { content: lead.headline.substring(0, 2000) } }]
    };
  }

  // Followers (Number)
  if (typeof lead.followers === 'number') {
    properties['Followers'] = {
      number: lead.followers
    };
  }

  return properties;
}

/**
 * Check if a lead already exists in Notion by LinkedIn URL
 */
async function leadExistsInNotion(databaseId, linkedinUrl) {
  if (!linkedinUrl) return false;

  try {
    const response = await notion.databases.query({
      database_id: databaseId,
      filter: {
        property: 'LinkedIn URL',
        url: {
          equals: linkedinUrl
        }
      }
    });
    return response.results.length > 0;
  } catch (error) {
    return false;
  }
}

/**
 * Upload a single lead to Notion
 */
async function uploadLeadToNotion(databaseId, lead, dryRun = false) {
  const linkedinUrl = lead.linkedin_url || lead.linkedinUrl;

  // Check if already exists (by LinkedIn URL)
  if (linkedinUrl) {
    const exists = await leadExistsInNotion(databaseId, linkedinUrl);
    if (exists) {
      return {
        success: true,
        skipped: true,
        name: lead.name,
        reason: 'Already exists in Notion'
      };
    }
  }

  if (dryRun) {
    return {
      success: true,
      dry_run: true,
      name: lead.name,
      company: lead.company,
      properties: Object.keys(buildNotionProperties(lead))
    };
  }

  // Build properties
  const properties = buildNotionProperties(lead);

  // Create page in Notion
  const response = await notion.pages.create({
    parent: { database_id: databaseId },
    properties: properties
  });

  return {
    success: true,
    name: lead.name,
    company: lead.company,
    notion_page_id: response.id,
    notion_url: response.url
  };
}

/**
 * Read leads from stdin
 */
async function readFromStdin() {
  return new Promise((resolve, reject) => {
    let data = '';
    process.stdin.setEncoding('utf8');

    process.stdin.on('readable', () => {
      let chunk;
      while ((chunk = process.stdin.read()) !== null) {
        data += chunk;
      }
    });

    process.stdin.on('end', () => {
      try {
        resolve(JSON.parse(data));
      } catch (e) {
        reject(new Error(`Invalid JSON from stdin: ${e.message}`));
      }
    });

    process.stdin.on('error', reject);
  });
}

/**
 * Main execution
 */
async function main() {
  const args = process.argv.slice(2);

  const useStdin = args.includes('--stdin');
  const dryRun = args.includes('--dry-run');
  const fileIdx = args.indexOf('--file');
  const filePath = fileIdx >= 0 && args[fileIdx + 1] ? args[fileIdx + 1] : null;

  if (!useStdin && !filePath) {
    console.error(JSON.stringify({
      success: false,
      error: 'Usage: node tools/upload-leads-to-notion.js --file leads.json OR --stdin [--dry-run]'
    }));
    process.exit(1);
  }

  try {
    // Load leads
    let leads;
    if (useStdin) {
      leads = await readFromStdin();
    } else {
      const resolvedPath = path.isAbsolute(filePath) ? filePath : path.join(PROJECT_ROOT, filePath);
      if (!fs.existsSync(resolvedPath)) {
        throw new Error(`Leads file not found: ${resolvedPath}`);
      }
      leads = JSON.parse(fs.readFileSync(resolvedPath, 'utf-8'));
    }

    // Ensure leads is an array
    if (!Array.isArray(leads)) {
      leads = [leads];
    }

    if (leads.length === 0) {
      console.log(JSON.stringify({
        success: true,
        message: 'No leads to upload',
        uploaded: [],
        failed: []
      }));
      process.exit(0);
    }

    // Initialize clients
    const config = loadConfig();
    db = initializeFirebase(config.serviceAccount);
    notion = initializeNotion();

    // Get Notion database ID from Firebase
    const databaseId = await getNotionDatabaseId(config.collection, config.clientId);

    // Upload each lead
    const results = {
      uploaded: [],
      skipped: [],
      failed: []
    };

    for (const lead of leads) {
      try {
        const result = await uploadLeadToNotion(databaseId, lead, dryRun);

        if (result.skipped) {
          results.skipped.push(result);
        } else {
          results.uploaded.push(result);
        }
      } catch (error) {
        results.failed.push({
          name: lead.name,
          company: lead.company,
          error: error.message
        });
      }
    }

    // Output results
    console.log(JSON.stringify({
      success: true,
      dry_run: dryRun,
      database_id: databaseId,
      total_leads: leads.length,
      uploaded: results.uploaded,
      skipped: results.skipped,
      failed: results.failed
    }, null, 2));

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
