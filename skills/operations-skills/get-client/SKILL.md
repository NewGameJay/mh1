---
name: get-client
description: |
  Fetch and display a Firestore client document by ID in a formatted markdown table.
  Use when asked to 'get client', 'view client info', 'lookup client',
  'show client data', or 'fetch client details'.
license: Proprietary
compatibility: [Firebase, Firestore]
metadata:
  author: mh1-engineering
  version: "1.0.0"
  status: active
  estimated_runtime: "<5s"
  max_cost: "$0.00"
  client_facing: false
  tags:
    - firebase
    - client
    - lookup
    - utility
allowed-tools: Read Shell
argument-hint: "[client-id]"
---

# Get Client Skill

Fetches and displays a Firestore client document by ID in a formatted markdown table.

## When to Use

Use this skill when you need to:
- View a client's Firestore document
- Look up client information by ID
- Check client data fields and values
- Verify client exists in the database

## Prerequisites

Ensure the `GOOGLE_APPLICATION_CREDENTIALS` environment variable is set to the path of your Firebase service account credentials JSON file.

## Instructions

### Step 1: Parse Arguments
Extract the client ID from `$ARGUMENTS`. If no client ID is provided, display usage instructions:

```
Usage: /get-client [client-id]

Example: /get-client {CLIENT_ID}
```

### Step 2: Fetch Client Document

**IMPORTANT**: Before running the script for the first time, ensure dependencies are installed:
- Run `npm install` in the `skills/get-client` directory

Use the Bash tool to execute the custom Node.js script:
```bash
cd "skills/get-client" && node get-client.js {client_id}
```

The script will output JSON with one of the following structures:

**Success:**
```json
{
  "id": "client_id",
  "path": "clients/client_id",
  "data": { ... }
}
```

**Error:**
```json
{
  "error": "NOT_FOUND" | "MISSING_ARGUMENT" | "FIREBASE_ERROR" | "CONFIG_ERROR",
  "message": "Error description"
}
```

Parse the JSON output and handle errors appropriately.

### Step 3: Format Output as Markdown Table
Create a formatted markdown table with the following structure:

```markdown
## Client: {displayName or name}

| Field | Value |
|-------|-------|
| **Document ID** | {document_id} |
| **Path** | clients/{document_id} |
| {field_name} | {field_value} |
...
```

**Formatting rules**:
- Show Document ID and Path at the top for reference
- Display all top-level fields from the document
- For nested objects, display `[Object]` to keep the table clean
- For arrays, display `[Array with N items]`
- Format ISO date strings as `YYYY-MM-DD` for readability
- Display boolean values as `true` or `false`
- Handle null values by displaying `null`

### Step 4: Error Handling

**Case 1: Client Not Found**
```
Client not found: {client_id}

The client document does not exist in Firestore.

Example of a valid client ID: {CLIENT_ID}
```

**Case 2: Missing Argument**
```
Missing client ID

Usage: /get-client [client-id]

Example: /get-client {CLIENT_ID}
```

**Case 3: Firebase Connection Error**
```
Error connecting to Firebase: {error_message}

Please verify:
- GOOGLE_APPLICATION_CREDENTIALS environment variable is set correctly
- Service account credentials file exists at the specified path
- Firebase Admin dependencies are installed (run `npm install` in skills/get-client)
- Network connection is available
```

**Case 4: Configuration Error**
```
Configuration error: {error_message}

Please verify:
- GOOGLE_APPLICATION_CREDENTIALS environment variable is set
- The path points to a valid JSON credentials file
```

### Step 5: Add Footer Note
Include a note at the bottom of the output:

```
**Note**: This shows top-level document fields only. Sub-collections are not included.
```

## Example Output

```markdown
## Client: {displayName}

| Field | Value |
|-------|-------|
| **Document ID** | {document_id} |
| **Path** | clients/{document_id} |
| name | {name} |
| displayName | {displayName} |
| website | {website} |
| status | active |
| onboardedDate | 2026-01-19 |
| marketResearchCompleted | true |
| dataQuality | [Object] |

**Note**: This shows top-level document fields only. Sub-collections are not included.
```

## Fetch Full Client (with Sub-collections)

For a complete client dump including all sub-collections, use the CommonJS script:

```bash
cd "skills/get-client" && node fetch-full-client.cjs {client_id}
```

This will return the client document along with up to 10 items from each sub-collection, and nested sub-collections within those items.
