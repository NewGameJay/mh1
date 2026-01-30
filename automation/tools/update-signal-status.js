#!/usr/bin/env node
/**
 * Update signal status in Firestore.
 *
 * Usage:
 *   node tools/update-signal-status.js <signal-url-or-id> --status unused|used|rejected
 *
 * The script accepts either:
 *   - A signal URL (e.g., "https://www.elenaverna.com/p/some-article")
 *   - A signal ID (e.g., "abc123-def456")
 *
 * It will search Firestore by URL first, then by ID as fallback.
 *
 * Examples:
 *   node tools/update-signal-status.js "https://www.elenaverna.com/p/some-article" --status rejected
 *   node tools/update-signal-status.js "abc123-def456" --status rejected
 *   node tools/update-signal-status.js "https://example.com/post" --status used --brief-id "2025-12-27-ab-001"
 */

const { initializeApp, cert, getApps } = require('firebase-admin/app');
const { getFirestore } = require('firebase-admin/firestore');
const fs = require('fs');
const path = require('path');

// Project paths
const PROJECT_ROOT = path.dirname(__dirname);
const CONFIG_PATH = path.join(PROJECT_ROOT, 'config.md');

const VALID_STATUSES = ['unused', 'used', 'rejected'];

/**
 * Load configuration from config.md
 */
function loadConfig() {
  if (!fs.existsSync(CONFIG_PATH)) {
    throw new Error(`Config file not found: ${CONFIG_PATH}`);
  }

  const content = fs.readFileSync(CONFIG_PATH, 'utf-8');
  const config = {};

  let match = content.match(/\*\*Service Account:\*\*\s*`([^`]+)`/);
  if (match) config.serviceAccount = match[1];

  match = content.match(/\*\*Collection:\*\*\s*`([^`]+)`/);
  if (match) config.collection = match[1];

  match = content.match(/\*\*Client ID:\*\*\s*`([^`]+)`/);
  if (match) config.clientId = match[1];

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
  // Check if already initialized
  if (getApps().length > 0) {
    return getFirestore();
  }

  const serviceAccountPath = path.join(PROJECT_ROOT, serviceAccountFile);
  if (!fs.existsSync(serviceAccountPath)) {
    throw new Error(`Service account file not found: ${serviceAccountPath}`);
  }

  const serviceAccount = require(serviceAccountPath);
  initializeApp({ credential: cert(serviceAccount) });
  return getFirestore();
}

/**
 * Update signal status in Firestore
 */
async function updateFirestoreStatus(db, collection, clientId, signalId, status, briefId = null) {
  const signalsRef = db.collection(collection).doc(clientId).collection('signals');

  // Try to find document by URL field first (since local files use URL as ID)
  let snapshot = await signalsRef.where('url', '==', signalId).get();

  if (snapshot.empty) {
    // Try by id field as fallback
    snapshot = await signalsRef.where('id', '==', signalId).get();
  }

  if (snapshot.empty) {
    console.error(`Warning: Signal not found in Firestore: ${signalId}`);
    return false;
  }

  // Update the document (use first match only)
  const doc = snapshot.docs[0];
  const updateData = { status };
  if (briefId) {
    updateData.used_in_assignment_brief = briefId;
  }

  await signalsRef.doc(doc.id).update(updateData);
  return true;
}

/**
 * Parse command line arguments
 */
function parseArgs() {
  const args = process.argv.slice(2);
  const options = {
    signalId: null,
    status: null,
    briefId: null
  };

  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--status' || args[i] === '-s') {
      options.status = args[i + 1];
      i++;
    } else if (args[i] === '--brief-id' || args[i] === '-b') {
      options.briefId = args[i + 1];
      i++;
    } else if (!args[i].startsWith('-')) {
      options.signalId = args[i];
    }
  }

  return options;
}

/**
 * Main function
 */
async function main() {
  const options = parseArgs();

  // Validate arguments
  if (!options.signalId) {
    console.error('Error: Signal ID is required');
    console.error('Usage: node tools/update-signal-status.js <signal-id> --status unused|used|rejected');
    process.exit(1);
  }

  if (!options.status) {
    console.error('Error: --status is required');
    process.exit(1);
  }

  if (!VALID_STATUSES.includes(options.status)) {
    console.error(`Error: Invalid status. Must be one of: ${VALID_STATUSES.join(', ')}`);
    process.exit(1);
  }

  // Load config and initialize Firebase
  const config = loadConfig();
  const db = initializeFirebase(config.serviceAccount);

  console.log(`Updating signal: ${options.signalId}`);
  console.log(`New status: ${options.status}`);

  // Update Firestore
  const firestoreUpdated = await updateFirestoreStatus(
    db,
    config.collection,
    config.clientId,
    options.signalId,
    options.status,
    options.briefId
  );
  console.log(`Firestore updated: ${firestoreUpdated ? 'Yes' : 'No'}`);

  if (options.briefId) {
    console.log(`Brief ID: ${options.briefId}`);
  }

  if (!firestoreUpdated) {
    console.error('Error: Signal not found in Firestore');
    process.exit(1);
  }
}

main().catch(err => {
  console.error('Error:', err.message);
  process.exit(1);
});
