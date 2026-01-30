#!/usr/bin/env node
/**
 * Get unread signals from Firestore.
 *
 * Queries Firestore signals collection directly, filtered by:
 * - status: 'unused' only
 * - sorted by: date_posted (desc)
 *
 * Usage:
 *   node tools/get-unread-signals.js [--limit N] [--json]
 *
 * Options:
 *   --limit N       Limit the number of signals to fetch (default: 20)
 *   --json          Output signal data as JSON (for programmatic use)
 *
 * Examples:
 *   node tools/get-unread-signals.js
 *   node tools/get-unread-signals.js --limit 10
 *   node tools/get-unread-signals.js --limit 10 --json
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
 * Fetch unread signals from Firestore
 */
async function getUnreadSignals(db, collection, clientId, limit = 20) {
  const signalsRef = db.collection(collection).doc(clientId).collection('signals');

  // Query for unused signals
  const snapshot = await signalsRef.where('status', '==', 'unused').get();

  const signals = [];
  snapshot.forEach(doc => {
    const data = doc.data();
    signals.push({
      id: data.id || doc.id,
      firestoreId: doc.id,
      type: data.type || '',
      title: data.title || '',
      content: data.content || '',
      author: data.author || '',
      url: data.url || '',
      datePosted: data.date_posted || '',
      dateAdded: data.date_added || '',
      keyword: data.keyword || '',
      status: data.status || '',
      typeMetadata: data.type_metadata || {}
    });
  });

  // Sort by date_posted (desc) - most recent first
  signals.sort((a, b) => {
    const dateA = a.datePosted ? new Date(a.datePosted).getTime() : 0;
    const dateB = b.datePosted ? new Date(b.datePosted).getTime() : 0;
    return dateB - dateA;
  });

  return limit ? signals.slice(0, limit) : signals;
}

/**
 * Parse command line arguments
 */
function parseArgs() {
  const args = process.argv.slice(2);
  const options = { limit: 20, json: false };

  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--limit' || args[i] === '-n') {
      options.limit = parseInt(args[i + 1], 10) || 20;
      i++;
    } else if (args[i] === '--json') {
      options.json = true;
    }
  }

  return options;
}

/**
 * Main function
 */
async function main() {
  const options = parseArgs();

  // Load config and initialize Firebase
  const config = loadConfig();
  const db = initializeFirebase(config.serviceAccount);

  // Only log to stderr if outputting JSON, so stdout stays clean for parsing
  const log = options.json ? console.error.bind(console) : console.log.bind(console);

  log('Fetching unread signals from Firestore...');
  log(`Collection: ${config.collection}/${config.clientId}/signals/\n`);

  const signals = await getUnreadSignals(db, config.collection, config.clientId, options.limit);

  if (signals.length === 0) {
    if (options.json) {
      console.log(JSON.stringify({ signals: [], count: 0 }));
    } else {
      console.log('No unread signals found.');
    }
    process.exit(0);
  }

  log(`Total unread signals fetched: ${signals.length}\n`);

  // Output results
  if (options.json) {
    const output = {
      signals: signals.map(s => ({
        id: s.id,
        firestoreId: s.firestoreId,
        title: s.title,
        author: s.author,
        url: s.url,
        datePosted: s.datePosted,
        dateAdded: s.dateAdded,
        content: s.content,
        type: s.type,
        keyword: s.keyword,
        status: s.status,
        typeMetadata: s.typeMetadata
      })),
      count: signals.length
    };
    console.log(JSON.stringify(output, null, 2));
  } else {
    // Human-readable output
    for (const signal of signals) {
      console.log(`- [${signal.type}] ${signal.title}`);
      console.log(`  Author: ${signal.author}`);
      console.log(`  Date: ${signal.datePosted}`);
      console.log(`  URL: ${signal.url}`);
      console.log(`  ID: ${signal.firestoreId}`);
      console.log('');
    }
  }
}

main().catch(err => {
  console.error('Error:', err.message);
  process.exit(1);
});
