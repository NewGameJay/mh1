/**
 * Firestore path navigation utilities
 * Parse paths and navigate to documents/collections
 */

import { convertTimestamps } from './timestamp-utils.js';

/**
 * Parse a Firestore path into segments and determine type
 * @param {string} path - Firestore path (e.g., "clients/abc123/founderContent")
 * @returns {Object} Parsed path information
 */
export function parsePath(path) {
  // Remove leading/trailing slashes and split
  const segments = path.replace(/^\/+|\/+$/g, '').split('/').filter(Boolean);

  return {
    segments,
    isCollection: segments.length % 2 === 1,
    isDocument: segments.length % 2 === 0,
    depth: Math.ceil(segments.length / 2),
    parentPath: segments.length > 1 ? segments.slice(0, -1).join('/') : null,
    name: segments[segments.length - 1] || null
  };
}

/**
 * Navigate to a Firestore path and return the data
 * @param {FirebaseFirestore.Firestore} db - Firestore instance
 * @param {string} path - Path to navigate to
 * @param {Object} options - Navigation options
 * @returns {Promise<Object>} Result with metadata and data
 */
export async function navigateToPath(db, path, options = {}) {
  const { limit = 20, fields = null, exclude = null } = options;
  const parsed = parsePath(path);

  if (parsed.segments.length === 0) {
    // Root level - list all collections
    return await listRootCollections(db);
  }

  if (parsed.isDocument) {
    return await fetchDocument(db, parsed.segments, { fields, exclude });
  } else {
    return await listCollection(db, parsed.segments, { limit, fields, exclude });
  }
}

/**
 * List root collections in Firestore
 * @param {FirebaseFirestore.Firestore} db - Firestore instance
 * @returns {Promise<Object>} List of root collections
 */
async function listRootCollections(db) {
  const collections = await db.listCollections();

  return {
    _meta: {
      path: '/',
      type: 'root',
      collectionCount: collections.length
    },
    collections: collections.map(col => ({
      id: col.id,
      path: col.id
    }))
  };
}

/**
 * Fetch a single document
 * @param {FirebaseFirestore.Firestore} db - Firestore instance
 * @param {string[]} segments - Path segments
 * @param {Object} options - Fetch options
 * @returns {Promise<Object>} Document data
 */
async function fetchDocument(db, segments, options = {}) {
  const { fields, exclude } = options;
  const path = segments.join('/');

  // Build reference by alternating collection/doc
  let ref = db;
  for (let i = 0; i < segments.length; i++) {
    if (i % 2 === 0) {
      ref = ref.collection(segments[i]);
    } else {
      ref = ref.doc(segments[i]);
    }
  }

  const doc = await ref.get();

  if (!doc.exists) {
    return {
      _meta: {
        path,
        type: 'document',
        exists: false
      },
      error: 'NOT_FOUND',
      message: `Document not found: ${path}`,
      suggestion: `Check if the path is correct. Try listing the parent collection.`
    };
  }

  // Get subcollections
  const subCollections = await doc.ref.listCollections();

  let data = convertTimestamps(doc.data());
  data = applyFieldFilters(data, fields, exclude);

  return {
    _meta: {
      path,
      type: 'document',
      exists: true,
      id: doc.id,
      subCollections: subCollections.map(c => c.id)
    },
    data
  };
}

/**
 * List documents in a collection
 * @param {FirebaseFirestore.Firestore} db - Firestore instance
 * @param {string[]} segments - Path segments
 * @param {Object} options - List options
 * @returns {Promise<Object>} Collection data
 */
async function listCollection(db, segments, options = {}) {
  const { limit, fields, exclude } = options;
  const path = segments.join('/');

  // Build reference by alternating collection/doc
  let ref = db;
  for (let i = 0; i < segments.length; i++) {
    if (i % 2 === 0) {
      ref = ref.collection(segments[i]);
    } else {
      ref = ref.doc(segments[i]);
    }
  }

  // Get total count
  const countResult = await ref.count().get();
  const totalCount = countResult.data().count;

  // Fetch documents with limit
  const snapshot = await ref.limit(limit).get();

  const documents = [];
  for (const doc of snapshot.docs) {
    let data = convertTimestamps(doc.data());
    data = applyFieldFilters(data, fields, exclude);

    documents.push({
      id: doc.id,
      path: doc.ref.path,
      data
    });
  }

  return {
    _meta: {
      path,
      type: 'collection',
      totalCount,
      showing: snapshot.size,
      limit,
      truncated: totalCount > limit,
      ...(totalCount > limit && { message: `Showing ${snapshot.size} of ${totalCount} documents` })
    },
    documents
  };
}

/**
 * Apply field inclusion/exclusion filters
 * @param {Object} data - Data to filter
 * @param {string[]|null} fields - Fields to include
 * @param {string[]|null} exclude - Fields to exclude
 * @returns {Object} Filtered data
 */
function applyFieldFilters(data, fields, exclude) {
  if (!data || typeof data !== 'object') {
    return data;
  }

  let result = data;

  // Apply inclusion filter
  if (fields && fields.length > 0) {
    result = {};
    for (const field of fields) {
      if (field in data) {
        result[field] = data[field];
      }
    }
  }

  // Apply exclusion filter
  if (exclude && exclude.length > 0) {
    result = { ...result };
    for (const field of exclude) {
      delete result[field];
    }
  }

  return result;
}

/**
 * Discover subcollections for a document
 * @param {FirebaseFirestore.Firestore} db - Firestore instance
 * @param {string} path - Document path
 * @returns {Promise<string[]>} List of subcollection names
 */
export async function discoverSubcollections(db, path) {
  const parsed = parsePath(path);

  if (!parsed.isDocument) {
    throw new Error('Subcollection discovery requires a document path');
  }

  // Build reference to document
  let ref = db;
  for (let i = 0; i < parsed.segments.length; i++) {
    if (i % 2 === 0) {
      ref = ref.collection(parsed.segments[i]);
    } else {
      ref = ref.doc(parsed.segments[i]);
    }
  }

  const collections = await ref.listCollections();
  return collections.map(c => c.id);
}
