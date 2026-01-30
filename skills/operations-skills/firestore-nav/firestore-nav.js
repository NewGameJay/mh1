#!/usr/bin/env node

/**
 * Firestore Navigation Tool
 *
 * Navigate Firestore collections and documents with flexible output formats.
 *
 * Usage:
 *   node firestore-nav.js <path> [options]
 *
 * Options:
 *   --format    json|markdown|table   Output format (default: json)
 *   --depth     1-5                   How deep to expand nested objects (default: 1)
 *   --fields    field1,field2         Specific fields to include
 *   --exclude   field1,field2         Fields to exclude
 *   --limit     N                     Max documents for collections (default: 20)
 *   --expand                          Expand nested objects inline
 *
 * Examples:
 *   node firestore-nav.js clients/abc123
 *   node firestore-nav.js clients/abc123/founderContent --format table --limit 10
 *   node firestore-nav.js clients/abc123 --fields name,status --format markdown
 */

import { initializeFirebase } from './lib/firebase-init.js';
import { navigateToPath, parsePath } from './lib/path-navigator.js';
import { formatOutput } from './lib/formatters.js';

/**
 * Parse command line arguments
 * @param {string[]} args - Command line arguments
 * @returns {Object} Parsed arguments
 */
function parseArgs(args) {
  const result = {
    path: '',
    format: 'json',
    depth: 2,
    fields: null,
    exclude: null,
    limit: 20,
    expand: false
  };

  let i = 0;
  while (i < args.length) {
    const arg = args[i];

    if (arg === '--format' && i + 1 < args.length) {
      const format = args[i + 1].toLowerCase();
      if (['json', 'markdown', 'table'].includes(format)) {
        result.format = format;
      }
      i += 2;
    } else if (arg.startsWith('--format=')) {
      const format = arg.split('=')[1].toLowerCase();
      if (['json', 'markdown', 'table'].includes(format)) {
        result.format = format;
      }
      i++;
    } else if (arg === '--depth' && i + 1 < args.length) {
      result.depth = Math.min(5, Math.max(1, parseInt(args[i + 1], 10) || 1));
      i += 2;
    } else if (arg.startsWith('--depth=')) {
      result.depth = Math.min(5, Math.max(1, parseInt(arg.split('=')[1], 10) || 1));
      i++;
    } else if (arg === '--fields' && i + 1 < args.length) {
      result.fields = args[i + 1].split(',').map(f => f.trim()).filter(Boolean);
      i += 2;
    } else if (arg.startsWith('--fields=')) {
      result.fields = arg.split('=')[1].split(',').map(f => f.trim()).filter(Boolean);
      i++;
    } else if (arg === '--exclude' && i + 1 < args.length) {
      result.exclude = args[i + 1].split(',').map(f => f.trim()).filter(Boolean);
      i += 2;
    } else if (arg.startsWith('--exclude=')) {
      result.exclude = arg.split('=')[1].split(',').map(f => f.trim()).filter(Boolean);
      i++;
    } else if (arg === '--limit' && i + 1 < args.length) {
      result.limit = Math.min(100, Math.max(1, parseInt(args[i + 1], 10) || 20));
      i += 2;
    } else if (arg.startsWith('--limit=')) {
      result.limit = Math.min(100, Math.max(1, parseInt(arg.split('=')[1], 10) || 20));
      i++;
    } else if (arg === '--expand') {
      result.expand = true;
      i++;
    } else if (arg === '--help' || arg === '-h') {
      printHelp();
      process.exit(0);
    } else if (!arg.startsWith('--') && !result.path) {
      result.path = arg;
      i++;
    } else {
      i++;
    }
  }

  return result;
}

/**
 * Print help message
 */
function printHelp() {
  console.log(`
Firestore Navigation Tool

Usage:
  node firestore-nav.js <path> [options]

Arguments:
  path                  Firestore path to navigate (e.g., "clients/abc123")

Options:
  --format <type>       Output format: json, markdown, table (default: json)
  --depth <n>           Depth to expand nested objects: 1-5 (default: 1)
  --fields <list>       Comma-separated fields to include
  --exclude <list>      Comma-separated fields to exclude
  --limit <n>           Max documents for collections: 1-100 (default: 20)
  --expand              Expand nested objects inline
  --help, -h            Show this help message

Path Types:
  Document (even segments):   clients/abc123
  Collection (odd segments):  clients/abc123/founderContent
  Root (empty):               ""

Examples:
  # Fetch a document
  node firestore-nav.js clients/{CLIENT_ID}

  # List a collection with limit
  node firestore-nav.js clients/{CLIENT_ID}/founderContent --limit 5

  # Format as markdown table
  node firestore-nav.js clients/{CLIENT_ID} --format markdown

  # Select specific fields
  node firestore-nav.js clients/{CLIENT_ID} --fields name,status,website

  # Deep collection navigation
  node firestore-nav.js clients/{CLIENT_ID}/socialListening/mentions/items --format table
`);
}

/**
 * Main execution
 */
async function main() {
  const args = process.argv.slice(2);

  if (args.length === 0) {
    printHelp();
    process.exit(0);
  }

  const options = parseArgs(args);

  if (!options.path && options.path !== '') {
    console.log(JSON.stringify({
      error: 'MISSING_PATH',
      message: 'Firestore path is required',
      usage: 'node firestore-nav.js <path> [options]',
      examples: [
        'clients/{CLIENT_ID}',
        'clients/{CLIENT_ID}/founderContent'
      ]
    }, null, 2));
    process.exit(1);
  }

  try {
    // Initialize Firebase
    const db = initializeFirebase();

    // Navigate to path
    const result = await navigateToPath(db, options.path, {
      limit: options.limit,
      fields: options.fields,
      exclude: options.exclude
    });

    // Format and output
    const output = formatOutput(result, options.format, {
      depth: options.depth,
      expand: options.expand
    });

    console.log(output);

    // Exit with error code if not found
    if (result.error === 'NOT_FOUND') {
      process.exit(1);
    }

    process.exit(0);
  } catch (error) {
    console.log(JSON.stringify({
      error: 'FIREBASE_ERROR',
      message: error.message,
      path: options.path
    }, null, 2));
    process.exit(1);
  }
}

main();
