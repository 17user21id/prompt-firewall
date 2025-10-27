#!/usr/bin/env python3
"""
Utility script to delete all tenants and their data from the system.
This will delete all data associated with tenants in the correct order.

WARNING: This is a destructive operation. Use with caution!
"""

import sys
import os
import time
from typing import Dict, List, Optional

# Add src to path so we can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.store.firestore.tenants import TenantStore
from src.common.firestore_config import FIRESTORE_CREDENTIALS, PROJECT_ID
from google.cloud import firestore


def get_tenant_data_stats(tenant_id: str, db) -> Dict[str, int]:
    """Get statistics about data for a tenant."""
    stats = {
        'logs': 0,
        'rules': 0,
        'prompts': 0
    }
    
    subcollections = ['logs', 'rules', 'prompts']
    for subcollection in subcollections:
        ref = db.collection('tenants').document(tenant_id).collection(subcollection)
        try:
            docs = list(ref.stream())
            stats[subcollection] = len(docs)
        except Exception as e:
            print(f"  Warning: Could not get stats for {subcollection}: {e}")
    
    return stats


def delete_subcollection_batch(collection_ref, batch_size=500):
    """
    Delete all documents in a subcollection using batched operations.
    This is more efficient than deleting one by one.
    """
    deleted_count = 0
    
    while True:
        # Get a batch of documents
        docs = collection_ref.limit(batch_size).stream()
        batch = []
        doc_count = 0
        
        for doc in docs:
            batch.append(doc)
            doc_count += 1
        
        if doc_count == 0:
            break
        
        # Delete in batch
        for doc in batch:
            doc.reference.delete()
            deleted_count += 1
        
        # If we got less than batch_size, we're done
        if doc_count < batch_size:
            break
    
    return deleted_count


def delete_all_tenant_data(tenant_id: str, db, tenant_name: str = None) -> Dict[str, int]:
    """
    Delete all data associated with a tenant.
    Returns a dictionary with counts of deleted items.
    """
    deleted_counts = {
        'logs': 0,
        'rules': 0,
        'prompts': 0
    }
    
    subcollections = ['logs', 'rules', 'prompts']
    
    for subcollection in subcollections:
        try:
            collection_ref = db.collection('tenants').document(tenant_id).collection(subcollection)
            count = delete_subcollection_batch(collection_ref)
            deleted_counts[subcollection] = count
            
            if count > 0:
                print(f"  ✓ Deleted {count} {subcollection}")
        except Exception as e:
            print(f"  ⚠️  Error deleting {subcollection}: {e}")
    
    return deleted_counts


def delete_all_tenants():
    """Delete all tenants and their associated data."""
    
    # Initialize Firestore and TenantStore
    print("Initializing Firestore connection...")
    db = firestore.Client(project=PROJECT_ID, credentials=FIRESTORE_CREDENTIALS)
    tenant_store = TenantStore()
    
    # Get all tenants
    print("Fetching all tenants...")
    all_tenants = tenant_store.get_all_tenants()
    
    if not all_tenants:
        print("No tenants found in the system.")
        return
    
    print(f"Found {len(all_tenants)} tenant(s).")
    
    # Show summary of data to be deleted
    print("\nData Summary:")
    print("=" * 80)
    total_stats = {'logs': 0, 'rules': 0, 'prompts': 0}
    
    for tenant in all_tenants:
        tenant_id = tenant.get('tenant_id')
        tenant_name = tenant.get('name', 'Unknown')
        
        if tenant_id:
            stats = get_tenant_data_stats(tenant_id, db)
            total_stats['logs'] += stats['logs']
            total_stats['rules'] += stats['rules']
            total_stats['prompts'] += stats['prompts']
            print(f"{tenant_name}: {stats['logs']} logs, {stats['rules']} rules, {stats['prompts']} prompts")
    
    print("=" * 80)
    print(f"Total: {total_stats['logs']} logs, {total_stats['rules']} rules, {total_stats['prompts']} prompts")
    print(f"Tenants to delete: {len(all_tenants)}")
    
    # Ask for confirmation
    print("\n" + "=" * 80)
    response = input(f"⚠️  WARNING: This will DELETE ALL {len(all_tenants)} tenant(s) and their data.\n\nContinue? (yes/no): ")
    
    if response.lower() != 'yes':
        print("\nOperation cancelled.")
        return
    
    print("\nStarting deletion process...")
    print("=" * 80)
    
    deleted_count = 0
    error_count = 0
    tenant_deletion_errors = []
    
    # Step 1: Delete all data first (logs, rules, prompts)
    print("\n[STEP 1] Deleting all tenant data (logs, rules, prompts)...")
    
    for i, tenant in enumerate(all_tenants, 1):
        tenant_id = tenant.get('tenant_id')
        tenant_name = tenant.get('name', 'Unknown')
        
        if not tenant_id:
            print(f"⚠️  [{i}/{len(all_tenants)}] Skipping tenant without ID: {tenant}")
            continue
        
        try:
            print(f"\n[{i}/{len(all_tenants)}] Processing: {tenant_name} (ID: {tenant_id[:8]}...)")
            
            # Delete all subcollections
            deleted_data = delete_all_tenant_data(tenant_id, db, tenant_name)
            
            if sum(deleted_data.values()) > 0:
                print(f"  ✓ All data deleted for {tenant_name}")
            else:
                print(f"  ℹ️  No data found for {tenant_name}")
            
            deleted_count += 1
            
        except Exception as e:
            error_count += 1
            print(f"  ✗ Error processing tenant {tenant_name}: {e}")
            tenant_deletion_errors.append({
                'tenant': tenant_name,
                'tenant_id': tenant_id,
                'error': str(e)
            })
    
    # Step 2: Delete tenant documents
    print(f"\n[STEP 2] Deleting tenant documents...")
    
    tenant_docs_deleted = 0
    for i, tenant in enumerate(all_tenants, 1):
        tenant_id = tenant.get('tenant_id')
        tenant_name = tenant.get('name', 'Unknown')
        
        if not tenant_id:
            continue
        
        try:
            tenant_ref = db.collection('tenants').document(tenant_id)
            tenant_ref.delete()
            tenant_docs_deleted += 1
            print(f"  [{i}/{len(all_tenants)}] ✓ Deleted tenant document: {tenant_name}")
            
        except Exception as e:
            print(f"  [{i}/{len(all_tenants)}] ✗ Error deleting tenant document {tenant_name}: {e}")
            error_count += 1
    
    # Final Summary
    print(f"\n{'='*80}")
    print(f"DELETION SUMMARY")
    print(f"{'='*80}")
    print(f"✓ Tenants processed: {deleted_count}")
    print(f"✓ Tenant documents deleted: {tenant_docs_deleted}")
    print(f"✗ Errors: {error_count}")
    print(f"Total tenants: {len(all_tenants)}")
    
    if tenant_deletion_errors:
        print(f"\nTenants with errors:")
        for error in tenant_deletion_errors:
            print(f"  - {error['tenant']}: {error['error']}")
    
    print(f"{'='*80}")
    
    if deleted_count == len(all_tenants) and error_count == 0:
        print("\n✅ All tenants and data deleted successfully!")
    elif error_count > 0:
        print(f"\n⚠️  Completed with {error_count} error(s). See details above.")
    else:
        print(f"\n⚠️  Some tenants may not have been processed correctly.")


def list_all_tenants():
    """List all tenants without deleting them."""
    tenant_store = TenantStore()
    all_tenants = tenant_store.get_all_tenants()
    
    if not all_tenants:
        print("No tenants found in the system.")
        return
    
    # Initialize Firestore to get data counts
    db = firestore.Client(project=PROJECT_ID, credentials=FIRESTORE_CREDENTIALS)
    
    print(f"\nFound {len(all_tenants)} tenant(s):")
    print(f"{'='*100}")
    print(f"{'Name':<30} {'Tenant ID':<37} {'Logs':<8} {'Rules':<8} {'Prompts':<8} {'Status':<10}")
    print(f"{'='*100}")
    
    total_stats = {'logs': 0, 'rules': 0, 'prompts': 0}
    
    for tenant in all_tenants:
        tenant_id = tenant.get('tenant_id', 'N/A')
        name = tenant.get('name', 'Unknown')
        status = tenant.get('status', 'active')
        
        # Get data counts
        if tenant_id != 'N/A':
            stats = get_tenant_data_stats(tenant_id, db)
            logs = stats['logs']
            rules = stats['rules']
            prompts = stats['prompts']
            total_stats['logs'] += logs
            total_stats['rules'] += rules
            total_stats['prompts'] += prompts
        else:
            logs = rules = prompts = 0
        
        print(f"{name:<30} {tenant_id:<37} {logs:<8} {rules:<8} {prompts:<8} {status:<10}")
    
    print(f"{'='*100}")
    print(f"{'TOTAL':<30} {'':<37} {total_stats['logs']:<8} {total_stats['rules']:<8} {total_stats['prompts']:<8} {'':<10}")


def main():
    """Main function."""
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == 'list':
            list_all_tenants()
        elif command == 'delete':
            delete_all_tenants()
        else:
            print("Usage: python delete_all_tenants.py [list|delete]")
            print("  list   - List all tenants with data counts")
            print("  delete - Delete all tenants (with confirmation)")
    else:
        print("Tenant Management Utility")
        print("=" * 60)
        print("Usage: python delete_all_tenants.py [list|delete]")
        print()
        print("Commands:")
        print("  list   - List all tenants in the system with data counts")
        print("  delete - Delete all tenants and their data (requires confirmation)")
        print()
        print("Examples:")
        print("  python delete_all_tenants.py list")
        print("  python delete_all_tenants.py delete")
        print()
        print("Warning: The delete command will permanently remove all tenants")
        print("         and their associated data (logs, rules, prompts).")


if __name__ == '__main__':
    main()