const admin = require('firebase-admin');
const fs = require('fs');

// Get credentials path from environment variable
const credentialsPath = process.env.GOOGLE_APPLICATION_CREDENTIALS;

if (!credentialsPath) {
  console.error(JSON.stringify({
    error: 'CONFIG_ERROR',
    message: 'GOOGLE_APPLICATION_CREDENTIALS environment variable is not set. ' +
             'Please set it to the path of your Firebase service account credentials JSON file.'
  }));
  process.exit(1);
}

// Load service account credentials
let serviceAccount;
try {
  serviceAccount = JSON.parse(fs.readFileSync(credentialsPath, 'utf8'));
} catch (err) {
  console.error(JSON.stringify({
    error: 'CONFIG_ERROR',
    message: `Failed to load credentials from ${credentialsPath}: ${err.message}`
  }));
  process.exit(1);
}

if (!admin.apps.length) {
  admin.initializeApp({
    credential: admin.credential.cert(serviceAccount)
  });
}

const db = admin.firestore();

async function fetchFullClient(clientId) {
  try {
    const clientRef = db.collection('clients').doc(clientId);
    const clientDoc = await clientRef.get();

    if (!clientDoc.exists) {
      console.error(JSON.stringify({
        error: 'NOT_FOUND',
        message: `Client ${clientId} not found`
      }));
      process.exit(1);
    }

    const result = {
      id: clientDoc.id,
      path: clientDoc.ref.path,
      data: clientDoc.data(),
      subCollections: {}
    };

    // List all sub-collections
    const collections = await clientRef.listCollections();

    // Fetch up to 10 items from each sub-collection
    for (const collection of collections) {
      const collectionName = collection.id;
      result.subCollections[collectionName] = {
        _metadata: {
          path: `${clientDoc.ref.path}/${collectionName}`,
          limit: 10
        },
        items: {}
      };

      const snapshot = await collection.limit(10).get();
      const totalCount = (await collection.count().get()).data().count;

      result.subCollections[collectionName]._metadata.totalCount = totalCount;
      result.subCollections[collectionName]._metadata.showing = snapshot.size;

      if (totalCount > 10) {
        result.subCollections[collectionName]._metadata.truncated = true;
        result.subCollections[collectionName]._metadata.message = `Showing first 10 of ${totalCount} items`;
      }

      // Process each document in the sub-collection
      for (const doc of snapshot.docs) {
        const docData = {
          id: doc.id,
          path: doc.ref.path,
          data: doc.data()
        };

        // Check if this document has sub-collections
        const subCollections = await doc.ref.listCollections();
        if (subCollections.length > 0) {
          docData.subCollections = {};

          for (const subCol of subCollections) {
            const subColName = subCol.id;
            docData.subCollections[subColName] = {
              _metadata: {
                path: `${doc.ref.path}/${subColName}`,
                limit: 10
              },
              items: {}
            };

            const subSnapshot = await subCol.limit(10).get();
            const subTotalCount = (await subCol.count().get()).data().count;

            docData.subCollections[subColName]._metadata.totalCount = subTotalCount;
            docData.subCollections[subColName]._metadata.showing = subSnapshot.size;

            if (subTotalCount > 10) {
              docData.subCollections[subColName]._metadata.truncated = true;
              docData.subCollections[subColName]._metadata.message = `Showing first 10 of ${subTotalCount} items`;
            }

            for (const subDoc of subSnapshot.docs) {
              docData.subCollections[subColName].items[subDoc.id] = {
                id: subDoc.id,
                path: subDoc.ref.path,
                data: subDoc.data()
              };
            }
          }
        }

        result.subCollections[collectionName].items[doc.id] = docData;
      }
    }

    // Output as formatted JSON
    console.log(JSON.stringify(result, null, 2));

  } catch (error) {
    console.error(JSON.stringify({
      error: 'FIREBASE_ERROR',
      message: error.message
    }));
    process.exit(1);
  }
}

// Get client ID from command line argument
const clientId = process.argv[2];

if (!clientId) {
  console.error(JSON.stringify({
    error: 'MISSING_ARGUMENT',
    message: 'Client ID is required'
  }));
  process.exit(1);
}

fetchFullClient(clientId);
