# Clients Directory

**⚠️ This directory should remain EMPTY.**

All client data is stored in **Firebase**, not locally.

## Why?

Per `COMPONENT_MAP.md`:
- Client data is the source of truth in Firebase
- Local files are only for system templates and configuration
- This prevents data sync issues and ensures single source of truth

## Where Is Client Data?

```
Firebase: clients/{clientId}/
├── metadata/
├── context/
├── founders/
├── signals/
├── competitors/
└── modules/
    └── linkedin-ghostwriter/
        ├── assignment-briefs/
        └── posts/
```

## How to Access Client Data

1. Set active client in `inputs/active_client.md`
2. Use Firebase client library (`lib/firebase_client.py`)
3. Or use Node.js tools (`tools/get-client.js`)

## If You See Files Here

They were likely created in error. Client data should be:
1. Moved to Firebase
2. Or deleted (if duplicates exist in Firebase)

Do NOT store client-specific data in this folder.
