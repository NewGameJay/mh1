# Get Client Skill

This skill fetches and displays Firestore client documents using a custom Node.js script.

## Setup

1. **Set environment variable**:
   ```bash
   export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/firebase-credentials.json"
   ```
   
   Or add to your `.env` file:
   ```
   GOOGLE_APPLICATION_CREDENTIALS=/path/to/your/firebase-credentials.json
   ```

2. **Install dependencies** (first time only):
   ```bash
   cd skills/get-client
   npm install
   ```

## Usage

```
/get-client [client-id]
```

Example:
```
/get-client {CLIENT_ID}
```

Where `{CLIENT_ID}` is the Firestore client document ID from `inputs/active_client.md`.

## Scripts

### get-client.js (ES Module)
Fetches a single client document and returns formatted JSON with timestamps converted to ISO strings.

```bash
node get-client.js <client-id>
```

### fetch-full-client.cjs (CommonJS)
Fetches a client document with all sub-collections (up to 10 items per collection) and nested sub-collections.

```bash
node fetch-full-client.cjs <client-id>
```

## Architecture

- **get-client.js**: Node.js ES module that uses Firebase Admin SDK to fetch documents
- **fetch-full-client.cjs**: CommonJS script for comprehensive client data including sub-collections
- **SKILL.md**: Instructions for Claude Code to execute and format results
- **package.json**: Node.js dependencies (firebase-admin)

## Output

The skill displays client information in a formatted markdown table with all top-level fields.

## Error Handling

The scripts handle four error cases:
- **MISSING_ARGUMENT**: No client ID provided
- **NOT_FOUND**: Client document doesn't exist
- **FIREBASE_ERROR**: Connection or authentication issues
- **CONFIG_ERROR**: Missing or invalid GOOGLE_APPLICATION_CREDENTIALS

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GOOGLE_APPLICATION_CREDENTIALS` | Yes | Path to Firebase service account JSON credentials file |
