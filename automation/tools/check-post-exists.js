#!/usr/bin/env node
/**
 * Check if a post exists in Firestore for a given brief ID.
 *
 * Queries the Firestore posts collection for documents where
 * `source_brief` matches the provided brief ID.
 *
 * Usage:
 *   node tools/check-post-exists.js "{brief_id}"
 *
 * Examples:
 *   node tools/check-post-exists.js "2026-01-12-building-in-public-is-scary-do-it-anyway-d1ea25"
 *
 * Output (JSON):
 *   {"exists": false}
 *   {"exists": true, "post_id": "...", "title": "...", "created_at": "..."}
 */

const { initializeApp, cert } = require('firebase-admin/app');
const { getFirestore } = require('firebase-admin/firestore');
const fs = require('fs');
const path = require('path');

// Project paths
const PROJECT_ROOT = path.dirname(__dirname);
const CONFIG_PATH = path.join(PROJECT_ROOT, 'config.md');

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

  // Parse Module Name (optional, defaults to 'linkedin-ghostwriter')
  match = content.match(/\*\*Module Name:\*\*\s*`([^`]+)`/);
  config.moduleName = match ? match[1] : 'linkedin-ghostwriter';

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
  initializeApp({ credential: cert(serviceAccount) });
  return getFirestore();
}

/**
 * Check if a post exists for the given brief ID
 * Path: {collection}/{clientId}/modules/{moduleName}/posts/
 */
async function checkPostExists(db, collection, clientId, moduleName, briefId) {
  const postsRef = db
    .collection(collection)
    .doc(clientId)
    .collection('modules')
    .doc(moduleName)
    .collection('posts');

  // Query for posts where source_brief matches the brief ID
  const snapshot = await postsRef
    .where('source_brief', '==', briefId)
    .limit(1)
    .get();

  if (snapshot.empty) {
    return { exists: false };
  }

  const doc = snapshot.docs[0];
  const data = doc.data();

  return {
    exists: true,
    post_id: doc.id,
    title: data.title || '',
    created_at: data.created_at || '',
    status: data.status || ''
  };
}

/**
 * Main function
 */
async function main() {
  const args = process.argv.slice(2);

  if (args.length === 0) {
    console.error('Usage: node tools/check-post-exists.js "{brief_id}"');
    console.error('');
    console.error('Example:');
    console.error('  node tools/check-post-exists.js "2026-01-12-building-in-public-d1ea25"');
    process.exit(1);
  }

  const briefId = args[0];

  // Load config and initialize Firebase
  const config = loadConfig();
  const db = initializeFirebase(config.serviceAccount);

  const result = await checkPostExists(db, config.collection, config.clientId, config.moduleName, briefId);

  // Output JSON result
  console.log(JSON.stringify(result, null, 2));

  // Exit with code 0 if no post exists, 1 if post exists (for scripting)
  process.exit(result.exists ? 1 : 0);
}

main().catch(err => {
  console.error(JSON.stringify({ error: err.message }));
  process.exit(2);
});
