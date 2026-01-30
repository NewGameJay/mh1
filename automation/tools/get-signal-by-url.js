#!/usr/bin/env node
/**
 * Get signal(s) from Firestore by URL.
 *
 * Fetches one or more signals from the Firestore signals collection using their URLs.
 * Returns the signal data as JSON to stdout.
 *
 * Usage:
 *   node tools/get-signal-by-url.js <signal-url>
 *   node tools/get-signal-by-url.js <signal-url-1> <signal-url-2> <signal-url-3>
 *   node tools/get-signal-by-url.js <signal-url> --json
 *   node tools/get-signal-by-url.js <signal-url> --markdown
 *
 * Examples:
 *   node tools/get-signal-by-url.js "https://www.saastr.com/ai-and-the-death-of-the-2021-sales-process/"
 *   node tools/get-signal-by-url.js "https://url1.com/article" "https://url2.com/article" --json
 *   node tools/get-signal-by-url.js "https://www.linkedin.com/feed/update/urn:li:share:123456/" --markdown
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
 * Normalize URL by removing query parameters for matching
 * This handles cases where stored URLs have UTM params but brief URLs don't
 */
function normalizeUrlForMatching(url) {
  try {
    const parsed = new URL(url);
    // Return just the origin + pathname (no query string)
    return parsed.origin + parsed.pathname;
  } catch (e) {
    // If URL parsing fails, return as-is
    return url;
  }
}

/**
 * Format signal data from Firestore document
 */
function formatSignalData(doc, data) {
  return {
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
    usedInAssignmentBrief: data.used_in_assignment_brief || '',
    typeMetadata: data.type_metadata || {}
  };
}

/**
 * Get a signal by URL from Firestore
 * Supports both exact match and normalized URL matching (strips query params)
 */
async function getSignalByUrl(db, collection, clientId, signalUrl) {
  const signalsRef = db.collection(collection).doc(clientId).collection('signals');

  // First try exact match
  let snapshot = await signalsRef.where('url', '==', signalUrl).limit(1).get();

  if (!snapshot.empty) {
    const doc = snapshot.docs[0];
    const data = doc.data();
    return formatSignalData(doc, data);
  }

  // If exact match fails, try matching by base URL (without query params)
  // This handles cases where:
  // - Brief has: https://linkedin.com/posts/user_post-activity-123
  // - Firestore has: https://linkedin.com/posts/user_post-activity-123?utm_source=...
  const baseUrl = signalUrl.split('?')[0];

  // Use Firestore range query to find URLs starting with the base URL
  snapshot = await signalsRef
    .where('url', '>=', baseUrl)
    .where('url', '<', baseUrl + '\uf8ff')
    .limit(1)
    .get();

  if (!snapshot.empty) {
    const doc = snapshot.docs[0];
    const data = doc.data();
    return formatSignalData(doc, data);
  }

  // Final fallback: search recent signals by normalized URL comparison
  // This handles edge cases with URL encoding differences
  const normalizedSearchUrl = normalizeUrlForMatching(signalUrl);
  const recentSnapshot = await signalsRef
    .orderBy('uploaded_at', 'desc')
    .limit(200)
    .get();

  for (const doc of recentSnapshot.docs) {
    const data = doc.data();
    const storedUrl = data.url || '';
    if (normalizeUrlForMatching(storedUrl) === normalizedSearchUrl) {
      return formatSignalData(doc, data);
    }
  }

  return null;
}

/**
 * Get multiple signals by URLs from Firestore
 */
async function getSignalsByUrls(db, collection, clientId, signalUrls) {
  const results = [];
  const notFound = [];

  for (const url of signalUrls) {
    const signal = await getSignalByUrl(db, collection, clientId, url);
    if (signal) {
      results.push(signal);
    } else {
      notFound.push(url);
    }
  }

  return { signals: results, notFound };
}

/**
 * Format signal as markdown
 */
function signalToMarkdown(signal) {
  const title = (signal.title || '').replace(/"/g, "'");
  const lines = [
    '---',
    `id: ${signal.url || signal.id || ''}`,
    `type: ${signal.type}`,
    `source: ${signal.author}`,
    `title: "${title}"`,
    `date_posted: ${signal.datePosted}`,
    `date_added: ${signal.dateAdded}`,
    `url: ${signal.url}`,
    `status: ${signal.status}`,
    `used_in_assignment_brief: "${signal.usedInAssignmentBrief}"`,
    '---',
    '',
    signal.content || ''
  ];

  return lines.join('\n');
}

/**
 * Parse command line arguments
 */
function parseArgs() {
  const args = process.argv.slice(2);
  const options = {
    signalUrls: [],
    format: 'json' // default to json
  };

  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--json') {
      options.format = 'json';
    } else if (args[i] === '--markdown' || args[i] === '--md') {
      options.format = 'markdown';
    } else if (!args[i].startsWith('-')) {
      options.signalUrls.push(args[i]);
    }
  }

  return options;
}

/**
 * Print usage help
 */
function printUsage() {
  console.log(`
Usage: node tools/get-signal-by-url.js <signal-url> [signal-url-2] [...] [options]

Arguments:
  signal-url    One or more URLs of signals to fetch

Options:
  --json        Output as JSON (default)
  --markdown    Output as markdown with frontmatter

Examples:
  # Single signal
  node tools/get-signal-by-url.js "https://www.saastr.com/article/"

  # Multiple signals (for grouped briefs)
  node tools/get-signal-by-url.js "https://url1.com/a" "https://url2.com/b" "https://url3.com/c"

  # Output as markdown
  node tools/get-signal-by-url.js "https://www.linkedin.com/feed/update/urn:li:share:123/" --markdown
`);
}

/**
 * Main function
 */
async function main() {
  const options = parseArgs();

  if (options.signalUrls.length === 0) {
    printUsage();
    process.exit(1);
  }

  // Load config and initialize Firebase
  const config = loadConfig();
  const db = initializeFirebase(config.serviceAccount);

  // Fetch single or multiple signals
  if (options.signalUrls.length === 1) {
    // Single signal - maintain backward compatibility
    const signal = await getSignalByUrl(db, config.collection, config.clientId, options.signalUrls[0]);

    if (!signal) {
      console.error(`Signal not found: ${options.signalUrls[0]}`);
      process.exit(1);
    }

    if (options.format === 'markdown') {
      console.log(signalToMarkdown(signal));
    } else {
      console.log(JSON.stringify(signal, null, 2));
    }
  } else {
    // Multiple signals
    const { signals, notFound } = await getSignalsByUrls(db, config.collection, config.clientId, options.signalUrls);

    if (signals.length === 0) {
      console.error('No signals found for the provided URLs');
      process.exit(1);
    }

    if (options.format === 'markdown') {
      // Output each signal as markdown, separated by a divider
      const output = signals.map(s => signalToMarkdown(s)).join('\n\n---\n\n');
      console.log(output);
    } else {
      // Output as JSON array with metadata
      const result = {
        count: signals.length,
        signals: signals,
        notFound: notFound.length > 0 ? notFound : undefined
      };
      console.log(JSON.stringify(result, null, 2));
    }

    // Warn about not found signals
    if (notFound.length > 0) {
      console.error(`\nWarning: ${notFound.length} signal(s) not found:`);
      notFound.forEach(url => console.error(`  - ${url}`));
    }
  }
}

main().catch(err => {
  console.error('Error:', err.message);
  process.exit(1);
});
