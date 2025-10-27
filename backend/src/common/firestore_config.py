# Firestore Configuration
import json
import os
from google.cloud.firestore import Client
from google.auth import default
from google.oauth2 import service_account

def get_firestore_credentials():
    """Load Firestore credentials from environment variable or service account key file."""
    # Try to load from service account key file first
    service_account_key_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
    if service_account_key_path and os.path.exists(service_account_key_path):
        return service_account.Credentials.from_service_account_file(service_account_key_path)
    
    # Try to load from environment variables
    credentials_dict_json = os.getenv('FIRESTORE_CREDENTIALS')
    if credentials_dict_json:
        credentials_dict = json.loads(credentials_dict_json)
        return service_account.Credentials.from_service_account_info(credentials_dict)
    
    # Fallback: try to load from default location
    default_key_path = 'service-account-key.json'
    if os.path.exists(default_key_path):
        return service_account.Credentials.from_service_account_file(default_key_path)
    
    # For Cloud Run: use default credentials
    try:
        credentials, project = default()
        return credentials
    except Exception as e:
        # Only raise error if we're in development and no credentials are found
        raise ValueError(
            "Firestore credentials not found. Please set GOOGLE_APPLICATION_CREDENTIALS environment variable "
            "or place service-account-key.json in the backend directory. "
            "See config.env.example for more details."
        )

# Create credentials object
try:
    FIRESTORE_CREDENTIALS = get_firestore_credentials()
except ValueError as e:
    # In Cloud Run, credentials will be obtained lazily
    FIRESTORE_CREDENTIALS = None

# Project Configuration
PROJECT_ID = "prompt-firewall-mvp"
DATABASE_ID = "(default)"
