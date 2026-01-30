/**
 * Timestamp conversion utilities
 * Converts Firestore Timestamp objects to ISO 8601 strings
 */

/**
 * Check if value is a Firestore timestamp object
 * @param {any} value - Value to check
 * @returns {boolean} True if value is a Firestore timestamp
 */
export function isTimestamp(value) {
  return value !== null &&
         typeof value === 'object' &&
         value._seconds !== undefined &&
         value._nanoseconds !== undefined;
}

/**
 * Convert a Firestore timestamp to ISO 8601 string
 * @param {Object} timestamp - Firestore timestamp object
 * @returns {string} ISO 8601 formatted date string
 */
export function timestampToISO(timestamp) {
  const millis = timestamp._seconds * 1000 + Math.floor(timestamp._nanoseconds / 1000000);
  return new Date(millis).toISOString();
}

/**
 * Recursively convert all Firestore timestamps in an object to ISO strings
 * @param {any} obj - Object to convert
 * @returns {any} Object with timestamps converted to ISO strings
 */
export function convertTimestamps(obj) {
  if (obj === null || obj === undefined) {
    return obj;
  }

  // Check if this is a Firestore Timestamp
  if (isTimestamp(obj)) {
    return timestampToISO(obj);
  }

  // Handle arrays
  if (Array.isArray(obj)) {
    return obj.map(convertTimestamps);
  }

  // Handle objects
  if (typeof obj === 'object') {
    const converted = {};
    for (const [key, value] of Object.entries(obj)) {
      converted[key] = convertTimestamps(value);
    }
    return converted;
  }

  // Return primitives as-is
  return obj;
}

/**
 * Format an ISO date string for display
 * @param {string} isoString - ISO 8601 date string
 * @param {boolean} includeTime - Whether to include time
 * @returns {string} Formatted date string
 */
export function formatDate(isoString, includeTime = false) {
  try {
    const date = new Date(isoString);
    if (includeTime) {
      return date.toISOString().replace('T', ' ').replace(/\.\d{3}Z$/, ' UTC');
    }
    return date.toISOString().split('T')[0];
  } catch {
    return isoString;
  }
}
