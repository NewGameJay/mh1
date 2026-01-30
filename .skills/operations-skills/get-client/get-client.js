#!/usr/bin/env node

import admin from 'firebase-admin';
import { readFileSync } from 'fs';

async function getClient(clientId) {
  try {
    // Get credentials path from environment variable
    const credentialsPath = process.env.GOOGLE_APPLICATION_CREDENTIALS;
    
    if (!credentialsPath) {
      console.log(JSON.stringify({
        error: 'CONFIG_ERROR',
        message: 'GOOGLE_APPLICATION_CREDENTIALS environment variable is not set. ' +
                 'Please set it to the path of your Firebase service account credentials JSON file.'
      }));
      process.exit(1);
    }

    // Load service account credentials
    let serviceAccount;
    try {
      serviceAccount = JSON.parse(readFileSync(credentialsPath, 'utf8'));
    } catch (err) {
      console.log(JSON.stringify({
        error: 'CONFIG_ERROR',
        message: `Failed to load credentials from ${credentialsPath}: ${err.message}`
      }));
      process.exit(1);
    }

    // Initialize Firebase Admin
    if (!admin.apps.length) {
      admin.initializeApp({
        credential: admin.credential.cert(serviceAccount)
      });
    }

    const db = admin.firestore();

    // Fetch the client document
    const docRef = db.collection('clients').doc(clientId);
    const doc = await docRef.get();

    if (!doc.exists) {
      console.log(JSON.stringify({
        error: 'NOT_FOUND',
        message: `Client not found: ${clientId}`
      }));
      process.exit(1);
    }

    // Convert Firebase Timestamps to ISO strings
    const convertTimestamps = (obj) => {
      if (obj === null || obj === undefined) return obj;

      if (obj._seconds !== undefined && obj._nanoseconds !== undefined) {
        // This is a Firestore Timestamp
        const date = new Date(obj._seconds * 1000 + obj._nanoseconds / 1000000);
        return date.toISOString();
      }

      if (Array.isArray(obj)) {
        return obj.map(convertTimestamps);
      }

      if (typeof obj === 'object') {
        const converted = {};
        for (const [key, value] of Object.entries(obj)) {
          converted[key] = convertTimestamps(value);
        }
        return converted;
      }

      return obj;
    };

    // Return the document data with timestamps converted
    const rawData = doc.data();
    const result = {
      id: doc.id,
      path: `clients/${doc.id}`,
      data: convertTimestamps(rawData)
    };

    console.log(JSON.stringify(result, null, 2));
    process.exit(0);

  } catch (error) {
    console.log(JSON.stringify({
      error: 'FIREBASE_ERROR',
      message: error.message,
      stack: error.stack
    }));
    process.exit(1);
  }
}

// Parse command line arguments
const clientId = process.argv[2];

if (!clientId) {
  console.log(JSON.stringify({
    error: 'MISSING_ARGUMENT',
    message: 'Client ID is required'
  }));
  process.exit(1);
}

getClient(clientId);
