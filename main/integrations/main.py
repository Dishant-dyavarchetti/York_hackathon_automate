from jira import JIRA
import os
from dotenv import load_dotenv
from openai import OpenAI
import json
import subprocess
import sys
from datetime import datetime
import requests

# Load environment variables from .env (assumes .env is in project root)
load_dotenv()

# Read credentials
JIRA_BASE_URL = os.getenv("JIRA_BASE_URL")
JIRA_EMAIL = os.getenv("JIRA_EMAIL")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPEN_WEATHER_API_KEY = os.getenv("OPEN_WEATHER_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama-3.3-70b-versatile"

# Check for missing values
if not all([JIRA_BASE_URL, JIRA_EMAIL, JIRA_API_TOKEN, OPENAI_API_KEY]):
    print("❌ Missing required environment variables. Check your .env file.")
    exit(1)

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

def get_project_base_path():
    """Get the base path where projects will be saved"""
    # Create a 'generated_projects' directory in the workspace root
    base_path = os.path.join(os.path.dirname(__file__), '..', '..', 'generated_projects')
    os.makedirs(base_path, exist_ok=True)
    return base_path

def create_project_structure(project_name):
    """Create the basic project structure"""
    try:
        # Get the full path for the project
        project_path = os.path.join(get_project_base_path(), project_name)
        print(f"\n📂 Creating project at: {project_path}")
        
        # Create main project directory
        os.makedirs(project_path, exist_ok=True)
        
        # Create common directories
        directories = [
            'src',
            'tests',
            'docs',
            'config',
            'static',
            'templates'
        ]
        
        for directory in directories:
            dir_path = os.path.join(project_path, directory)
            os.makedirs(dir_path, exist_ok=True)
            print(f"  └─ Created directory: {directory}")
            
        return project_path
    except Exception as e:
        print(f"❌ Error creating project structure: {e}")
        return None

def generate_application_code(ticket_description, ticket_summary, ticket_key):
    """
    Generate complete application code based on the ticket requirements using Groq Llama-3 API
    """
    try:
        # Get all available API keys from .env
        api_keys = {
            'OPEN_WEATHER_API_KEY': os.getenv('OPEN_WEATHER_API_KEY')
        }
        available_api_keys = {k: v for k, v in api_keys.items() if v is not None}

        # Create a robust, explicit prompt
        prompt = f"""
You are a senior software engineer. Generate a complete, working Python web application for the following Jira ticket:

Ticket Key: {ticket_key}
Summary: {ticket_summary}
Description: {ticket_description}

Available API Keys:
{json.dumps(available_api_keys, indent=2)}

## Requirements

- Use Flask (version 2.3.3) and Jinja2 (version 3.1.2)
- Load API keys from a `.env` file using `python-dotenv`
- Fetch real data from the required API (e.g., OpenWeather) using the API key
- Display the fetched data in the UI (not just a placeholder)
- Show clear error messages in the UI if the API call fails or the key is missing
- Include a `config.py` for loading/validating API keys
- Include a `.env` template with all required keys
- Include a `run.py` that sets up the virtual environment, installs dependencies, and runs the app
- List all dependencies in `requirements.txt`
- Include a `README.md` with setup and usage instructions

## Output Format

Return a JSON object with this structure:
{{
  "project_name": "project_{ticket_key.lower()}",
  "files": [
    {{"path": "src/main.py", "content": "<Flask app code that fetches and displays data>"}},
    {{"path": "src/templates/index.html", "content": "<HTML template with dynamic data and error display>"}},
    {{"path": "src/static/style.css", "content": "<CSS for modern, responsive UI>"}},
    {{"path": "config.py", "content": "<API key loading/validation code>"}},
    {{"path": ".env", "content": "# API Keys\\nOPEN_WEATHER_API_KEY=your_api_key_here"}},
    {{"path": "requirements.txt", "content": "Flask==2.3.3\\npython-dotenv==1.0.0\\nrequests==2.31.0\\nJinja2==3.1.2"}},
    {{"path": "run.py", "content": "<script to set up venv, install requirements, and run the app>"}},
    {{"path": "README.md", "content": "<setup and usage instructions>"}}
  ]
}}

- The Flask app must read the API key from the environment using `python-dotenv`.
- The main route must fetch data from the API and pass it to the template.
- The template must display the data or an error message if the fetch fails.
- The UI must be visually appealing and responsive.
- All files must be included in the output JSON.
- The app must run with `python run.py` and work out-of-the-box.

Respond ONLY with the JSON object, no extra text.
"""
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "model": GROQ_MODEL,
            "messages": [
                {"role": "system", "content": "You are a senior software engineer. Respond ONLY with the JSON object as described."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7
        }
        response = requests.post(GROQ_API_URL, headers=headers, json=data)
        response.raise_for_status()
        response_content = response.json()["choices"][0]["message"]["content"].strip()
        print("\n📄 RAW LLM RESPONSE:\n")
        print(response_content)
        import re
        # Remove code fences if present
        response_content_clean = re.sub(r'^```(?:json)?|```$', '', response_content.strip(), flags=re.MULTILINE).strip()
        try:
            project_data = json.loads(response_content_clean)
            return project_data
        except json.JSONDecodeError as e:
            print(f"\n❌ JSON Parse Error: {str(e)}")
            print("The response was not valid JSON. Please check the raw response above.")
            # Save the raw response to a file for debugging
            with open('llm_raw_response.txt', 'w', encoding='utf-8') as f:
                f.write(response_content)
            return None
    except Exception as e:
        print(f"\n❌ Error generating application code: {e}")
        return None

def create_application_files(project_data):
    """Create all the files for the application"""
    try:
        project_name = project_data["project_name"]
        
        # Create project structure and get the full path
        project_path = create_project_structure(project_name)
        if not project_path:
            return False
            
        print(f"\n📝 Creating files in project directory: {project_path}")
        
        # Create all files
        for file_info in project_data["files"]:
            file_path = os.path.join(project_path, file_info["path"])
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(file_info["content"])
            print(f"  └─ Created file: {file_info['path']}")
                
        return True
    except Exception as e:
        print(f"❌ Error creating application files: {e}")
        return False

def setup_virtual_environment(project_name):
    """Set up Python virtual environment and install requirements"""
    try:
        project_path = os.path.join(get_project_base_path(), project_name)
        venv_path = os.path.join(project_path, "venv")
        
        print(f"\n🔧 Setting up virtual environment at: {venv_path}")
        
        # Create virtual environment
        subprocess.run([sys.executable, "-m", "venv", venv_path], check=True)
        
        # Get the path to the virtual environment's pip
        if os.name == 'nt':  # Windows
            pip_path = os.path.join(venv_path, "Scripts", "pip")
        else:  # Unix/Linux
            pip_path = os.path.join(venv_path, "bin", "pip")
            
        # Install requirements
        print("  └─ Installing dependencies...")
        subprocess.run([pip_path, "install", "-r", os.path.join(project_path, "requirements.txt")], check=True)
        
        return True
    except Exception as e:
        print(f"❌ Error setting up virtual environment: {e}")
        return False

# Connect to Jira
try:
    jira = JIRA(
        server=JIRA_BASE_URL,
        basic_auth=(JIRA_EMAIL, JIRA_API_TOKEN)
    )
    print("✅ Connected to Jira!")
except Exception as e:
    print(f"❌ Failed to connect to Jira: {e}")
    exit(1)

# Fetch assigned tickets that are NOT in Done
jql_query = 'assignee = currentUser() AND statusCategory != Done ORDER BY updated DESC'
try:
    issues = jira.search_issues(jql_query, maxResults=10)

    if not issues:
        print("📭 No active tickets assigned to you.")
        exit(0)

    # Show selection menu
    print("\n📋 Select a Jira Ticket:\n")
    for idx, issue in enumerate(issues):
        print(f"{idx + 1}. {issue.key} - {issue.fields.summary} [Status: {issue.fields.status.name}]")

    # User picks ticket
    choice = int(input("\n🔎 Enter the number of the ticket you want to process: ")) - 1

    if choice < 0 or choice >= len(issues):
        print("❌ Invalid selection.")
        exit(1)

    selected_issue = issues[choice]
    print(f"\n✅ You selected: {selected_issue.key} - {selected_issue.fields.summary}")
    print("\n📝 Ticket Description:\n")
    print(selected_issue.fields.description or "(No description)")

    # Transition ticket to In Progress
    try:
        transitions = jira.transitions(selected_issue)
        in_progress_transition = next((t for t in transitions if t['name'].lower() == 'in progress'), None)
        if in_progress_transition:
            jira.transition_issue(selected_issue, in_progress_transition['id'])
            print(f"✅ Ticket {selected_issue.key} transitioned to In Progress.")
        else:
            print(f"❌ Could not find 'In Progress' transition for ticket {selected_issue.key}.")
    except Exception as e:
        print(f"❌ Error transitioning ticket: {e}")

    # Generate application code
    print("\n🤖 Generating application code...")
    project_data = generate_application_code(
        selected_issue.fields.description or "",
        selected_issue.fields.summary,
        selected_issue.key
    )
    
    if project_data:
        print("\n📁 Creating project structure and files...")
        if create_application_files(project_data):
            print("\n🔧 Setting up virtual environment and installing dependencies...")
            if setup_virtual_environment(project_data["project_name"]):
                project_path = os.path.join(get_project_base_path(), project_data["project_name"])
                print(f"\n✨ Successfully created application!")
                print(f"📂 Project location: {project_path}")
                print("\n📚 Please check the README.md file for setup and running instructions.")
            else:
                print("❌ Failed to set up virtual environment")
        else:
            print("❌ Failed to create application files")
    else:
        print("❌ Failed to generate application code")

except Exception as e:
    print(f"❌ Error fetching tickets: {e}")

