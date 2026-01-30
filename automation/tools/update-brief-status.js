#!/usr/bin/env node
/**
 * Update assignment brief status in both local file and Firestore.
 *
 * Usage:
 *   node tools/update-brief-status.js <brief-id> --status draft|used
 *
 * Examples:
 *   node tools/update-brief-status.js "2026-01-12-building-in-public-d1ea25" --status used
 *   node tools/update-brief-status.js "2026-01-12-gen-marketer-ad8509" --status draft
 */

const { initializeApp, cert, getApps } = require('firebase-admin/app');
const { getFirestore } = require('firebase-admin/firestore');
const fs = require('fs');
const path = require('path');

// Project paths
const PROJECT_ROOT = path.dirname(__dirname);
const CONFIG_PATH = path.join(PROJECT_ROOT, 'config.md');
const BRIEFS_DIR = path.join(PROJECT_ROOT, 'assignment-briefs');

const VALID_STATUSES = ['draft', 'used'];

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
 * Find local brief file by ID
 * Searches for files where the frontmatter id matches or filename contains the brief ID
 */
function findLocalBriefFile(briefId) {
  if (!fs.existsSync(BRIEFS_DIR)) {
    return null;
  }

  const files = fs.readdirSync(BRIEFS_DIR).filter(f => f.endsWith('.md'));

  for (const file of files) {
    const filePath = path.join(BRIEFS_DIR, file);
    const content = fs.readFileSync(filePath, 'utf-8');

    // Check if ID matches in frontmatter
    const idMatch = content.match(/^id:\s*"?([^"\n]+)"?/m);
    if (idMatch && idMatch[1].trim() === briefId) {
      return filePath;
    }

    // Also check if filename contains the brief ID
    if (file.includes(briefId)) {
      return filePath;
    }
  }

  return null;
}

/**
 * Update the frontmatter in a local markdown file
 */
function updateLocalFrontmatter(filePath, status) {
  if (!fs.existsSync(filePath)) {
    return false;
  }

  let content = fs.readFileSync(filePath, 'utf-8');

  if (!content.startsWith('---')) {
    console.error(`Warning: No frontmatter found in ${filePath}`);
    return false;
  }

  const parts = content.split('---');
  if (parts.length < 3) {
    console.error(`Warning: Invalid frontmatter format in ${filePath}`);
    return false;
  }

  let frontmatter = parts[1];
  const body = parts.slice(2).join('---');

  // Update status field
  if (/^status:\s*.+$/m.test(frontmatter)) {
    frontmatter = frontmatter.replace(/^status:\s*.+$/m, `status: ${status}`);
  } else {
    frontmatter = frontmatter.trimEnd() + `\nstatus: ${status}\n`;
  }

  const newContent = `---${frontmatter}---${body}`;
  fs.writeFileSync(filePath, newContent, 'utf-8');

  return true;
}

/**
 * Update brief status in Firestore
 */
async function updateFirestoreStatus(db, collection, clientId, moduleName, briefId, status) {
  const briefsRef = db
    .collection(collection)
    .doc(clientId)
    .collection('modules')
    .doc(moduleName)
    .collection('assignment-briefs');

  // Try to find document by id field
  let snapshot = await briefsRef.where('id', '==', briefId).get();

  if (snapshot.empty) {
    // Try by document ID as fallback
    const docRef = briefsRef.doc(briefId);
    const doc = await docRef.get();
    if (doc.exists) {
      await docRef.update({ status });
      return true;
    }
    console.error(`Warning: Brief not found in Firestore: ${briefId}`);
    return false;
  }

  // Update the document (use first match only)
  const doc = snapshot.docs[0];
  await briefsRef.doc(doc.id).update({ status });
  return true;
}

/**
 * Parse command line arguments
 */
function parseArgs() {
  const args = process.argv.slice(2);
  const options = {
    briefId: null,
    status: null
  };

  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--status' || args[i] === '-s') {
      options.status = args[i + 1];
      i++;
    } else if (!args[i].startsWith('-')) {
      options.briefId = args[i];
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
  if (!options.briefId) {
    console.error('Error: Brief ID is required');
    console.error('Usage: node tools/update-brief-status.js <brief-id> --status draft|used');
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

  console.log(`Updating brief: ${options.briefId}`);
  console.log(`New status: ${options.status}`);

  // Update local file
  const localFile = findLocalBriefFile(options.briefId);
  let localUpdated = false;
  if (localFile) {
    localUpdated = updateLocalFrontmatter(localFile, options.status);
    console.log(`Local file updated: ${localUpdated ? path.basename(localFile) : 'No'}`);
  } else {
    console.log('Local file updated: No (file not found)');
  }

  // Update Firestore
  const firestoreUpdated = await updateFirestoreStatus(
    db,
    config.collection,
    config.clientId,
    config.moduleName,
    options.briefId,
    options.status
  );
  console.log(`Firestore updated: ${firestoreUpdated ? 'Yes' : 'No'}`);

  // Output JSON result for programmatic use
  console.log(JSON.stringify({
    success: localUpdated || firestoreUpdated,
    brief_id: options.briefId,
    status: options.status,
    local_updated: localUpdated,
    firestore_updated: firestoreUpdated
  }));

  if (!localUpdated && !firestoreUpdated) {
    console.error('Error: Brief not found in local files or Firestore');
    process.exit(1);
  }
}

main().catch(err => {
  console.error('Error:', err.message);
  process.exit(1);
});
