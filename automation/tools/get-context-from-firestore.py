#!/usr/bin/env python3

"""
Download Context Files from Firebase Storage

This script:
1. Reads config to get Collection (defaults to 'clients') and Client ID
2. Queries Firestore to get the client's `name` property
3. Downloads all files from Firebase Storage at clients/{name}/
4. Saves them to the local context/ directory

Usage: python tools/get-context-from-firestore.py
"""

import os
import re
import sys
from pathlib import Path

import firebase_admin
from firebase_admin import credentials, firestore, storage

# Paths
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
CONFIG_PATH = PROJECT_ROOT / 'config.md'
CONTEXT_DIR = PROJECT_ROOT / 'context'


def load_config() -> dict:
    """Load configuration from config.md"""
    if not CONFIG_PATH.exists():
        raise FileNotFoundError(f'Config file not found: {CONFIG_PATH}')

    content = CONFIG_PATH.read_text(encoding='utf-8')

    config = {}

    # Parse Service Account
    match = re.search(r'\*\*Service Account:\*\*\s*`([^`]+)`', content)
    if match:
        config['service_account'] = match.group(1)

    # Parse Collection (defaults to 'clients' for consistency)
    match = re.search(r'\*\*Collection:\*\*\s*`([^`]+)`', content)
    if match:
        config['collection'] = match.group(1)
    else:
        config['collection'] = 'clients'  # Default

    # Parse Client ID
    match = re.search(r'\*\*Client ID:\*\*\s*`([^`]+)`', content)
    if match:
        config['client_id'] = match.group(1)

    # Validate required fields
    required = ['service_account', 'collection', 'client_id']
    missing = [f for f in required if f not in config]
    if missing:
        raise ValueError(f'Missing config fields: {", ".join(missing)}')

    return config


def initialize_firebase(service_account_file: str):
    """Initialize Firebase Admin SDK with Storage bucket"""
    service_account_path = PROJECT_ROOT / service_account_file
    if not service_account_path.exists():
        raise FileNotFoundError(f'Service account file not found: {service_account_path}')

    cred = credentials.Certificate(str(service_account_path))

    # Extract project ID from service account for storage bucket
    import json
    with open(service_account_path) as f:
        sa_data = json.load(f)
    project_id = sa_data.get('project_id')

    firebase_admin.initialize_app(cred, {
        'storageBucket': f'{project_id}.firebasestorage.app'
    })

    db = firestore.client()
    bucket = storage.bucket()

    return db, bucket


def get_client_name(db, collection: str, client_id: str) -> str:
    """Get the client's name from Firestore clients collection"""
    print(f'Fetching client data from {collection}/{client_id}...')

    doc_ref = db.collection(collection).document(client_id)
    doc = doc_ref.get()

    if not doc.exists:
        raise ValueError(f'Client document not found: {collection}/{client_id}')

    data = doc.to_dict()
    client_name = data.get('name')

    if not client_name:
        raise ValueError(f'Client document missing "name" field: {collection}/{client_id}')

    display_name = data.get('displayName', client_name)
    print(f'Found client: {display_name} (name: {client_name})\n')

    return client_name


def ensure_directory_exists(file_path: Path) -> bool:
    """Ensure directory exists, creating it if necessary"""
    directory = file_path.parent
    if not directory.exists():
        directory.mkdir(parents=True, exist_ok=True)
        return True
    return False


def download_context_files(bucket, client_name: str):
    """Download all context files from Firebase Storage"""
    storage_prefix = f'clients/{client_name}/'
    print(f'Listing files from Storage: {storage_prefix}')

    blobs = list(bucket.list_blobs(prefix=storage_prefix))

    # Filter out directory placeholders (blobs ending with /)
    files = [b for b in blobs if not b.name.endswith('/')]

    if not files:
        print(f'No files found in Storage at {storage_prefix}')
        return None

    print(f'Found {len(files)} files\n')

    results = {
        'success': [],
        'failed': [],
        'directories_created': set()
    }

    for blob in files:
        # Extract relative path (remove clients/{name}/ prefix)
        relative_path = blob.name[len(storage_prefix):]

        if not relative_path:
            continue

        local_path = CONTEXT_DIR / relative_path

        try:
            # Ensure directory exists
            dir_created = ensure_directory_exists(local_path)
            if dir_created:
                results['directories_created'].add(str(local_path.parent))

            # Check if file already exists
            file_exists = local_path.exists()

            # Download the file content
            content = blob.download_as_text(encoding='utf-8')

            # Write the file
            local_path.write_text(content, encoding='utf-8')

            results['success'].append({
                'blob_name': blob.name,
                'relative_path': relative_path,
                'content_length': len(content),
                'overwritten': file_exists
            })

            status = '~' if file_exists else '+'
            action = 'Updated' if file_exists else 'Created'
            print(f'{status} {action}: {relative_path} ({len(content):,} chars)')

        except Exception as error:
            results['failed'].append({
                'blob_name': blob.name,
                'relative_path': relative_path,
                'error': str(error)
            })
            print(f'Failed: {relative_path} - {error}')

    return results


def main():
    """Main execution"""
    print('============================================')
    print('FIREBASE STORAGE CONTEXT DOWNLOAD')
    print('============================================\n')

    # Load config
    config = load_config()
    collection = config['collection']
    client_id = config['client_id']

    print(f'Config loaded from: {CONFIG_PATH.name}')
    print(f'  Collection: {collection}')
    print(f'  Client ID: {client_id}\n')

    # Initialize Firebase
    db, bucket = initialize_firebase(config['service_account'])

    # Get client name from Firestore
    client_name = get_client_name(db, collection, client_id)

    # Ensure context directory exists
    if not CONTEXT_DIR.exists():
        CONTEXT_DIR.mkdir(parents=True, exist_ok=True)
        print(f'Created context directory: {CONTEXT_DIR}\n')

    # Download files from Storage
    results = download_context_files(bucket, client_name)

    if not results or (len(results['success']) == 0 and len(results['failed']) == 0):
        sys.exit(0)

    overwritten = len([r for r in results['success'] if r['overwritten']])
    created = len([r for r in results['success'] if not r['overwritten']])
    total_chars = sum(r['content_length'] for r in results['success'])

    print('\n============================================')
    print('DOWNLOAD COMPLETE')
    print('============================================')
    print(f'Client: {client_name}')
    print(f'Source: clients/{client_name}/')
    print(f'Output: {CONTEXT_DIR}/\n')

    print(f'Successfully saved: {len(results["success"])}')
    print(f'   - New files created: {created}')
    print(f'   - Files updated: {overwritten}')

    if results['directories_created']:
        print('\nDirectories created:')
        for directory in results['directories_created']:
            rel_path = os.path.relpath(directory, os.getcwd())
            print(f'   - {rel_path}/')

    if results['failed']:
        print(f'\nFailed: {len(results["failed"])}')
        for f in results['failed']:
            path_or_name = f.get('relative_path') or f['blob_name']
            print(f'   - {path_or_name}: {f["error"]}')

    print(f'\nTotal content downloaded: {total_chars:,} characters')
    print('============================================')

    sys.exit(1 if results['failed'] else 0)


if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        print(f'Fatal error: {error}')
        sys.exit(1)
