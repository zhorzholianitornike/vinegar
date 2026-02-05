"""
Configuration Helper for Railway Deployment
============================================
Handles Google Cloud credentials loading for Railway environment.
Supports multiple methods of providing credentials.
"""

import os
import json
import base64
from pathlib import Path


def setup_google_credentials():
    """
    Setup Google Cloud credentials for Railway deployment.

    Supports three methods:
    1. GOOGLE_APPLICATION_CREDENTIALS (file path) - for local development
    2. GOOGLE_APPLICATION_CREDENTIALS_JSON (JSON string) - for Railway
    3. GOOGLE_CREDENTIALS_BASE64 (base64 encoded JSON) - for Railway

    Returns:
        bool: True if credentials were set up successfully
    """

    # Method 1: File path (local development)
    if os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
        creds_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        if os.path.exists(creds_path):
            print(f"✓ Using Google credentials from file: {creds_path}")
            return True
        else:
            print(f"⚠️  Credentials file not found: {creds_path}")

    # Method 2: JSON string (Railway environment variable)
    creds_json_str = os.getenv("GOOGLE_APPLICATION_CREDENTIALS_JSON")
    if creds_json_str:
        try:
            # Validate it's valid JSON
            json.loads(creds_json_str)

            # Write to temporary file
            temp_creds_path = "/tmp/gcp-credentials.json"
            with open(temp_creds_path, "w") as f:
                f.write(creds_json_str)

            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = temp_creds_path
            print(f"✓ Google credentials loaded from GOOGLE_APPLICATION_CREDENTIALS_JSON")
            return True

        except json.JSONDecodeError as e:
            print(f"✗ Invalid JSON in GOOGLE_APPLICATION_CREDENTIALS_JSON: {e}")
            return False

    # Method 3: Base64 encoded JSON (Railway alternative)
    creds_base64 = os.getenv("GOOGLE_CREDENTIALS_BASE64")
    if creds_base64:
        try:
            # Decode base64
            creds_json = base64.b64decode(creds_base64).decode('utf-8')

            # Validate it's valid JSON
            json.loads(creds_json)

            # Write to temporary file
            temp_creds_path = "/tmp/gcp-credentials.json"
            with open(temp_creds_path, "w") as f:
                f.write(creds_json)

            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = temp_creds_path
            print(f"✓ Google credentials loaded from GOOGLE_CREDENTIALS_BASE64")
            return True

        except Exception as e:
            print(f"✗ Error decoding GOOGLE_CREDENTIALS_BASE64: {e}")
            return False

    # No credentials found
    print("⚠️  No Google Cloud credentials found!")
    print("Please set one of:")
    print("  - GOOGLE_APPLICATION_CREDENTIALS (file path)")
    print("  - GOOGLE_APPLICATION_CREDENTIALS_JSON (JSON string)")
    print("  - GOOGLE_CREDENTIALS_BASE64 (base64 encoded)")
    return False


def validate_environment():
    """
    Validate that all required environment variables are set.

    Returns:
        dict: Status of each required variable
    """
    required_vars = {
        "TELEGRAM_BOT_TOKEN": os.getenv("TELEGRAM_BOT_TOKEN"),
        "GOOGLE_GEMINI_API_KEY": os.getenv("GOOGLE_GEMINI_API_KEY"),
        "GOOGLE_CLOUD_PROJECT": os.getenv("GOOGLE_CLOUD_PROJECT"),
    }

    status = {}
    all_present = True

    for var, value in required_vars.items():
        if value:
            status[var] = "✓"
        else:
            status[var] = "✗"
            all_present = False

    return status, all_present


# Example usage
if __name__ == "__main__":
    print("=" * 50)
    print("Configuration Check")
    print("=" * 50 + "\n")

    # Setup credentials
    print("1. Setting up Google Cloud credentials...")
    creds_ok = setup_google_credentials()

    print("\n" + "=" * 50)
    print("2. Validating environment variables...")
    print("=" * 50 + "\n")

    status, all_ok = validate_environment()

    for var, state in status.items():
        print(f"{state} {var}")

    print("\n" + "=" * 50)

    if creds_ok and all_ok:
        print("✅ Configuration is complete!")
    else:
        print("⚠️  Configuration incomplete. Please check above.")

    print("=" * 50)
