/**
 * Output formatters for Firestore data
 * Supports JSON, Markdown, and Table formats
 */

/**
 * Format data based on specified format
 * @param {Object} result - Data from path navigator
 * @param {string} format - Output format (json, markdown, table)
 * @param {Object} options - Formatting options
 * @returns {string} Formatted output
 */
export function formatOutput(result, format, options = {}) {
  const { depth = 1, expand = false } = options;

  switch (format) {
    case 'markdown':
      return formatAsMarkdown(result, { depth, expand });
    case 'table':
      return formatAsTable(result, { depth, expand });
    case 'json':
    default:
      return formatAsJson(result, { depth, expand });
  }
}

/**
 * Format as pretty-printed JSON
 * @param {Object} result - Data to format
 * @param {Object} options - Formatting options
 * @returns {string} JSON string
 */
export function formatAsJson(result, options = {}) {
  const { depth, expand } = options;

  // Apply depth limiting if not expanding
  const processed = expand ? result : applyDepthLimit(result, 0, depth);

  return JSON.stringify(processed, null, 2);
}

/**
 * Format as structured Markdown
 * @param {Object} result - Data to format
 * @param {Object} options - Formatting options
 * @returns {string} Markdown string
 */
export function formatAsMarkdown(result, options = {}) {
  const { depth, expand } = options;
  const lines = [];
  const meta = result._meta || {};

  // Header
  if (meta.type === 'root') {
    lines.push('# Firestore Root Collections');
    lines.push('');
    lines.push(`Found ${meta.collectionCount} collections:`);
    lines.push('');
    for (const col of result.collections || []) {
      lines.push(`- \`${col.id}\``);
    }
  } else if (meta.type === 'document') {
    lines.push(`## Document: ${meta.path}`);
    lines.push('');

    if (!meta.exists) {
      lines.push(`**Error**: Document not found`);
      lines.push('');
      lines.push(result.suggestion || '');
    } else {
      // Document ID
      lines.push(`**ID**: \`${meta.id}\``);

      // Subcollections hint
      if (meta.subCollections && meta.subCollections.length > 0) {
        lines.push(`**Subcollections**: ${meta.subCollections.map(s => `\`${s}\``).join(', ')}`);
      }
      lines.push('');

      // Data table
      lines.push('| Field | Value |');
      lines.push('|-------|-------|');

      for (const [key, value] of Object.entries(result.data || {})) {
        const displayValue = formatCellValue(value, depth, expand);
        lines.push(`| ${key} | ${displayValue} |`);
      }

      // Nested expansion
      if (expand && depth > 1) {
        lines.push('');
        for (const [key, value] of Object.entries(result.data || {})) {
          if (typeof value === 'object' && value !== null && !Array.isArray(value)) {
            lines.push(`### ${key}`);
            lines.push('');
            lines.push(formatNestedObject(value, 1, depth));
          }
        }
      }
    }
  } else if (meta.type === 'collection') {
    lines.push(`## Collection: ${meta.path}`);
    lines.push('');
    lines.push(`**Documents**: ${meta.showing} of ${meta.totalCount}${meta.truncated ? ' (truncated)' : ''}`);
    lines.push('');

    // List documents
    for (const doc of result.documents || []) {
      lines.push(`### ${doc.id}`);
      lines.push('');
      lines.push('| Field | Value |');
      lines.push('|-------|-------|');

      for (const [key, value] of Object.entries(doc.data || {})) {
        const displayValue = formatCellValue(value, depth, expand);
        lines.push(`| ${key} | ${displayValue} |`);
      }
      lines.push('');
    }
  }

  return lines.join('\n');
}

/**
 * Format as pipe-delimited table (for collections)
 * @param {Object} result - Data to format
 * @param {Object} options - Formatting options
 * @returns {string} Table string
 */
export function formatAsTable(result, options = {}) {
  const { depth, expand } = options;
  const meta = result._meta || {};

  if (meta.type === 'document') {
    // For single documents, show key-value pairs
    const lines = [];
    lines.push('| Field | Value |');
    lines.push('|-------|-------|');

    for (const [key, value] of Object.entries(result.data || {})) {
      const displayValue = formatCellValue(value, depth, expand);
      lines.push(`| ${key} | ${displayValue} |`);
    }

    return lines.join('\n');
  }

  if (meta.type === 'collection') {
    const documents = result.documents || [];
    if (documents.length === 0) {
      return 'No documents found.';
    }

    // Collect all unique fields across documents
    const allFields = new Set(['id']);
    for (const doc of documents) {
      for (const key of Object.keys(doc.data || {})) {
        allFields.add(key);
      }
    }
    const fields = Array.from(allFields);

    // Build table
    const lines = [];
    lines.push('| ' + fields.join(' | ') + ' |');
    lines.push('|' + fields.map(() => '---').join('|') + '|');

    for (const doc of documents) {
      const row = fields.map(field => {
        if (field === 'id') return doc.id;
        const value = doc.data?.[field];
        return formatCellValue(value, depth, expand);
      });
      lines.push('| ' + row.join(' | ') + ' |');
    }

    // Add metadata footer
    if (meta.truncated) {
      lines.push('');
      lines.push(`*Showing ${meta.showing} of ${meta.totalCount} documents*`);
    }

    return lines.join('\n');
  }

  if (meta.type === 'root') {
    const lines = [];
    lines.push('| Collection |');
    lines.push('|------------|');
    for (const col of result.collections || []) {
      lines.push(`| ${col.id} |`);
    }
    return lines.join('\n');
  }

  return formatAsJson(result, options);
}

/**
 * Format a single cell value for table display
 * @param {any} value - Value to format
 * @param {number} depth - Max depth to expand
 * @param {boolean} expand - Whether to expand nested objects
 * @returns {string} Formatted cell value
 */
export function formatCellValue(value, depth = 1, expand = false) {
  if (value === null || value === undefined) {
    return '_null_';
  }

  if (typeof value === 'boolean') {
    return value ? 'true' : 'false';
  }

  if (typeof value === 'number') {
    return String(value);
  }

  if (typeof value === 'string') {
    // Check if it's an ISO date
    if (/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}/.test(value)) {
      return value.split('T')[0];
    }
    // Truncate long strings
    if (value.length > 50) {
      return value.substring(0, 47) + '...';
    }
    return value;
  }

  if (Array.isArray(value)) {
    if (expand && depth > 1) {
      return value.map(v => formatCellValue(v, depth - 1, expand)).join(', ');
    }
    return `[Array: ${value.length} items]`;
  }

  if (typeof value === 'object') {
    const keys = Object.keys(value);
    if (expand && depth > 1) {
      const summary = keys.slice(0, 3).map(k => `${k}: ${formatCellValue(value[k], depth - 1, false)}`).join(', ');
      return `{${summary}${keys.length > 3 ? ', ...' : ''}}`;
    }
    return `[Object: ${keys.length} keys]`;
  }

  return String(value);
}

/**
 * Format nested object for markdown display
 * @param {Object} obj - Object to format
 * @param {number} currentDepth - Current depth level
 * @param {number} maxDepth - Maximum depth to expand
 * @returns {string} Formatted markdown
 */
function formatNestedObject(obj, currentDepth, maxDepth) {
  if (currentDepth >= maxDepth) {
    return '[Max depth reached]';
  }

  const lines = [];
  const indent = '  '.repeat(currentDepth);

  for (const [key, value] of Object.entries(obj)) {
    if (typeof value === 'object' && value !== null && !Array.isArray(value)) {
      lines.push(`${indent}- **${key}**:`);
      lines.push(formatNestedObject(value, currentDepth + 1, maxDepth));
    } else {
      const displayValue = formatCellValue(value, maxDepth - currentDepth, false);
      lines.push(`${indent}- ${key}: ${displayValue}`);
    }
  }

  return lines.join('\n');
}

/**
 * Apply depth limiting to nested objects
 * Preserves structure metadata (_meta) and applies depth limits to data content
 * @param {any} data - Data to limit
 * @param {number} currentDepth - Current depth
 * @param {number} maxDepth - Maximum depth (depth of nested content to show)
 * @param {boolean} isStructural - Whether we're in structural keys (_meta, data, documents)
 * @returns {any} Depth-limited data
 */
function applyDepthLimit(data, currentDepth, maxDepth, isStructural = true) {
  if (data === null || data === undefined) {
    return data;
  }

  // At root level, handle structural keys specially
  if (currentDepth === 0 && typeof data === 'object' && !Array.isArray(data)) {
    const result = {};
    for (const [key, value] of Object.entries(data)) {
      if (key === '_meta') {
        // Always preserve _meta fully
        result[key] = value;
      } else if (key === 'data' || key === 'documents' || key === 'collections') {
        // These are the content containers - apply depth limiting inside them
        result[key] = applyDepthLimit(value, 0, maxDepth, false);
      } else {
        result[key] = applyDepthLimit(value, currentDepth + 1, maxDepth, isStructural);
      }
    }
    return result;
  }

  // For non-structural content, apply depth limits
  if (!isStructural && currentDepth >= maxDepth) {
    if (Array.isArray(data)) {
      return `[Array: ${data.length} items]`;
    }
    if (typeof data === 'object') {
      return `[Object: ${Object.keys(data).length} keys]`;
    }
  }

  if (Array.isArray(data)) {
    return data.map(item => applyDepthLimit(item, currentDepth + 1, maxDepth, isStructural));
  }

  if (typeof data === 'object') {
    const result = {};
    for (const [key, value] of Object.entries(data)) {
      // Inside documents array, 'data' is content, 'id' and 'path' are structural
      if (key === 'data' && !isStructural) {
        result[key] = applyDepthLimit(value, 0, maxDepth, false);
      } else if (key === 'id' || key === 'path') {
        result[key] = value;
      } else {
        result[key] = applyDepthLimit(value, currentDepth + 1, maxDepth, isStructural);
      }
    }
    return result;
  }

  return data;
}
