#!/usr/bin/env python3
"""
Test script to verify Firestore connection is working with the configured credentials.
"""

import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from google.cloud import firestore
from src.common.firestore_config import FIRESTORE_CREDENTIALS, PROJECT_ID

def test_firestore_connection():
    """Test the Firestore connection."""
    try:
        print("Testing Firestore connection...")
        print(f"Project ID: {PROJECT_ID}")
        print(f"Service Account Email: {FIRESTORE_CREDENTIALS.service_account_email}")
        
        # Initialize Firestore client
        db = firestore.Client(project=PROJECT_ID, credentials=FIRESTORE_CREDENTIALS)
        
        # Test basic connection by listing collections
        print("\nListing collections...")
        collections = db.collections()
        collection_names = [col.id for col in collections]
        
        if collection_names:
            print(f"Found collections: {collection_names}")
        else:
            print("No collections found (this is normal for a new project)")
        
        # Test creating a test document
        print("\nTesting document creation...")
        test_ref = db.collection('test').document('connection_test')
        test_ref.set({
            'message': 'Hello Firestore!',
            'timestamp': firestore.SERVER_TIMESTAMP,
            'test': True
        })
        print("✅ Test document created successfully")
        
        # Test reading the document
        print("\nTesting document retrieval...")
        doc = test_ref.get()
        if doc.exists:
            print(f"✅ Document retrieved: {doc.to_dict()}")
        else:
            print("❌ Document not found")
        
        # Clean up test document
        print("\nCleaning up test document...")
        test_ref.delete()
        print("✅ Test document deleted")
        
        print("\n🎉 Firestore connection test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Firestore connection test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_firestore_connection()
    sys.exit(0 if success else 1)
