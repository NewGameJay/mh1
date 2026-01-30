#!/usr/bin/env python3
"""
MH-1 to Firebase Migration Script

Migrates voice contracts, context docs, brand-visual docs, and campaigns
from local MH-1-Platform files to Firebase Firestore and Storage.

Usage:
    python scripts/migrate_mh1_to_firebase.py [--dry-run] [--client-id CLIENT_ID]

Requirements:
    pip install firebase-admin python-dotenv
"""

import argparse
import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('migration.log')
    ]
)
logger = logging.getLogger(__name__)

# Try to import Firebase, but allow dry-run without it
try:
    import firebase_admin
    from firebase_admin import credentials, firestore, storage
    FIREBASE_AVAILABLE = True
except ImportError:
    FIREBASE_AVAILABLE = False
    logger.warning("firebase-admin not installed. Only dry-run mode available.")

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    logger.warning("python-dotenv not installed. Using environment variables directly.")


class MigrationStats:
    """Track migration statistics."""
    
    def __init__(self):
        self.uploaded = 0
        self.skipped = 0
        self.failed = 0
        self.errors: List[str] = []
    
    def record_success(self, item: str):
        self.uploaded += 1
        logger.info(f"✓ Uploaded: {item}")
    
    def record_skip(self, item: str, reason: str):
        self.skipped += 1
        logger.info(f"⊘ Skipped: {item} ({reason})")
    
    def record_failure(self, item: str, error: str):
        self.failed += 1
        self.errors.append(f"{item}: {error}")
        logger.error(f"✗ Failed: {item} - {error}")
    
    def summary(self) -> str:
        return f"""
Migration Summary
=================
Uploaded: {self.uploaded}
Skipped:  {self.skipped}
Failed:   {self.failed}

{('Errors:' + chr(10) + chr(10).join(self.errors)) if self.errors else 'No errors.'}
"""


class FirebaseMigrator:
    """Handles migration of MH-1 data to Firebase."""
    
    def __init__(self, project_id: str, service_account_path: str, 
                 storage_bucket: str, dry_run: bool = False):
        self.project_id = project_id
        self.storage_bucket = storage_bucket
        self.dry_run = dry_run
        self.stats = MigrationStats()
        
        if not dry_run:
            if not FIREBASE_AVAILABLE:
                raise RuntimeError("firebase-admin required for live migration. Install with: pip install firebase-admin")
            
            # Initialize Firebase
            cred = credentials.Certificate(service_account_path)
            try:
                firebase_admin.initialize_app(cred, {
                    'storageBucket': storage_bucket
                })
            except ValueError:
                # Already initialized
                pass
            
            self.db = firestore.client()
            self.bucket = storage.bucket()
        else:
            self.db = None
            self.bucket = None
    
    def _upload_to_firestore(self, collection: str, doc_id: str, data: Dict[str, Any]) -> bool:
        """Upload a document to Firestore."""
        if self.dry_run:
            logger.info(f"[DRY-RUN] Would upload to {collection}/{doc_id}")
            return True
        
        try:
            self.db.collection(collection).document(doc_id).set(data)
            return True
        except Exception as e:
            logger.error(f"Firestore upload failed: {e}")
            return False
    
    def _upload_to_storage(self, local_path: Path, remote_path: str, 
                          content_type: str = 'application/octet-stream') -> bool:
        """Upload a file to Firebase Storage."""
        if self.dry_run:
            logger.info(f"[DRY-RUN] Would upload {local_path} to storage/{remote_path}")
            return True
        
        try:
            blob = self.bucket.blob(remote_path)
            blob.upload_from_filename(str(local_path), content_type=content_type)
            return True
        except Exception as e:
            logger.error(f"Storage upload failed: {e}")
            return False
    
    def migrate_voice_contracts(self, source_dir: Path, client_id: str) -> None:
        """Migrate voice contracts from context-data directory."""
        logger.info(f"\n{'='*60}")
        logger.info("Migrating Voice Contracts")
        logger.info('='*60)
        
        if not source_dir.exists():
            logger.warning(f"Source directory not found: {source_dir}")
            return
        
        for json_file in source_dir.glob("voice_contract*.json"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Determine founder ID from filename or data
                if 'founderId' in data:
                    founder_id = data['founderId']
                elif '_chris_toy' in json_file.name:
                    founder_id = 'chris-toy'
                elif '_raaja_nemani' in json_file.name:
                    founder_id = 'raaja-nemani'
                else:
                    founder_id = 'default'
                
                # Add migration metadata
                data['_migrated'] = {
                    'sourceFile': str(json_file.name),
                    'migratedAt': datetime.utcnow().isoformat(),
                    'migratedBy': 'migrate_mh1_to_firebase.py'
                }
                
                # Upload to Firestore
                doc_path = f"clients/{client_id}/voiceContracts"
                doc_id = founder_id
                
                if self._upload_to_firestore(doc_path, doc_id, data):
                    self.stats.record_success(f"voice_contract: {founder_id}")
                else:
                    self.stats.record_failure(f"voice_contract: {founder_id}", "Firestore upload failed")
                    
            except json.JSONDecodeError as e:
                self.stats.record_failure(str(json_file), f"Invalid JSON: {e}")
            except Exception as e:
                self.stats.record_failure(str(json_file), str(e))
        
        # Also migrate context_bundle.json if it exists
        bundle_file = source_dir / "context_bundle.json"
        if bundle_file.exists():
            try:
                with open(bundle_file, 'r', encoding='utf-8') as f:
                    bundle_data = json.load(f)
                
                bundle_data['_migrated'] = {
                    'sourceFile': 'context_bundle.json',
                    'migratedAt': datetime.utcnow().isoformat(),
                    'migratedBy': 'migrate_mh1_to_firebase.py'
                }
                
                if self._upload_to_firestore(f"clients/{client_id}/context", "bundle", bundle_data):
                    self.stats.record_success("context_bundle")
                else:
                    self.stats.record_failure("context_bundle", "Firestore upload failed")
                    
            except Exception as e:
                self.stats.record_failure("context_bundle.json", str(e))
    
    def migrate_context_docs(self, source_dir: Path, client_id: str) -> None:
        """Migrate context documents (audience, brand, competitive, etc.)."""
        logger.info(f"\n{'='*60}")
        logger.info("Migrating Context Documents")
        logger.info('='*60)
        
        if not source_dir.exists():
            logger.warning(f"Source directory not found: {source_dir}")
            return
        
        for md_file in source_dir.glob("*.md"):
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                doc_name = md_file.stem  # e.g., 'audience', 'brand'
                
                doc_data = {
                    'name': doc_name,
                    'content': content,
                    'format': 'markdown',
                    'category': 'context',
                    '_migrated': {
                        'sourceFile': str(md_file.name),
                        'migratedAt': datetime.utcnow().isoformat(),
                        'migratedBy': 'migrate_mh1_to_firebase.py'
                    }
                }
                
                if self._upload_to_firestore(f"clients/{client_id}/context", doc_name, doc_data):
                    self.stats.record_success(f"context: {doc_name}")
                else:
                    self.stats.record_failure(f"context: {doc_name}", "Firestore upload failed")
                    
            except Exception as e:
                self.stats.record_failure(str(md_file), str(e))
    
    def migrate_brand_visual(self, source_dir: Path, client_id: str) -> None:
        """Migrate brand-visual documents."""
        logger.info(f"\n{'='*60}")
        logger.info("Migrating Brand Visual Documents")
        logger.info('='*60)
        
        if not source_dir.exists():
            logger.warning(f"Source directory not found: {source_dir}")
            return
        
        for md_file in source_dir.glob("*.md"):
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                doc_name = md_file.stem  # e.g., 'colors', 'typography'
                
                doc_data = {
                    'name': doc_name,
                    'content': content,
                    'format': 'markdown',
                    'category': 'brand-visual',
                    '_migrated': {
                        'sourceFile': str(md_file.name),
                        'migratedAt': datetime.utcnow().isoformat(),
                        'migratedBy': 'migrate_mh1_to_firebase.py'
                    }
                }
                
                if self._upload_to_firestore(f"clients/{client_id}/brandVisual", doc_name, doc_data):
                    self.stats.record_success(f"brand-visual: {doc_name}")
                else:
                    self.stats.record_failure(f"brand-visual: {doc_name}", "Firestore upload failed")
                    
            except Exception as e:
                self.stats.record_failure(str(md_file), str(e))
    
    def migrate_campaigns(self, source_dir: Path, client_id: str) -> None:
        """Migrate campaign data including posts and calendars."""
        logger.info(f"\n{'='*60}")
        logger.info("Migrating Campaigns")
        logger.info('='*60)
        
        if not source_dir.exists():
            logger.warning(f"Source directory not found: {source_dir}")
            return
        
        for campaign_dir in source_dir.iterdir():
            if not campaign_dir.is_dir():
                continue
            
            campaign_name = campaign_dir.name
            logger.info(f"\nProcessing campaign: {campaign_name}")
            
            try:
                # Create campaign document with metadata
                campaign_data = {
                    'name': campaign_name,
                    'status': 'migrated',
                    'createdAt': datetime.utcnow().isoformat(),
                    '_migrated': {
                        'sourceDir': str(campaign_dir.name),
                        'migratedAt': datetime.utcnow().isoformat(),
                        'migratedBy': 'migrate_mh1_to_firebase.py'
                    }
                }
                
                # Look for final calendar
                calendar_files = list(campaign_dir.glob("*CALENDAR*.json"))
                if calendar_files:
                    calendar_file = calendar_files[0]
                    with open(calendar_file, 'r', encoding='utf-8') as f:
                        campaign_data['calendar'] = json.load(f)
                
                # Look for final posts
                final_posts_files = list(campaign_dir.glob("final-*.json"))
                if final_posts_files:
                    posts_file = final_posts_files[0]
                    with open(posts_file, 'r', encoding='utf-8') as f:
                        campaign_data['finalPosts'] = json.load(f)
                
                # Look for QA report
                qa_files = list(campaign_dir.glob("qa-*.json"))
                if qa_files:
                    qa_file = qa_files[0]
                    with open(qa_file, 'r', encoding='utf-8') as f:
                        campaign_data['qaReport'] = json.load(f)
                
                # Upload campaign document
                if self._upload_to_firestore(f"clients/{client_id}/campaigns", campaign_name, campaign_data):
                    self.stats.record_success(f"campaign: {campaign_name}")
                else:
                    self.stats.record_failure(f"campaign: {campaign_name}", "Firestore upload failed")
                
                # Upload individual batch posts
                posts_dir = campaign_dir / "posts"
                if posts_dir.exists():
                    for batch_file in posts_dir.glob("*.json"):
                        try:
                            with open(batch_file, 'r', encoding='utf-8') as f:
                                batch_data = json.load(f)
                            
                            batch_name = batch_file.stem
                            batch_doc = {
                                'campaignId': campaign_name,
                                'batchName': batch_name,
                                'posts': batch_data,
                                '_migrated': {
                                    'sourceFile': str(batch_file.name),
                                    'migratedAt': datetime.utcnow().isoformat()
                                }
                            }
                            
                            if self._upload_to_firestore(
                                f"clients/{client_id}/campaigns/{campaign_name}/batches",
                                batch_name,
                                batch_doc
                            ):
                                self.stats.record_success(f"batch: {campaign_name}/{batch_name}")
                            else:
                                self.stats.record_failure(f"batch: {batch_name}", "Upload failed")
                                
                        except Exception as e:
                            self.stats.record_failure(str(batch_file), str(e))
                
                # Upload source data to Storage
                source_data_dir = campaign_dir / "source-data"
                if source_data_dir.exists():
                    for source_file in source_data_dir.glob("*.json"):
                        storage_path = f"clients/{client_id}/campaigns/{campaign_name}/source-data/{source_file.name}"
                        if self._upload_to_storage(source_file, storage_path, 'application/json'):
                            self.stats.record_success(f"source-data: {source_file.name}")
                        else:
                            self.stats.record_failure(f"source-data: {source_file.name}", "Storage upload failed")
                            
            except Exception as e:
                self.stats.record_failure(f"campaign: {campaign_name}", str(e))
    
    def run_full_migration(self, mh1_root: Path, client_id: str) -> MigrationStats:
        """Run the complete migration process."""
        logger.info(f"""
╔══════════════════════════════════════════════════════════════╗
║         MH-1 to Firebase Migration                          ║
║         Client: {client_id:<44}║
║         Mode: {'DRY-RUN' if self.dry_run else 'LIVE':<47}║
╚══════════════════════════════════════════════════════════════╝
""")
        
        # Migrate voice contracts
        context_data_dir = mh1_root / "context-data"
        self.migrate_voice_contracts(context_data_dir, client_id)
        
        # Migrate context documents
        context_dir = mh1_root / "context"
        self.migrate_context_docs(context_dir, client_id)
        
        # Migrate brand-visual documents
        brand_visual_dir = mh1_root / "brand-visual"
        self.migrate_brand_visual(brand_visual_dir, client_id)
        
        # Migrate campaigns
        campaigns_dir = mh1_root / "campaigns"
        self.migrate_campaigns(campaigns_dir, client_id)
        
        logger.info(self.stats.summary())
        return self.stats


def main():
    parser = argparse.ArgumentParser(
        description="Migrate MH-1 data to Firebase",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Dry run (no actual uploads)
  python scripts/migrate_mh1_to_firebase.py --dry-run

  # Full migration
  python scripts/migrate_mh1_to_firebase.py --client-id marketerhire

  # Custom source directory
  python scripts/migrate_mh1_to_firebase.py --source ./MH-1-Platform/MH-1 --client-id marketerhire
"""
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Simulate migration without uploading'
    )
    
    parser.add_argument(
        '--client-id',
        default='mh1',
        help='Client ID for Firebase collection paths (default: mh1)'
    )
    
    parser.add_argument(
        '--source',
        type=Path,
        default=None,
        help='Path to MH-1 data directory (default: ./MH-1-Platform/MH-1)'
    )
    
    args = parser.parse_args()
    
    # Determine source directory
    if args.source:
        mh1_root = args.source
    else:
        # Try to find MH-1 directory
        script_dir = Path(__file__).parent.parent
        mh1_root = script_dir / "MH-1-Platform" / "MH-1"
        
        if not mh1_root.exists():
            # Try current directory
            mh1_root = Path.cwd() / "MH-1-Platform" / "MH-1"
    
    if not mh1_root.exists():
        logger.error(f"MH-1 source directory not found: {mh1_root}")
        logger.error("Use --source to specify the path to MH-1 data directory")
        sys.exit(1)
    
    logger.info(f"Source directory: {mh1_root}")
    
    # Get Firebase configuration from environment
    project_id = os.getenv('FIREBASE_PROJECT_ID', 'moe-platform-479917')
    service_account_path = os.getenv('SERVICE_ACCOUNT_KEY_PATH', '')
    storage_bucket = os.getenv('FIREBASE_STORAGE_BUCKET', f'{project_id}.firebasestorage.app')
    
    if not args.dry_run and not service_account_path:
        logger.error("SERVICE_ACCOUNT_KEY_PATH environment variable required for live migration")
        logger.error("Set it in .env file or use --dry-run to simulate")
        sys.exit(1)
    
    # Run migration
    try:
        migrator = FirebaseMigrator(
            project_id=project_id,
            service_account_path=service_account_path,
            storage_bucket=storage_bucket,
            dry_run=args.dry_run
        )
        
        stats = migrator.run_full_migration(mh1_root, args.client_id)
        
        # Exit with error code if there were failures
        if stats.failed > 0:
            sys.exit(1)
            
    except Exception as e:
        logger.exception(f"Migration failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
