#!/usr/bin/env node

/**
 * Upload LinkedIn Posts to Notion Database
 *
 * This script reads markdown post files from the posts/ directory
 * and uploads them to a Notion database. The database ID is retrieved
 * from Firebase (clients/{clientId}/modules/linkedin-ghostwriter.notionDatabaseId).
 *
 * Usage:
 *     node tools/upload-posts-to-notion.js "{post_path}"
 *     node tools/upload-posts-to-notion.js --all
 *     node tools/upload-posts-to-notion.js --all --dry-run
 *
 * Environment:
 *     NOTION_API_TOKEN - Notion integration token (from .env)
 *
 * Output (JSON):
 *     {"success": true, "uploaded": [...], "failed": [...]}
 *     {"success": false, "error": "..."}
 */

require('dotenv').config();
const { Client } = require('@notionhq/client');
const admin = require('firebase-admin');
const fs = require('fs');
const path = require('path');

// Paths
const SCRIPT_DIR = __dirname;
const PROJECT_ROOT = path.join(SCRIPT_DIR, '..');
const CONFIG_PATH = path.join(PROJECT_ROOT, 'config.md');
const POSTS_DIR = path.join(PROJECT_ROOT, 'posts');

let db = null;
let notion = null;

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
 * Initialize Notion client
 */
function initializeNotion() {
  const token = process.env.NOTION_API_TOKEN;
  if (!token) {
    throw new Error('NOTION_API_TOKEN not found in environment. Add it to .env file.');
  }

  return new Client({ auth: token });
}

/**
 * Get Notion database ID from Firebase
 * Path: clients/{clientId}/modules/linkedin-ghostwriter
 */
async function getNotionDatabaseId(collection, clientId) {
  const docRef = db.collection(collection).doc(clientId).collection('modules').doc('linkedin-ghostwriter');
  const doc = await docRef.get();

  if (!doc.exists) {
    throw new Error(`Module document not found: ${collection}/${clientId}/modules/linkedin-ghostwriter`);
  }

  const data = doc.data();
  const databaseId = data.notionDatabaseId;

  if (!databaseId) {
    throw new Error(`notionDatabaseId not found in ${collection}/${clientId}/modules/linkedin-ghostwriter`);
  }

  return databaseId;
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
      if ((value.startsWith('"') && value.endsWith('"')) ||
          (value.startsWith("'") && value.endsWith("'"))) {
        value = value.slice(1, -1);
      }
      currentValue.push(value);
      continue;
    }

    // Check for nested object property
    if (inNestedObject && line.startsWith('  ') && stripped.includes(':')) {
      const colonIdx = stripped.indexOf(':');
      const key = stripped.slice(0, colonIdx).trim();
      let value = stripped.slice(colonIdx + 1).trim();
      if ((value.startsWith('"') && value.endsWith('"')) ||
          (value.startsWith("'") && value.endsWith("'"))) {
        value = value.slice(1, -1);
      }
      nestedObject[key] = value;
      continue;
    }

    // Check for new key
    const colonIdx = line.indexOf(':');
    if (colonIdx > 0 && !stripped.startsWith('-') && !line.startsWith(' ')) {
      if (currentKey && inArray) {
        metadata[currentKey] = currentValue;
      }
      if (nestedKey && inNestedObject) {
        metadata[nestedKey] = nestedObject;
      }

      const key = line.slice(0, colonIdx).trim();
      let value = line.slice(colonIdx + 1).trim();

      if (value.startsWith('[') && value.endsWith(']')) {
        try {
          metadata[key] = JSON.parse(value);
        } catch (e) {
          const inner = value.slice(1, -1);
          const items = [];
          for (let item of inner.split(',')) {
            item = item.trim();
            if ((item.startsWith('"') && item.endsWith('"')) ||
                (item.startsWith("'") && item.endsWith("'"))) {
              item = item.slice(1, -1);
            }
            if (item) items.push(item);
          }
          metadata[key] = items;
        }
        currentKey = null;
        inArray = false;
        nestedKey = null;
        inNestedObject = false;
        nestedObject = {};
      } else if (value === '' || value === '[]') {
        if (i + 1 < lines.length && lines[i + 1].startsWith('  ') && !lines[i + 1].trim().startsWith('-')) {
          nestedKey = key;
          nestedObject = {};
          inNestedObject = true;
          currentKey = null;
          inArray = false;
        } else {
          currentKey = key;
          currentValue = [];
          inArray = true;
          nestedKey = null;
          inNestedObject = false;
          nestedObject = {};
        }
      } else {
        if ((value.startsWith('"') && value.endsWith('"')) ||
            (value.startsWith("'") && value.endsWith("'"))) {
          value = value.slice(1, -1);
        }
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
  const distributionMarker = '## Distribution Notes';
  const idx = body.indexOf(distributionMarker);

  if (idx > 0) {
    let content = body.slice(0, idx).trim();
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
 * Convert markdown content to Notion blocks
 */
function contentToNotionBlocks(content) {
  const blocks = [];
  const paragraphs = content.split('\n\n');

  for (const para of paragraphs) {
    const trimmed = para.trim();
    if (!trimmed) continue;

    // Check if it's a hashtag line
    if (trimmed.startsWith('#') && !trimmed.startsWith('##')) {
      blocks.push({
        object: 'block',
        type: 'paragraph',
        paragraph: {
          rich_text: [{
            type: 'text',
            text: { content: trimmed }
          }]
        }
      });
    } else {
      // Regular paragraph - split by single newlines for line breaks
      const lines = trimmed.split('\n');
      const richText = [];

      for (let i = 0; i < lines.length; i++) {
        richText.push({
          type: 'text',
          text: { content: lines[i] }
        });
        if (i < lines.length - 1) {
          richText.push({
            type: 'text',
            text: { content: '\n' }
          });
        }
      }

      blocks.push({
        object: 'block',
        type: 'paragraph',
        paragraph: { rich_text: richText }
      });
    }
  }

  return blocks;
}

/**
 * Build Notion page properties from post metadata
 * Maps to user's Notion database schema
 */
function buildNotionProperties(metadata, postContent, distributionNotes) {
  const properties = {};

  // Name (Title) - Required title property, use post title
  if (metadata.title) {
    properties['Name'] = {
      title: [{ text: { content: metadata.title } }]
    };
  }

  // Post ID (Rich Text)
  if (metadata.id) {
    properties['Post ID'] = {
      rich_text: [{ text: { content: metadata.id } }]
    };
  }

  // Content (Rich Text) - the actual post content
  if (postContent) {
    properties['Content'] = {
      rich_text: [{ text: { content: postContent.substring(0, 2000) } }]
    };
  }

  // Founder (Rich Text)
  if (metadata.founder) {
    properties['Founder'] = {
      rich_text: [{ text: { content: metadata.founder } }]
    };
  }

  // Content Pillar (Select)
  if (metadata.content_pillar) {
    properties['Content Pillar'] = {
      select: { name: metadata.content_pillar }
    };
  }

  // Funnel Stage (Select)
  if (metadata.funnel_stage) {
    properties['Funnel Stage'] = {
      select: { name: metadata.funnel_stage }
    };
  }

  // Status (Status type)
  if (metadata.status) {
    // Map our status values to Notion status names
    const statusMap = {
      'draft': 'Draft',
      'published': 'Published',
      'scheduled': 'Scheduled',
      'in_review': 'In Review'
    };
    const statusName = statusMap[metadata.status.toLowerCase()] || 'Draft';
    properties['Status'] = {
      status: { name: statusName }
    };
  }

  // Target Persona (Rich Text)
  if (metadata.target_persona) {
    properties['Target Persona'] = {
      rich_text: [{ text: { content: metadata.target_persona } }]
    };
  }

  // POV (Rich Text)
  if (metadata.pov) {
    properties['POV'] = {
      rich_text: [{ text: { content: metadata.pov.substring(0, 2000) } }]
    };
  }

  // Source Brief (Rich Text)
  if (metadata.source_brief) {
    properties['Source Brief'] = {
      rich_text: [{ text: { content: metadata.source_brief } }]
    };
  }

  // Word Count (Number)
  if (metadata.word_count) {
    properties['Word Count'] = {
      number: metadata.word_count
    };
  }

  // Created At (Date)
  if (metadata.created_at) {
    properties['Created At'] = {
      date: { start: metadata.created_at.split('T')[0] }
    };
  }

  // Uploaded At (Date) - current timestamp
  properties['Uploaded At'] = {
    date: { start: new Date().toISOString() }
  };

  // Signals Used (Rich Text - joined URLs)
  if (metadata.signals_used && Array.isArray(metadata.signals_used)) {
    properties['Signals Used'] = {
      rich_text: [{ text: { content: metadata.signals_used.join('\n').substring(0, 2000) } }]
    };
  }

  // Template ID (Rich Text)
  if (metadata.template && metadata.template.id) {
    properties['Template ID'] = {
      rich_text: [{ text: { content: metadata.template.id } }]
    };
  }

  // Template Name (Rich Text)
  if (metadata.template && metadata.template.name) {
    properties['Template Name'] = {
      rich_text: [{ text: { content: metadata.template.name } }]
    };
  }

  // Citations (Rich Text)
  if (metadata.citations && Array.isArray(metadata.citations)) {
    properties['Citations'] = {
      rich_text: [{ text: { content: metadata.citations.join('\n').substring(0, 2000) } }]
    };
  }

  // Distribution Notes fields
  if (distributionNotes) {
    // Best Posting Time (Rich Text)
    if (distributionNotes.best_posting_time) {
      properties['Best Posting Time'] = {
        rich_text: [{ text: { content: distributionNotes.best_posting_time } }]
      };
    }

    // Comment Links (URL) - use first link if available
    if (distributionNotes.comment_links && distributionNotes.comment_links.length > 0) {
      properties['Comment Links'] = {
        url: distributionNotes.comment_links[0]
      };
    }

    // Tags (Rich Text)
    if (distributionNotes.tags) {
      properties['Tags'] = {
        rich_text: [{ text: { content: distributionNotes.tags } }]
      };
    }
  }

  return properties;
}

/**
 * Check if a page already exists in Notion by Post ID
 */
async function pageExistsInNotion(databaseId, postId) {
  try {
    const response = await notion.databases.query({
      database_id: databaseId,
      filter: {
        property: 'Post ID',
        rich_text: {
          equals: postId
        }
      }
    });
    return response.results.length > 0;
  } catch (error) {
    return false;
  }
}

/**
 * Upload a single post to Notion
 */
async function uploadPostToNotion(databaseId, filePath, dryRun = false) {
  const content = fs.readFileSync(filePath, 'utf-8');
  const { metadata, body } = parseFrontmatter(content);
  const postContent = extractPostContent(body);
  const distributionNotes = extractDistributionNotes(body);

  const postId = metadata.id || path.basename(filePath, '.md');

  // Check if already exists
  const exists = await pageExistsInNotion(databaseId, postId);
  if (exists) {
    return {
      success: true,
      skipped: true,
      post_id: postId,
      reason: 'Already exists in Notion'
    };
  }

  if (dryRun) {
    return {
      success: true,
      dry_run: true,
      post_id: postId,
      title: metadata.title,
      properties: Object.keys(buildNotionProperties(metadata, postContent, distributionNotes))
    };
  }

  // Build properties and content blocks
  const properties = buildNotionProperties(metadata, postContent, distributionNotes);
  const blocks = contentToNotionBlocks(postContent);

  // Create page in Notion
  const response = await notion.pages.create({
    parent: { database_id: databaseId },
    properties: properties,
    children: blocks
  });

  return {
    success: true,
    post_id: postId,
    title: metadata.title,
    notion_page_id: response.id,
    notion_url: response.url
  };
}

/**
 * Get all post files in the posts directory
 */
function getAllPostFiles() {
  if (!fs.existsSync(POSTS_DIR)) {
    return [];
  }

  return fs.readdirSync(POSTS_DIR)
    .filter(f => f.endsWith('.md'))
    .map(f => path.join(POSTS_DIR, f));
}

/**
 * Resolve post file path
 */
function resolvePostPath(inputPath) {
  if (path.isAbsolute(inputPath)) {
    return inputPath;
  }
  if (inputPath.startsWith('posts/')) {
    return path.join(PROJECT_ROOT, inputPath);
  }
  return path.join(POSTS_DIR, inputPath);
}

/**
 * Main execution
 */
async function main() {
  const args = process.argv.slice(2);

  const uploadAll = args.includes('--all');
  const dryRun = args.includes('--dry-run');
  const filePaths = args.filter(a => !a.startsWith('--'));

  if (!uploadAll && filePaths.length === 0) {
    console.error(JSON.stringify({
      success: false,
      error: 'Usage: node tools/upload-posts-to-notion.js "{post_path}" OR --all [--dry-run]'
    }));
    process.exit(1);
  }

  try {
    // Initialize clients
    const config = loadConfig();
    db = initializeFirebase(config.serviceAccount);
    notion = initializeNotion();

    // Get Notion database ID from Firebase
    const databaseId = await getNotionDatabaseId(config.collection, config.clientId);

    // Determine files to upload
    let files = [];
    if (uploadAll) {
      files = getAllPostFiles();
    } else {
      files = filePaths.map(p => resolvePostPath(p));
    }

    if (files.length === 0) {
      console.log(JSON.stringify({
        success: true,
        message: 'No post files found',
        uploaded: [],
        failed: []
      }));
      process.exit(0);
    }

    // Upload each file
    const results = {
      uploaded: [],
      skipped: [],
      failed: []
    };

    for (const filePath of files) {
      if (!fs.existsSync(filePath)) {
        results.failed.push({
          file: filePath,
          error: 'File not found'
        });
        continue;
      }

      try {
        const result = await uploadPostToNotion(databaseId, filePath, dryRun);

        if (result.skipped) {
          results.skipped.push(result);
        } else {
          results.uploaded.push(result);
        }
      } catch (error) {
        results.failed.push({
          file: path.basename(filePath),
          error: error.message
        });
      }
    }

    // Output results
    console.log(JSON.stringify({
      success: true,
      dry_run: dryRun,
      database_id: databaseId,
      total_files: files.length,
      uploaded: results.uploaded,
      skipped: results.skipped,
      failed: results.failed
    }, null, 2));

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
