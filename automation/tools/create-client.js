#!/usr/bin/env node

/**
 * Create Client in Firestore
 *
 * This script creates a new client document in Firestore with a modules subcollection.
 * Creates the standard structure for MH1 clients.
 *
 * Usage:
 *     node tools/create-client.js --displayName "Acme Corp" --name "acme" --website "https://acme.com"
 *     node tools/create-client.js --json '{"displayName": "Acme Corp", "name": "acme", "website": "https://acme.com"}'
 *     node tools/create-client.js --dry-run --displayName "Test" --name "test" --website "https://test.com"
 *
 * Output (JSON):
 *     {"success": true, "client_id": "...", "path": "..."}
 *     {"success": false, "error": "..."}
 *
 * Firestore Structure Created:
 *     clients/{clientId}
 *       - displayName: string
 *       - name: string (slug)
 *       - website: string
 *       - createdAt: timestamp
 *       - status: "active"
 *       - modules: subcollection
 *         - linkedin-ghostwriter: {}
 *         - leads-database: {}
 *         - signals: {}
 */

require('dotenv').config();
const admin = require('firebase-admin');
const fs = require('fs');
const path = require('path');

// Paths
const SCRIPT_DIR = __dirname;
const PROJECT_ROOT = path.join(SCRIPT_DIR, '..');
const CONFIG_PATH = path.join(PROJECT_ROOT, 'config.md');

let db = null;

/**
 * Load configuration from config.md (for service account only)
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

  // Parse Collection (for reference)
  match = content.match(/\*\*Collection:\*\*\s*`([^`]+)`/);
  if (match) {
    config.collection = match[1];
  }

  // Validate required fields
  if (!config.serviceAccount) {
    throw new Error('Missing serviceAccount in config.md');
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
 * Generate a URL-safe slug from a name
 */
function generateSlug(name) {
  return name
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '');
}

/**
 * Check if a client already exists
 */
async function clientExists(collection, clientId) {
  const docRef = db.collection(collection).doc(clientId);
  const doc = await docRef.get();
  return doc.exists;
}

/**
 * Create client document and modules subcollection
 */
async function createClient(collection, clientData, dryRun = false) {
  const clientId = clientData.name;

  // Check if client already exists
  const exists = await clientExists(collection, clientId);
  if (exists) {
    throw new Error(`Client already exists: ${collection}/${clientId}`);
  }

  if (dryRun) {
    return {
      success: true,
      dry_run: true,
      client_id: clientId,
      path: `${collection}/${clientId}`,
      data: clientData,
      modules: ['linkedin-ghostwriter', 'leads-database', 'signals']
    };
  }

  // Create client document
  const clientRef = db.collection(collection).doc(clientId);

  const clientDoc = {
    displayName: clientData.displayName,
    name: clientData.name,
    website: clientData.website,
    createdAt: admin.firestore.FieldValue.serverTimestamp(),
    updatedAt: admin.firestore.FieldValue.serverTimestamp(),
    status: 'active',
    // Optional fields
    industry: clientData.industry || '',
    description: clientData.description || '',
    contactEmail: clientData.contactEmail || '',
    founders: clientData.founders || []
  };

  await clientRef.set(clientDoc);

  // Create modules subcollection with default module documents
  const modulesRef = clientRef.collection('modules');

  // LinkedIn Ghostwriter module
  await modulesRef.doc('linkedin-ghostwriter').set({
    enabled: true,
    createdAt: admin.firestore.FieldValue.serverTimestamp(),
    notionDatabaseId: '', // To be configured
    settings: {
      defaultFounder: '',
      postingSchedule: [],
      contentPillars: []
    }
  });

  // Leads Database module
  await modulesRef.doc('leads-database').set({
    enabled: true,
    createdAt: admin.firestore.FieldValue.serverTimestamp(),
    notionDatabaseId: '', // To be configured
    settings: {
      icpTypes: ['Primary', 'Secondary', 'Tertiary'],
      scoringWeights: {}
    }
  });

  // Signals module
  await modulesRef.doc('signals').set({
    enabled: true,
    createdAt: admin.firestore.FieldValue.serverTimestamp(),
    settings: {
      sources: [],
      keywords: {},
      thoughtLeaders: []
    }
  });

  return {
    success: true,
    client_id: clientId,
    display_name: clientData.displayName,
    website: clientData.website,
    path: `${collection}/${clientId}`,
    modules_created: ['linkedin-ghostwriter', 'leads-database', 'signals']
  };
}

/**
 * Parse command line arguments
 */
function parseArgs(args) {
  const result = {};

  // Check for --json flag
  const jsonIdx = args.indexOf('--json');
  if (jsonIdx >= 0 && args[jsonIdx + 1]) {
    try {
      return { ...JSON.parse(args[jsonIdx + 1]), fromJson: true };
    } catch (e) {
      throw new Error(`Invalid JSON: ${e.message}`);
    }
  }

  // Parse individual flags
  const flags = ['--displayName', '--name', '--website', '--industry', '--description', '--contactEmail'];

  for (const flag of flags) {
    const idx = args.indexOf(flag);
    if (idx >= 0 && args[idx + 1]) {
      const key = flag.replace('--', '');
      result[key] = args[idx + 1];
    }
  }

  return result;
}

/**
 * Main execution
 */
async function main() {
  const args = process.argv.slice(2);

  const dryRun = args.includes('--dry-run');

  // Parse arguments
  let clientData;
  try {
    clientData = parseArgs(args);
  } catch (e) {
    console.error(JSON.stringify({
      success: false,
      error: e.message
    }));
    process.exit(1);
  }

  // Validate required fields
  if (!clientData.displayName) {
    console.error(JSON.stringify({
      success: false,
      error: 'Missing required field: --displayName'
    }));
    process.exit(1);
  }

  // Generate name slug if not provided
  if (!clientData.name) {
    clientData.name = generateSlug(clientData.displayName);
  }

  // Validate website
  if (!clientData.website) {
    console.error(JSON.stringify({
      success: false,
      error: 'Missing required field: --website'
    }));
    process.exit(1);
  }

  try {
    // Initialize Firebase
    const config = loadConfig();
    db = initializeFirebase(config.serviceAccount);

    // Use collection from config (default to 'clients' for consistency with Python code)
    const collection = config.collection || 'clients';

    // Create client
    const result = await createClient(collection, clientData, dryRun);

    // Output results
    console.log(JSON.stringify(result, null, 2));

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
