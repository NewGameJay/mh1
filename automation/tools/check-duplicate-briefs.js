#!/usr/bin/env node

/**
 * Check if any existing assignment briefs use the same signal(s).
 *
 * Queries the Firestore assignment-briefs collection which contains:
 *   - id: uuid
 *   - title: string
 *   - status: "draft" | "used"
 *   - founder: string
 *   - content_pillar: content-pillar-id
 *   - funnel_stage: "TOFU" | "MOFU" | "BOFU"
 *   - signals: [signal-url-1, signal-url-2, ...]
 *   - pov: pov-id
 *   - target_persona: persona-id
 *   - created_at: timestamp
 *
 * Usage:
 *   node scripts/check-duplicate-briefs.js <signal-url-1> [signal-url-2] ...
 *
 * Examples:
 *   node scripts/check-duplicate-briefs.js "https://linkedin.com/posts/abc123"
 *   node scripts/check-duplicate-briefs.js "https://linkedin.com/posts/abc123" "https://linkedin.com/posts/def456"
 *
 * Options:
 *   --json     Output results as JSON
 *   --status   Filter by brief status (draft, used, all). Default: all
 *
 * Returns:
 *   Exit code 0 if no duplicates found
 *   Exit code 1 if duplicates found (prints matching brief IDs)
 */

const admin = require('firebase-admin');
const fs = require('fs');
const path = require('path');

// Project paths
const SCRIPT_DIR = __dirname;
const PROJECT_ROOT = path.dirname(SCRIPT_DIR);
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
  
  if (!admin.apps.length) {
    admin.initializeApp({
      credential: admin.credential.cert(serviceAccount)
    });
  }

  return admin.firestore();
}

/**
 * Check if any existing briefs use the same signal(s)
 *
 * Path: {collection}/{clientId}/modules/{moduleName}/assignment-briefs/
 */
async function checkDuplicateBriefs(db, collection, clientId, moduleName, signalUrls) {
  // Path: {collection}/{clientId}/modules/{moduleName}/assignment-briefs/
  const briefsRef = db
    .collection(collection)
    .doc(clientId)
    .collection('modules')
    .doc(moduleName)
    .collection('assignment-briefs');

  const duplicates = [];
  const checkedBriefIds = new Set();

  // Query for each signal URL using array-contains
  // Note: Firestore only allows one array-contains per query
  for (const signalUrl of signalUrls) {
    const query = briefsRef.where('signals', 'array-contains', signalUrl);
    const snapshot = await query.get();

    for (const doc of snapshot.docs) {
      // Skip the _index document
      if (doc.id === '_index') continue;

      const data = doc.data();
      const briefId = data.id || doc.id;

      // Skip if we've already processed this brief
      if (checkedBriefIds.has(briefId)) {
        // Update existing duplicate entry with additional overlapping signal
        const existingDup = duplicates.find(d => d.briefId === briefId);
        if (existingDup && !existingDup.overlappingSignals.includes(signalUrl)) {
          existingDup.overlappingSignals.push(signalUrl);
        }
        continue;
      }

      checkedBriefIds.add(briefId);
      const briefSignals = data.signals || [];

      // Find all overlapping signals
      const overlapping = signalUrls.filter(url => briefSignals.includes(url));

      duplicates.push({
        briefId,
        title: data.title || 'Unknown',
        status: data.status || 'unknown',
        founder: data.founder || '',
        contentPillar: data.content_pillar || '',
        funnelStage: data.funnel_stage || '',
        overlappingSignals: overlapping,
        allBriefSignals: briefSignals
      });
    }
  }

  return duplicates;
}

/**
 * Parse command line arguments
 */
function parseArgs() {
  const args = process.argv.slice(2);
  const result = {
    signals: [],
    json: false,
    status: 'all'
  };

  for (let i = 0; i < args.length; i++) {
    const arg = args[i];
    if (arg === '--json') {
      result.json = true;
    } else if (arg === '--status') {
      i++;
      if (args[i] && ['draft', 'used', 'all'].includes(args[i])) {
        result.status = args[i];
      }
    } else if (!arg.startsWith('--')) {
      result.signals.push(arg);
    }
  }

  return result;
}

/**
 * Main execution
 */
async function main() {
  const args = parseArgs();

  if (args.signals.length === 0) {
    console.error('Usage: node scripts/check-duplicate-briefs.js <signal-url-1> [signal-url-2] ...');
    console.error('');
    console.error('Options:');
    console.error('  --json           Output results as JSON');
    console.error('  --status <type>  Filter by brief status (draft, used, all). Default: all');
    process.exit(2);
  }

  // Load config and initialize Firebase
  const config = loadConfig();
  const db = initializeFirebase(config.serviceAccount);

  // Check for duplicates
  let duplicates = await checkDuplicateBriefs(
    db,
    config.collection,
    config.clientId,
    config.moduleName,
    args.signals
  );

  // Filter by status if specified
  if (args.status !== 'all') {
    duplicates = duplicates.filter(d => d.status === args.status);
  }

  if (duplicates.length > 0) {
    if (args.json) {
      console.log(JSON.stringify(duplicates, null, 2));
    } else {
      console.log(`Found ${duplicates.length} existing brief(s) using the same signal(s):`);
      console.log('');
      for (const dup of duplicates) {
        console.log(`  Brief ID: ${dup.briefId}`);
        console.log(`  Title: ${dup.title}`);
        console.log(`  Status: ${dup.status}`);
        if (dup.founder) {
          console.log(`  Founder: ${dup.founder}`);
        }
        if (dup.funnelStage) {
          console.log(`  Funnel Stage: ${dup.funnelStage}`);
        }
        console.log(`  Overlapping signals:`);
        for (const sig of dup.overlappingSignals) {
          console.log(`    - ${sig.length > 80 ? sig.slice(0, 80) + '...' : sig}`);
        }
        console.log('');
      }
    }
    process.exit(1);
  } else {
    if (args.json) {
      console.log('[]');
    } else {
      console.log('No duplicate briefs found. Safe to create new brief.');
    }
    process.exit(0);
  }
}

main().catch(error => {
  console.error('Error:', error.message);
  process.exit(2);
});

