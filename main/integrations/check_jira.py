from jira import JIRA
import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

# Load credentials
JIRA_BASE_URL = os.getenv("JIRA_BASE_URL")
JIRA_EMAIL = os.getenv("JIRA_EMAIL")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")

if not all([JIRA_BASE_URL, JIRA_EMAIL, JIRA_API_TOKEN]):
    print("❌ Missing environment variables. Check your .env file.")
    exit(1)

# Connect to Jira and verify identity
try:
    jira = JIRA(
        server=JIRA_BASE_URL,
        basic_auth=(JIRA_EMAIL, JIRA_API_TOKEN)
    )

    user = jira.current_user()
    myself = jira.user(user)

    print("✅ Jira connection successful!")
    print(f"👤 Authenticated as: {myself.displayName} ({myself.emailAddress})")

except Exception as e:
    print(f"❌ Jira connection failed: {e}")
