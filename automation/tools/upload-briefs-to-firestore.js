#!/usr/bin/env node

/**
 * Upload Assignment Briefs to Firestore
 *
 * This script reads markdown files from the assignment-briefs/ directory
 * and uploads them to Firestore under:
 *   test-clients/{clientId}/modules/linkedin-ghostwriter/assignment-briefs/{briefId}
 *
 * The assignment-briefs collection contains:
 *   - Individual brief documents (by UUID)
 *   - An _index document with the full briefs index
 *
 * Usage:
 *     node tools/upload-briefs-to-firestore.js                          # Upload all briefs
 *     node tools/upload-briefs-to-firestore.js --files file1.md file2.md  # Upload specific files
 */

const admin = require('firebase-admin');
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

// Paths
const SCRIPT_DIR = __dirname;
const PROJECT_ROOT = path.join(SCRIPT_DIR, '..');
const CONFIG_PATH = path.join(PROJECT_ROOT, 'config.md');
const BRIEFS_DIR = path.join(PROJECT_ROOT, 'assignment-briefs');

let db = null;

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

  // Parse Module Name (optional, defaults to 'linkedin-ghostwriter')
  match = content.match(/\*\*Module Name:\*\*\s*`([^`]+)`/);
  config.moduleName = match ? match[1] : 'linkedin-ghostwriter';

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
 * Parse YAML-like frontmatter from markdown content
 */
function parseFrontmatter(content) {
  const pattern = /^---\n([\s\S]*?)\n---\n([\s\S]*)$/;
  const match = content.match(pattern);

  if (!match) {
    return { metadata: {}, body: content };
  }

  const frontmatter = match[1];
  const body = match[2].trim();
  const metadata = {};

  let currentKey = null;
  let currentValue = [];
  let inArray = false;

  const lines = frontmatter.split('\n');
  for (const line of lines) {
    const stripped = line.trim();

    // Check if this is an array item
    if (stripped.startsWith('- ') && inArray) {
      let value = stripped.slice(2).trim();
      // Remove quotes
      if ((value.startsWith('"') && value.endsWith('"')) ||
          (value.startsWith("'") && value.endsWith("'"))) {
        value = value.slice(1, -1);
      }
      currentValue.push(value);
      continue;
    }

    // Check for new key
    const colonIdx = line.indexOf(':');
    if (colonIdx > 0 && !stripped.startsWith('-')) {
      // Save previous key if exists
      if (currentKey && inArray) {
        metadata[currentKey] = currentValue;
      }

      const key = line.slice(0, colonIdx).trim();
      let value = line.slice(colonIdx + 1).trim();

      // Check if value is an inline array
      if (value.startsWith('[') && value.endsWith(']')) {
        try {
          metadata[key] = JSON.parse(value);
        } catch (e) {
          // Parse manually
          const inner = value.slice(1, -1);
          const items = [];
          for (let item of inner.split(',')) {
            item = item.trim();
            if ((item.startsWith('"') && item.endsWith('"')) ||
                (item.startsWith("'") && item.endsWith("'"))) {
              item = item.slice(1, -1);
            }
            if (item) {
              items.push(item);
            }
          }
          metadata[key] = items;
        }
        currentKey = null;
        inArray = false;
      } else if (value === '' || value === '[]') {
        // Multi-line array starting
        currentKey = key;
        currentValue = [];
        inArray = true;
      } else {
        // Regular value
        if ((value.startsWith('"') && value.endsWith('"')) ||
            (value.startsWith("'") && value.endsWith("'"))) {
          value = value.slice(1, -1);
        }
        metadata[key] = value;
        currentKey = null;
        inArray = false;
      }
    }
  }

  // Save last key if exists
  if (currentKey && inArray) {
    metadata[currentKey] = currentValue;
  }

  return { metadata, body };
}

/**
 * Extract title from body content (first H1)
 */
function extractTitleFromBody(body) {
  for (const line of body.split('\n')) {
    if (line.startsWith('# ')) {
      return line.slice(2).trim();
    }
  }
  return 'Untitled Brief';
}

/**
 * Map status to valid schema status
 */
function mapStatus(fileStatus) {
  const validStatuses = ['draft', 'used'];
  if (validStatuses.includes(fileStatus)) {
    return fileStatus;
  }
  return 'draft';
}

/**
 * Normalize target persona to single value
 */
function normalizeTargetPersona(targetPersonas) {
  if (Array.isArray(targetPersonas) && targetPersonas.length > 0) {
    return targetPersonas[0];
  }
  if (typeof targetPersonas === 'string') {
    return targetPersonas;
  }
  return '';
}

/**
 * Process a single brief file and return document data
 * Schema:
 *   id: string (from frontmatter, or generate UUID if missing)
 *   title: string
 *   status: "draft" | "used"
 *   founder: string
 *   content_pillar: string (pillar ID)
 *   funnel_stage: "TOFU" | "MOFU" | "BOFU"
 *   signals: string[] (signal URLs)
 *   pov: string
 *   target_persona: string (persona ID)
 *   created_at: timestamp
 *   content: string (markdown body)
 */
function processBriefFile(filePath) {
  const content = fs.readFileSync(filePath, 'utf-8');
  const { metadata, body } = parseFrontmatter(content);
  const stats = fs.statSync(filePath);

  // Use the ID from frontmatter, or generate a new UUID if not present
  const briefId = metadata.id || crypto.randomUUID();

  // Generate document data matching exact schema
  const briefDoc = {
    id: briefId,
    title: metadata.title || extractTitleFromBody(body),
    status: mapStatus(metadata.status || 'draft'),
    founder: metadata.founder || '',
    content_pillar: metadata.content_pillar || '',
    funnel_stage: metadata.funnel_stage || 'TOFU',
    signals: metadata.signals || [],
    pov: metadata.pov || '',
    target_persona: metadata.target_persona || normalizeTargetPersona(metadata.target_personas) || '',
    created_at: stats.birthtime.toISOString(),
    content: body
  };

  return briefDoc;
}

/**
 * Upload a single brief to Firestore
 */
async function uploadBrief(collection, clientId, moduleName, briefDoc) {
  // Path: {collection}/{clientId}/modules/{moduleName}/assignment-briefs/{briefId}
  const briefsRef = db
    .collection(collection)
    .doc(clientId)
    .collection('modules')
    .doc(moduleName)
    .collection('assignment-briefs');

  const docRef = briefsRef.doc(briefDoc.id);
  await docRef.set(briefDoc);

  return briefDoc.id;
}

/**
 * Fetch all existing briefs from Firestore (excluding _index)
 */
async function fetchExistingBriefs(collection, clientId, moduleName) {
  const briefsRef = db
    .collection(collection)
    .doc(clientId)
    .collection('modules')
    .doc(moduleName)
    .collection('assignment-briefs');

  const snapshot = await briefsRef.get();
  const briefs = [];

  snapshot.forEach(doc => {
    // Skip the _index document
    if (doc.id !== '_index') {
      const data = doc.data();
      briefs.push({
        id: data.id || doc.id,
        title: data.title || '',
        status: data.status || 'draft',
        founder: data.founder || '',
        content_pillar: data.content_pillar || '',
        funnel_stage: data.funnel_stage || 'TOFU',
        signals: data.signals || [],
        pov: data.pov || '',
        target_persona: data.target_persona || '',
        created_at: data.created_at || ''
      });
    }
  });

  return briefs;
}

/**
 * Upload the briefs index to Firestore
 * Merges newly uploaded briefs with existing briefs in Firestore
 */
async function uploadIndex(collection, clientId, moduleName, newBriefsData) {
  // Fetch all existing briefs from Firestore
  const existingBriefs = await fetchExistingBriefs(collection, clientId, moduleName);

  // Create a map of existing briefs by ID for easy lookup
  const briefsMap = new Map();

  // Add existing briefs to map
  for (const brief of existingBriefs) {
    briefsMap.set(brief.id, brief);
  }

  // Add/update with newly uploaded briefs (these take precedence)
  for (const brief of newBriefsData) {
    briefsMap.set(brief.id, brief);
  }

  // Convert map back to array and sort by created_at descending
  const mergedIndex = Array.from(briefsMap.values()).sort((a, b) => {
    return (b.created_at || '').localeCompare(a.created_at || '');
  });

  // Path: test-clients/{clientId}/modules/linkedin-ghostwriter/assignment-briefs/_index
  const indexRef = db
    .collection(collection)
    .doc(clientId)
    .collection('modules')
    .doc(moduleName)
    .collection('assignment-briefs')
    .doc('_index');

  await indexRef.set({
    briefs: mergedIndex,
    count: mergedIndex.length,
    updated_at: admin.firestore.FieldValue.serverTimestamp()
  });

  console.log(`   - Existing briefs in Firestore: ${existingBriefs.length}`);
  console.log(`   - New/updated briefs: ${newBriefsData.length}`);
  console.log(`   - Total briefs in index: ${mergedIndex.length}`);

  return '_index';
}

/**
 * Get all markdown files from briefs directory
 */
function getBriefFiles() {
  if (!fs.existsSync(BRIEFS_DIR)) {
    return [];
  }

  return fs.readdirSync(BRIEFS_DIR)
    .filter(f => f.endsWith('.md'))
    .map(f => path.join(BRIEFS_DIR, f))
    .sort();
}

/**
 * Parse command line arguments
 */
function parseArgs() {
  const args = process.argv.slice(2);
  const result = {
    files: []
  };

  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--files') {
      // Collect all following arguments until next flag or end
      i++;
      while (i < args.length && !args[i].startsWith('--')) {
        result.files.push(args[i]);
        i++;
      }
      i--; // Back up one since the loop will increment
    }
  }

  return result;
}

/**
 * Main execution
 */
async function main() {
  const args = parseArgs();

  console.log('============================================');
  console.log('FIREBASE ASSIGNMENT BRIEFS UPLOAD');
  console.log('============================================\n');

  // Load config
  const config = loadConfig();
  const { collection, clientId, moduleName } = config;

  console.log(`Config loaded from: ${path.basename(CONFIG_PATH)}`);
  console.log(`  Collection: ${collection}`);
  console.log(`  Client ID: ${clientId}`);
  console.log(`  Module: ${moduleName}\n`);

  // Determine files to process
  let filesToProcess = [];
  if (args.files.length > 0) {
    filesToProcess = args.files.map(f => {
      if (path.isAbsolute(f)) return f;
      if (f.startsWith('assignment-briefs/')) return path.join(PROJECT_ROOT, f);
      return path.join(BRIEFS_DIR, f);
    });
  } else {
    filesToProcess = getBriefFiles();
  }

  console.log(`📂 Found ${filesToProcess.length} brief files to process\n`);

  if (filesToProcess.length === 0) {
    console.log('No files to process.');
    process.exit(0);
  }

  // Initialize Firebase
  db = initializeFirebase(config.serviceAccount);

  const processedBriefs = [];
  const results = {
    success: [],
    failed: []
  };

  // Process all files
  for (const filePath of filesToProcess) {
    const fileName = path.basename(filePath);

    if (!fs.existsSync(filePath)) {
      results.failed.push({ fileName, error: 'File not found' });
      console.error(`❌ Not found: ${fileName}`);
      continue;
    }

    try {
      const briefDoc = processBriefFile(filePath);
      processedBriefs.push(briefDoc);

      await uploadBrief(collection, clientId, moduleName, briefDoc);
      results.success.push({
        fileName,
        id: briefDoc.id,
        title: briefDoc.title,
        status: briefDoc.status,
        funnel_stage: briefDoc.funnel_stage
      });
      console.log(`✅ Uploaded: ${fileName} (${briefDoc.funnel_stage}, ${briefDoc.status})`);

    } catch (error) {
      results.failed.push({ fileName, error: error.message });
      console.error(`❌ Failed: ${fileName} - ${error.message}`);
    }
  }

  // Upload merged index to Firestore
  const indexData = processedBriefs.map(doc => ({
    id: doc.id,
    title: doc.title,
    status: doc.status,
    founder: doc.founder,
    content_pillar: doc.content_pillar,
    funnel_stage: doc.funnel_stage,
    signals: doc.signals,
    pov: doc.pov,
    target_persona: doc.target_persona,
    created_at: doc.created_at
  }));
  await uploadIndex(collection, clientId, moduleName, indexData);
  console.log('\n📝 Uploaded merged index to Firestore: _index');

  // Summary
  console.log('\n============================================');
  console.log('SUMMARY');
  console.log('============================================');
  console.log(`✅ Successfully processed: ${results.success.length}`);
  console.log(`❌ Failed: ${results.failed.length}`);

  if (results.failed.length > 0) {
    console.log('\nFailed files:');
    results.failed.forEach(f => console.log(`  - ${f.fileName}: ${f.error}`));
  }

  // Stats breakdown by funnel stage
  const tofuCount = results.success.filter(r => r.funnel_stage === 'TOFU').length;
  const mofuCount = results.success.filter(r => r.funnel_stage === 'MOFU').length;
  const bofuCount = results.success.filter(r => r.funnel_stage === 'BOFU').length;

  console.log('\n📊 Funnel stage breakdown:');
  console.log(`   - TOFU: ${tofuCount}`);
  console.log(`   - MOFU: ${mofuCount}`);
  console.log(`   - BOFU: ${bofuCount}`);

  // Stats breakdown by status
  const draftCount = results.success.filter(r => r.status === 'draft').length;
  const usedCount = results.success.filter(r => r.status === 'used').length;

  console.log('\n📊 Status breakdown:');
  console.log(`   - Draft: ${draftCount}`);
  console.log(`   - Used: ${usedCount}`);

  console.log(`\n📍 Firestore path: ${collection}/${clientId}/modules/${moduleName}/assignment-briefs/`);

  console.log('============================================');

  process.exit(results.failed.length > 0 ? 1 : 0);
}

main().catch(error => {
  console.error('Fatal error:', error);
  process.exit(1);
});
