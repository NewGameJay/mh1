/**
 * Firebase Admin initialization module
 * Initializes Firebase Admin SDK with service account credentials
 * 
 * Uses GOOGLE_APPLICATION_CREDENTIALS environment variable for credentials path.
 */

import admin from 'firebase-admin';
import { readFileSync } from 'fs';

let db = null;

/**
 * Initialize Firebase Admin and return Firestore instance
 * @returns {FirebaseFirestore.Firestore} Firestore database instance
 */
export function initializeFirebase() {
  if (db) {
    return db;
  }

  try {
    // Get credentials path from environment variable
    const credentialsPath = process.env.GOOGLE_APPLICATION_CREDENTIALS;
    
    if (!credentialsPath) {
      throw new Error(
        'GOOGLE_APPLICATION_CREDENTIALS environment variable is not set. ' +
        'Please set it to the path of your Firebase service account credentials JSON file.'
      );
    }

    const serviceAccount = JSON.parse(readFileSync(credentialsPath, 'utf8'));

    if (!admin.apps.length) {
      admin.initializeApp({
        credential: admin.credential.cert(serviceAccount)
      });
    }

    db = admin.firestore();
    return db;
  } catch (error) {
    if (error.code === 'ENOENT') {
      throw new Error(
        `Firebase credentials file not found at: ${process.env.GOOGLE_APPLICATION_CREDENTIALS}. ` +
        'Please verify the GOOGLE_APPLICATION_CREDENTIALS path is correct.'
      );
    }
    throw new Error(`Failed to initialize Firebase: ${error.message}`);
  }
}

export { admin };
