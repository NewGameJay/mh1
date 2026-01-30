#!/usr/bin/env node

/**
 * Upload Context Files to Firebase Storage
 *
 * This script reads markdown files from the local context/ directory
 * and uploads/updates them to Firebase Storage: clients/{clientName}/{relativePath}
 *
 * Usage:
 *   node scripts/upload-context-to-firestore.js                    # Upload all context files
 *   node scripts/upload-context-to-firestore.js founder-info       # Upload only founder-info folder
 *   node scripts/upload-context-to-firestore.js writing-analysis   # Upload only writing-analysis folder
 *   node scripts/upload-context-to-firestore.js founder-info writing-analysis  # Upload multiple folders
 */

const admin = require('firebase-admin');
const fs = require('fs');
const path = require('path');

// Project paths
const PROJECT_ROOT = path.join(__dirname, '..');
const CONFIG_PATH = path.join(PROJECT_ROOT, 'config.md');
const CONTEXT_DIR = path.join(PROJECT_ROOT, 'context');

// Parse command line arguments for specific folders
const targetFolders = process.argv.slice(2);

let db = null;
let bucket = null;

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
  if (match) config.serviceAccount = match[1];

  // Parse Collection
  match = content.match(/\*\*Collection:\*\*\s*`([^`]+)`/);
  if (match) config.collection = match[1];

  // Parse Client ID
  match = content.match(/\*\*Client ID:\*\*\s*`([^`]+)`/);
  if (match) config.clientId = match[1];

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
    credential: admin.credential.cert(serviceAccount),
    storageBucket: `${serviceAccount.project_id}.firebasestorage.app`
  });

  return {
    db: admin.firestore(),
    bucket: admin.storage().bucket()
  };
}

/**
 * Get client name from Firestore
 */
async function getClientName(collection, clientId) {
  const doc = await db.collection(collection).doc(clientId).get();
  if (!doc.exists) {
    throw new Error(`Client document not found: ${collection}/${clientId}`);
  }
  const data = doc.data();
  if (!data.name) {
    throw new Error(`Client document missing 'name' field: ${collection}/${clientId}`);
  }
  return data.name;
}

/**
 * Recursively get all markdown files from a directory
 */
function getMarkdownFiles(dir, baseDir = dir) {
  const files = [];
  const entries = fs.readdirSync(dir, { withFileTypes: true });

  for (const entry of entries) {
    const fullPath = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      files.push(...getMarkdownFiles(fullPath, baseDir));
    } else if (entry.name.endsWith('.md')) {
      const relativePath = path.relative(baseDir, fullPath);
      files.push({ fullPath, relativePath });
    }
  }

  return files;
}

/**
 * Categorize the file based on its path
 */
function categorizeFile(relativePath) {
  if (relativePath.startsWith('founder-info/')) return 'founder-info';
  if (relativePath.startsWith('writing-analysis/')) return 'writing-analysis';
  return 'general';
}

/**
 * Upload a single context file to Storage
 */
async function uploadContextFile(file, clientName) {
  const { fullPath, relativePath } = file;
  const content = fs.readFileSync(fullPath, 'utf-8');
  const category = categorizeFile(relativePath);

  // Upload to Storage
  const storagePath = `clients/${clientName}/${relativePath}`;
  const storageFile = bucket.file(storagePath);
  await storageFile.save(content, {
    metadata: {
      contentType: 'text/markdown',
      metadata: {
        category,
        uploadedAt: new Date().toISOString()
      }
    }
  });

  return { relativePath, contentLength: content.length, storagePath };
}

/**
 * Filter files based on target folders
 */
function filterFilesByFolders(files, folders) {
  if (folders.length === 0) return files;

  return files.filter(file => {
    return folders.some(folder => file.relativePath.startsWith(folder + '/'));
  });
}

/**
 * Main execution
 */
async function main() {
  // Load config
  const config = loadConfig();
  const { collection, clientId } = config;

  console.log('============================================');
  console.log('FIREBASE STORAGE CONTEXT UPLOAD');
  console.log('============================================\n');

  console.log(`Config loaded from: ${path.basename(CONFIG_PATH)}`);
  console.log(`  Collection: ${collection}`);
  console.log(`  Client ID: ${clientId}`);

  if (targetFolders.length > 0) {
    console.log(`  Target folders: ${targetFolders.join(', ')}`);
  } else {
    console.log(`  Target folders: all`);
  }
  console.log('');

  // Initialize Firebase
  const firebase = initializeFirebase(config.serviceAccount);
  db = firebase.db;
  bucket = firebase.bucket;

  // Get client name for Storage path
  const clientName = await getClientName(collection, clientId);
  console.log(`  Client name: ${clientName}`);
  console.log(`  Storage path: clients/${clientName}/\n`);

  console.log('Scanning context directory:', CONTEXT_DIR);

  if (!fs.existsSync(CONTEXT_DIR)) {
    console.error('Context directory not found:', CONTEXT_DIR);
    process.exit(1);
  }

  let files = getMarkdownFiles(CONTEXT_DIR);

  // Filter by target folders if specified
  if (targetFolders.length > 0) {
    files = filterFilesByFolders(files, targetFolders);
    console.log(`Found ${files.length} markdown files in specified folders\n`);
  } else {
    console.log(`Found ${files.length} markdown files\n`);
  }

  const results = {
    success: [],
    failed: []
  };

  for (const file of files) {
    try {
      const result = await uploadContextFile(file, clientName);
      results.success.push(result);
      console.log(`Uploaded: ${result.relativePath} (${result.contentLength} chars)`);
    } catch (error) {
      results.failed.push({ relativePath: file.relativePath, error: error.message });
      console.error(`Failed: ${file.relativePath} - ${error.message}`);
    }
  }

  console.log('\n--- Summary ---');
  console.log(`Successfully uploaded: ${results.success.length}`);
  console.log(`Failed: ${results.failed.length}`);

  if (results.failed.length > 0) {
    console.log('\nFailed files:');
    results.failed.forEach(f => console.log(`  - ${f.relativePath}: ${f.error}`));
  }

  const totalChars = results.success.reduce((sum, r) => sum + r.contentLength, 0);
  console.log(`\nTotal content uploaded: ${totalChars.toLocaleString()} characters`);
  console.log(`Storage path: clients/${clientName}/`);

  process.exit(results.failed.length > 0 ? 1 : 0);
}

main().catch(error => {
  console.error('Fatal error:', error);
  process.exit(1);
});
