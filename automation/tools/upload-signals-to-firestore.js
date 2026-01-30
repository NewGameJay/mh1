#!/usr/bin/env node

/**
 * Upload Signals to Firestore
 *
 * This script uploads signals directly to Firestore under {collection}/{clientId}/signals/
 * Signals are NOT persisted locally - they go directly to Firestore.
 *
 * Usage:
 *   CLI: node tools/upload-signals-to-firestore.js --json '{"type":"twitter-post","author":"user","content":"..."}'
 *   Module: const { uploadSignalData } = require('./tools/upload-signals-to-firestore.js');
 *
 * Signal Schema:
 *   {
 *     type: string,        // e.g., "twitter-post", "reddit-post", "linkedin-post", "web-sources-rss"
 *     author: string,      // Author name or handle
 *     title: string,       // Title or first 100 chars of content
 *     content: string,     // Full content body
 *     date_posted: string, // YYYY-MM-DD format
 *     url: string,         // Source URL (used for deduplication)
 *     status: string       // "unused" (default)
 *   }
 */

const admin = require('firebase-admin');
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

// Project paths
const PROJECT_ROOT = path.join(__dirname, '..');
const CONFIG_PATH = path.join(PROJECT_ROOT, 'config.md');

let db = null;
let initialized = false;

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
 * Initialize Firebase Admin SDK (singleton)
 */
function initializeFirebase(serviceAccountFile) {
  if (initialized) {
    return db;
  }

  const serviceAccountPath = path.join(PROJECT_ROOT, serviceAccountFile);
  if (!fs.existsSync(serviceAccountPath)) {
    throw new Error(`Service account file not found: ${serviceAccountPath}`);
  }

  const serviceAccount = require(serviceAccountPath);
  admin.initializeApp({
    credential: admin.credential.cert(serviceAccount)
  });

  initialized = true;
  return admin.firestore();
}

/**
 * Generate a UUID
 */
function generateUUID() {
  return crypto.randomUUID();
}

/**
 * Create a Firestore document from signal data object
 */
function createSignalDoc(signalData) {
  const today = new Date().toISOString().split('T')[0];

  // Extract title from content if not provided
  let title = signalData.title;
  if (!title && signalData.content) {
    const firstLine = signalData.content.split('\n')[0];
    title = firstLine.substring(0, 100);
  }

  const signalDoc = {
    id: generateUUID(),
    type: signalData.type || '',
    title: title || '',
    content: signalData.content || '',
    date_posted: signalData.date_posted || signalData['date-posted'] || '',
    date_added: signalData.date_added || signalData['date-added'] || today,
    url: signalData.url || '',
    author: signalData.author || signalData.source || '',
    status: signalData.status || 'unused',
    used_in_assignment_brief: signalData.used_in_assignment_brief || '',
    uploaded_at: admin.firestore.FieldValue.serverTimestamp()
  };

  return signalDoc;
}

/**
 * Check if a signal with the same URL already exists in Firestore
 */
async function checkDuplicateByUrl(collection, clientId, url) {
  if (!url) return null;

  const snapshot = await db
    .collection(collection)
    .doc(clientId)
    .collection('signals')
    .where('url', '==', url)
    .limit(1)
    .get();

  if (snapshot.empty) {
    return null;
  }

  const doc = snapshot.docs[0];
  return { id: doc.id, ...doc.data() };
}

/**
 * Upload a single signal to Firestore
 */
async function uploadSignal(collection, clientId, signalDoc) {
  const docRef = db
    .collection(collection)
    .doc(clientId)
    .collection('signals')
    .doc(signalDoc.id);

  await docRef.set(signalDoc);
  return signalDoc.id;
}

/**
 * Upload a signal data object directly to Firestore (no local file)
 * @param {Object} signalData - Signal data object with type, author, content, url, etc.
 * @returns {Object} - Result with id, status (uploaded/skipped/failed), and details
 */
async function uploadSignalData(signalData) {
  // Load config and initialize Firebase
  const config = loadConfig();
  const { collection, clientId } = config;
  db = initializeFirebase(config.serviceAccount);

  const signalDoc = createSignalDoc(signalData);

  // Check for duplicate by URL before uploading
  if (signalDoc.url) {
    const existing = await checkDuplicateByUrl(collection, clientId, signalDoc.url);
    if (existing) {
      return {
        status: 'skipped',
        reason: 'duplicate',
        url: signalDoc.url,
        existingId: existing.id
      };
    }
  }

  await uploadSignal(collection, clientId, signalDoc);

  return {
    status: 'uploaded',
    id: signalDoc.id,
    type: signalDoc.type,
    author: signalDoc.author,
    url: signalDoc.url
  };
}

/**
 * Bulk upload multiple signals to Firestore
 * @param {Array} signalsArray - Array of signal data objects
 * @returns {Object} - Results summary with success, skipped, failed arrays
 */
async function uploadSignalsBatch(signalsArray) {
  const results = {
    success: [],
    skipped: [],
    failed: []
  };

  for (const signalData of signalsArray) {
    try {
      const result = await uploadSignalData(signalData);
      if (result.status === 'uploaded') {
        results.success.push(result);
      } else if (result.status === 'skipped') {
        results.skipped.push(result);
      }
    } catch (error) {
      results.failed.push({
        url: signalData.url,
        error: error.message
      });
    }
  }

  return results;
}

/**
 * Main CLI execution
 */
async function main() {
  const args = process.argv.slice(2);

  // Check for --json flag for direct signal upload
  if (args.includes('--json')) {
    const jsonIndex = args.indexOf('--json');
    const jsonStr = args[jsonIndex + 1];

    if (!jsonStr) {
      console.error('Error: --json requires a JSON string argument');
      process.exit(1);
    }

    try {
      const signalData = JSON.parse(jsonStr);
      const result = await uploadSignalData(signalData);

      if (result.status === 'uploaded') {
        console.log(`✅ Uploaded: ${result.id} (${result.type})`);
      } else if (result.status === 'skipped') {
        console.log(`⏭️  Skipped: duplicate URL exists (${result.existingId})`);
      }

      // Output JSON for programmatic use
      console.log(JSON.stringify(result));
      process.exit(0);
    } catch (error) {
      console.error(`❌ Failed: ${error.message}`);
      process.exit(1);
    }
  }

  // Check for --batch flag for bulk upload from JSON file
  if (args.includes('--batch')) {
    const batchIndex = args.indexOf('--batch');
    const filePath = args[batchIndex + 1];

    if (!filePath) {
      console.error('Error: --batch requires a JSON file path');
      process.exit(1);
    }

    const fullPath = path.isAbsolute(filePath) ? filePath : path.join(PROJECT_ROOT, filePath);
    if (!fs.existsSync(fullPath)) {
      console.error(`Error: File not found: ${fullPath}`);
      process.exit(1);
    }

    try {
      const signalsArray = JSON.parse(fs.readFileSync(fullPath, 'utf-8'));
      console.log(`📂 Processing ${signalsArray.length} signals from ${path.basename(filePath)}\n`);

      const results = await uploadSignalsBatch(signalsArray);

      console.log('\n--- Summary ---');
      console.log(`✅ Uploaded: ${results.success.length}`);
      console.log(`⏭️  Skipped (duplicates): ${results.skipped.length}`);
      console.log(`❌ Failed: ${results.failed.length}`);

      const config = loadConfig();
      console.log(`\n📍 Firestore path: ${config.collection}/${config.clientId}/signals/`);

      process.exit(results.failed.length > 0 ? 1 : 0);
    } catch (error) {
      console.error(`❌ Failed: ${error.message}`);
      process.exit(1);
    }
  }

  // Default: show usage
  console.log('Usage:');
  console.log('  Upload single signal:  node tools/upload-signals-to-firestore.js --json \'{"type":"...", "content":"..."}\'');
  console.log('  Upload batch:          node tools/upload-signals-to-firestore.js --batch signals.json');
  console.log('');
  console.log('Signal Schema:');
  console.log('  {');
  console.log('    type: string,        // "twitter-post", "reddit-post", "linkedin-post", "linkedin-keyword", "web-sources-rss"');
  console.log('    author: string,      // Author name or handle');
  console.log('    title: string,       // Title (optional, extracted from content if not provided)');
  console.log('    content: string,     // Full content body');
  console.log('    date_posted: string, // YYYY-MM-DD format');
  console.log('    url: string,         // Source URL (used for deduplication)');
  console.log('    status: string       // "unused" (default)');
  console.log('  }');
  process.exit(0);
}

// Export functions for programmatic use
module.exports = {
  uploadSignalData,
  uploadSignalsBatch,
  createSignalDoc,
  checkDuplicateByUrl
};

// Run main if executed directly
if (require.main === module) {
  main().catch(error => {
    console.error('Fatal error:', error);
    process.exit(1);
  });
}
