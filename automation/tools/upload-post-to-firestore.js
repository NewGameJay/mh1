#!/usr/bin/env node

/**
 * Upload LinkedIn Post to Firestore
 *
 * This script reads a markdown post file from the posts/ directory
 * and uploads it to Firestore under:
 *   {collection}/{clientId}/modules/{moduleName}/posts/{postId}
 *
 * Usage:
 *     node tools/upload-post-to-firestore.js "{post_path}"
 *
 * Examples:
 *     node tools/upload-post-to-firestore.js "posts/2026-01-14-building-in-public-a3f2b1.md"
 *     node tools/upload-post-to-firestore.js "2026-01-14-building-in-public-a3f2b1.md"
 *
 * Output (JSON):
 *     {"success": true, "post_id": "...", "title": "..."}
 *     {"success": false, "error": "..."}
 */

const admin = require('firebase-admin');
const fs = require('fs');
const path = require('path');

// Paths
const SCRIPT_DIR = __dirname;
const PROJECT_ROOT = path.join(SCRIPT_DIR, '..');
const CONFIG_PATH = path.join(PROJECT_ROOT, 'config.md');
const POSTS_DIR = path.join(PROJECT_ROOT, 'posts');

let db = null;

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
  admin.initializeApp({
    credential: admin.credential.cert(serviceAccount)
  });

  return admin.firestore();
}

/**
 * Parse YAML-like frontmatter from markdown content
 */
function parseFrontmatter(content) {
  const pattern = /^---\n([\s\S]*?)\n---\n([\s\S]*)$/;
  const match = content.match(pattern);

  if (!match) {
    return { metadata: {}, body: content };
  }

  const frontmatter = match[1];
  const body = match[2].trim();
  const metadata = {};

  let currentKey = null;
  let currentValue = [];
  let inArray = false;
  let inNestedObject = false;
  let nestedKey = null;
  let nestedObject = {};

  const lines = frontmatter.split('\n');
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    const stripped = line.trim();

    // Check if this is an array item
    if (stripped.startsWith('- ') && inArray) {
      let value = stripped.slice(2).trim();
      // Remove quotes
      if ((value.startsWith('"') && value.endsWith('"')) ||
          (value.startsWith("'") && value.endsWith("'"))) {
        value = value.slice(1, -1);
      }
      currentValue.push(value);
      continue;
    }

    // Check for nested object property (indented key: value)
    if (inNestedObject && line.startsWith('  ') && stripped.includes(':')) {
      const colonIdx = stripped.indexOf(':');
      const key = stripped.slice(0, colonIdx).trim();
      let value = stripped.slice(colonIdx + 1).trim();
      // Remove quotes
      if ((value.startsWith('"') && value.endsWith('"')) ||
          (value.startsWith("'") && value.endsWith("'"))) {
        value = value.slice(1, -1);
      }
      nestedObject[key] = value;
      continue;
    }

    // Check for new key (not indented)
    const colonIdx = line.indexOf(':');
    if (colonIdx > 0 && !stripped.startsWith('-') && !line.startsWith(' ')) {
      // Save previous key if exists
      if (currentKey && inArray) {
        metadata[currentKey] = currentValue;
      }
      if (nestedKey && inNestedObject) {
        metadata[nestedKey] = nestedObject;
      }

      const key = line.slice(0, colonIdx).trim();
      let value = line.slice(colonIdx + 1).trim();

      // Check if value is an inline array
      if (value.startsWith('[') && value.endsWith(']')) {
        try {
          metadata[key] = JSON.parse(value);
        } catch (e) {
          // Parse manually
          const inner = value.slice(1, -1);
          const items = [];
          for (let item of inner.split(',')) {
            item = item.trim();
            if ((item.startsWith('"') && item.endsWith('"')) ||
                (item.startsWith("'") && item.endsWith("'"))) {
              item = item.slice(1, -1);
            }
            if (item) {
              items.push(item);
            }
          }
          metadata[key] = items;
        }
        currentKey = null;
        inArray = false;
        nestedKey = null;
        inNestedObject = false;
        nestedObject = {};
      } else if (value === '' || value === '[]') {
        // Check if next line is indented (nested object) or array
        if (i + 1 < lines.length && lines[i + 1].startsWith('  ') && !lines[i + 1].trim().startsWith('-')) {
          // Nested object starting
          nestedKey = key;
          nestedObject = {};
          inNestedObject = true;
          currentKey = null;
          inArray = false;
        } else {
          // Multi-line array starting
          currentKey = key;
          currentValue = [];
          inArray = true;
          nestedKey = null;
          inNestedObject = false;
          nestedObject = {};
        }
      } else {
        // Regular value
        if ((value.startsWith('"') && value.endsWith('"')) ||
            (value.startsWith("'") && value.endsWith("'"))) {
          value = value.slice(1, -1);
        }
        // Handle numeric values
        if (/^\d+$/.test(value)) {
          metadata[key] = parseInt(value, 10);
        } else {
          metadata[key] = value;
        }
        currentKey = null;
        inArray = false;
        nestedKey = null;
        inNestedObject = false;
        nestedObject = {};
      }
    }
  }

  // Save last key if exists
  if (currentKey && inArray) {
    metadata[currentKey] = currentValue;
  }
  if (nestedKey && inNestedObject) {
    metadata[nestedKey] = nestedObject;
  }

  return { metadata, body };
}

/**
 * Extract post content (before Distribution Notes section)
 */
function extractPostContent(body) {
  // Split at the Distribution Notes section
  const distributionMarker = '## Distribution Notes';
  const idx = body.indexOf(distributionMarker);

  if (idx > 0) {
    // Get content before Distribution Notes, trim trailing separator
    let content = body.slice(0, idx).trim();
    // Remove trailing horizontal rule if present
    if (content.endsWith('---')) {
      content = content.slice(0, -3).trim();
    }
    return content;
  }

  return body;
}

/**
 * Extract distribution notes from body
 */
function extractDistributionNotes(body) {
  const distributionMarker = '## Distribution Notes';
  const idx = body.indexOf(distributionMarker);

  if (idx < 0) {
    return {};
  }

  const notesSection = body.slice(idx);
  const notes = {};

  // Extract "Post in comments" links
  const commentsMatch = notesSection.match(/\*\*Post in comments:\*\*\n([\s\S]*?)(?=\n\*\*|$)/);
  if (commentsMatch) {
    const links = [];
    const linkLines = commentsMatch[1].split('\n');
    for (const line of linkLines) {
      const trimmed = line.trim();
      if (trimmed.startsWith('- ')) {
        links.push(trimmed.slice(2).trim());
      }
    }
    notes.comment_links = links;
  }

  // Extract "Best posting time"
  const timeMatch = notesSection.match(/\*\*Best posting time:\*\*\s*(.+)/);
  if (timeMatch) {
    notes.best_posting_time = timeMatch[1].trim();
  }

  // Extract "Tags"
  const tagsMatch = notesSection.match(/\*\*Tags:\*\*\s*(.+)/);
  if (tagsMatch) {
    notes.tags = tagsMatch[1].trim();
  }

  return notes;
}

/**
 * Process a single post file and return document data
 * Schema:
 *   id: string
 *   title: string
 *   source_brief: string (brief ID/filename)
 *   status: "created" | "published" | "scheduled"
 *   founder: string
 *   content_pillar: string
 *   template: { id: string, name: string }
 *   funnel_stage: "TOFU" | "MOFU" | "BOFU"
 *   signals_used: string[] (signal URLs)
 *   pov: string
 *   target_persona: string
 *   word_count: number
 *   created_at: string (ISO timestamp)
 *   citations: string[]
 *   content: string (the actual LinkedIn post text)
 *   distribution_notes: { comment_links: [], best_posting_time: "", tags: "" }
 */
function processPostFile(filePath) {
  const content = fs.readFileSync(filePath, 'utf-8');
  const { metadata, body } = parseFrontmatter(content);

  // Extract post content (before Distribution Notes)
  const postContent = extractPostContent(body);

  // Extract distribution notes
  const distributionNotes = extractDistributionNotes(body);

  // Calculate word count if not provided
  const wordCount = metadata.word_count || postContent.split(/\s+/).filter(w => w.length > 0).length;

  // Generate document data matching exact schema
  const postDoc = {
    id: metadata.id || path.basename(filePath, '.md'),
    title: metadata.title || '',
    source_brief: metadata.source_brief || '',
    status: metadata.status || 'created',
    founder: metadata.founder || '',
    content_pillar: metadata.content_pillar || '',
    template: metadata.template || { id: '', name: '' },
    funnel_stage: metadata.funnel_stage || 'TOFU',
    signals_used: metadata.signals_used || [],
    pov: metadata.pov || '',
    target_persona: metadata.target_persona || '',
    word_count: wordCount,
    created_at: metadata.created_at || new Date().toISOString(),
    citations: metadata.citations || [],
    content: postContent,
    distribution_notes: distributionNotes,
    uploaded_at: admin.firestore.FieldValue.serverTimestamp()
  };

  return postDoc;
}

/**
 * Upload a single post to Firestore
 */
async function uploadPost(collection, clientId, moduleName, postDoc) {
  // Path: {collection}/{clientId}/modules/{moduleName}/posts/{postId}
  const postsRef = db
    .collection(collection)
    .doc(clientId)
    .collection('modules')
    .doc(moduleName)
    .collection('posts');

  const docRef = postsRef.doc(postDoc.id);
  await docRef.set(postDoc);

  return postDoc.id;
}

/**
 * Resolve post file path
 */
function resolvePostPath(inputPath) {
  // If absolute path, use as-is
  if (path.isAbsolute(inputPath)) {
    return inputPath;
  }

  // If starts with posts/, resolve from project root
  if (inputPath.startsWith('posts/')) {
    return path.join(PROJECT_ROOT, inputPath);
  }

  // Otherwise, assume it's just a filename in posts/
  return path.join(POSTS_DIR, inputPath);
}

/**
 * Main execution
 */
async function main() {
  const args = process.argv.slice(2);

  if (args.length === 0) {
    console.error(JSON.stringify({
      success: false,
      error: 'Usage: node tools/upload-post-to-firestore.js "{post_path}"'
    }));
    process.exit(1);
  }

  const inputPath = args[0];
  const filePath = resolvePostPath(inputPath);

  // Check if file exists
  if (!fs.existsSync(filePath)) {
    console.error(JSON.stringify({
      success: false,
      error: `Post file not found: ${filePath}`
    }));
    process.exit(1);
  }

  try {
    // Load config and initialize Firebase
    const config = loadConfig();
    db = initializeFirebase(config.serviceAccount);

    // Process and upload the post
    const postDoc = processPostFile(filePath);
    await uploadPost(config.collection, config.clientId, config.moduleName, postDoc);

    // Output success
    console.log(JSON.stringify({
      success: true,
      post_id: postDoc.id,
      title: postDoc.title,
      source_brief: postDoc.source_brief,
      status: postDoc.status,
      founder: postDoc.founder,
      funnel_stage: postDoc.funnel_stage,
      word_count: postDoc.word_count,
      firestore_path: `${config.collection}/${config.clientId}/modules/${config.moduleName}/posts/${postDoc.id}`
    }));

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
