import os
import sys
from pathlib import Path

def check_credentials():
    """Check if required credential files and environment variables exist."""
    project_root = Path(__file__).parent.parent.parent
    credentials_path = project_root / "config" / "credentials.json"
    
    if not credentials_path.exists():
        print("Error: Google Sheets credentials file not found!")
        print(f"Please place your credentials.json file in: {credentials_path}")
        print("\nTo get credentials.json:")
        print("1. Go to Google Cloud Console")
        print("2. Create a project and enable Google Sheets API")
        print("3. Create service account credentials")
        print("4. Download JSON and rename to credentials.json")
        sys.exit(1)

    required_env_vars = ['GEMINI_API_KEY', 'SERPAPI_API_KEY']
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    
    if missing_vars:
        print("Error: Missing required environment variables:")
        for var in missing_vars:
            print(f"- {var}")
        sys.exit(1)
