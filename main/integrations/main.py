from jira import JIRA
import os
from dotenv import load_dotenv
from openai import OpenAI
import json
import subprocess
import sys
from datetime import datetime
import requests
import time
import webbrowser

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
You are a senior software engineer. Generate a complete, working Python web application based STRICTLY on the requirements outlined in the provided Jira ticket description. Focus on creating a functional application that addresses the specific task described in the ticket, such as fetching and displaying current location weather if that is the ticket's requirement.

IMPORTANT: If the ticket requires location-based functionality (like weather), you MUST implement geolocation using the browser's navigator.geolocation API. Do not rely on hardcoded locations or manual input unless specifically requested in the ticket.

Ticket Key: {ticket_key}
Summary: {ticket_summary}
Description: {ticket_description}

Available API Keys:
{json.dumps(available_api_keys, indent=2)}

## Requirements

- Implement the core functionality as described in the Jira ticket description.
- For location-based features (like weather), use the browser's navigator.geolocation API to get the user's current location.
- Use Flask (version 2.3.3) and Jinja2 (version 3.1.2) for the web application structure.
- Load necessary API keys from a `.env` file using `python-dotenv`.
- Fetch and display real data from any required API (e.g., OpenWeather) using the provided API key.
- Ensure the UI clearly displays fetched data or relevant error messages if API calls fail or keys are missing.
- Design and implement a modern, responsive, and visually appealing user interface and styling using HTML, CSS, and JavaScript as appropriate for the Flask template.
- Include a dot-env for loading/validating API keys.
- Directly access the API keys from the `.env` file.
- Include a gitignore of the files like .env,git-auto.py and folder like venv
- Include a `.env` template with all required keys mentioned in the ticket description.
- Include a `run.py` that sets up the virtual environment, installs dependencies, and runs the app.
- List all dependencies in `requirements.txt`.
- Include a `README.md` with setup and usage instructions.

## Output Format

Return a JSON object with this structure:
{{
  "project_name": "project_{ticket_key.lower()}",
  "files": [
    {{"path": "src/main.py", "content": "<Flask app code that fetches and displays data>"}},
    {{"path": "src/templates/index.html", "content": "<HTML template with dynamic data and error display>"}},
    {{"path": "src/static/style.css", "content": "<CSS for modern, responsive UI>"}},
    {{"path": "src/static/app.js", "content": "<JavaScript code for geolocation and dynamic updates>"}},
    {{"path": ".env", "content": "# API Keys\\nOPEN_WEATHER_API_KEY=your_api_key_here"}},
    {{"path": "requirements.txt", "content": "Flask==2.3.3\\npython-dotenv==1.0.0\\nrequests==2.31.0\\nJinja2==3.1.2"}},
    {{"path": "run.py", "content": "<script to set up venv, install requirements, and run the app>"}},
    {{"path": "README.md", "content": "<setup and usage instructions>"}}
  ]
}}

- The Flask app must read the API key from the environment using `python-dotenv`.
- The main route must fetch data from the API and pass it to the template.
- The template must display the data or an error message if the fetch fails.
- For location-based features, the JavaScript code must use navigator.geolocation to get the user's current location.
- The UI must be visually appealing and responsive as per the styling requirement.
- The CSS should be internal in the HTML and well made for better Styling
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
            python_path = os.path.join(venv_path, "Scripts", "python")
        else:  # Unix/Linux
            pip_path = os.path.join(venv_path, "bin", "pip")
            python_path = os.path.join(venv_path, "bin", "python")
            
        # Install requirements
        print("  └─ Installing dependencies...")
        subprocess.run([pip_path, "install", "-r", os.path.join(project_path, "requirements.txt")], check=True)
        
        return True, python_path
    except Exception as e:
        print(f"❌ Error setting up virtual environment: {e}")
        return False, None

def run_git_auto():
    """Run git-auto.py in a new terminal window"""
    try:
        # Get the absolute path to git-auto.py
        git_auto_path = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'git-auto.py'))
        # Get the path to venv in main directory
        venv_path = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'venv'))
        print(f"\n📂 Running git-auto.py from: {git_auto_path}")
        print(f"📂 Using virtual environment from: {venv_path}")
        
        if os.name == 'nt':  # Windows
            # Use start to open in new window with proper path handling and venv activation
            if os.path.exists(venv_path):
                activate_script = os.path.join(venv_path, 'Scripts', 'activate.bat')
                cmd = f'start cmd /k "{activate_script} && cd /d {os.path.dirname(git_auto_path)} && python {os.path.basename(git_auto_path)}"'
            else:
                print("❌ Virtual environment not found. Please create it first.")
                return False
            subprocess.Popen(cmd, shell=True)
        else:  # Unix/Linux
            # Use xterm or gnome-terminal with venv activation
            if os.path.exists(venv_path):
                activate_script = os.path.join(venv_path, 'bin', 'activate')
                if os.path.exists('/usr/bin/gnome-terminal'):
                    cmd = f'source {activate_script} && python3 {git_auto_path}'
                    subprocess.Popen(['gnome-terminal', '--', 'bash', '-c', cmd])
                else:
                    cmd = f'source {activate_script} && python3 {git_auto_path}'
                    subprocess.Popen(['xterm', '-e', cmd])
            else:
                print("❌ Virtual environment not found. Please create it first.")
                return False
        return True
    except Exception as e:
        print(f"❌ Error running git-auto.py: {e}")
        return False

def run_project(project_name, python_path):
    """Run the generated project"""
    try:
        project_path = os.path.join(get_project_base_path(), project_name)
        main_script = os.path.join(project_path, "src", "main.py")
        
        print(f"\n🚀 Running project at: {project_path}")
        
        # Run the project using the virtual environment's Python
        process = subprocess.Popen(
            [python_path, main_script],
            cwd=project_path,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait a moment for Flask to start
        time.sleep(2)
        
        # Open the browser
        url = "http://127.0.0.1:5000"
        print(f"\n🌐 Opening browser at: {url}")
        webbrowser.open(url)
        
        # Ask if user wants to run git-auto
        run_git = input("\n🚀 Would you like to run git-auto to push the project to GitHub? (y/n): ").lower().strip()
        if run_git == 'y':
            if run_git_auto():
                print("\n✅ git-auto.py is running in a new terminal window.")
            else:
                print("\n❌ Failed to run git-auto.py")
        
        # Print output in real-time
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                print(output.strip())
                
        # Check for errors
        if process.returncode != 0:
            error = process.stderr.read()
            print(f"❌ Error running project: {error}")
            return False
            
        return True
    except Exception as e:
        print(f"❌ Error running project: {e}")
        return False

def check_existing_project(ticket_key):
    """Check if a project already exists for the given ticket"""
    project_name = f"project_{ticket_key.lower()}"
    project_path = os.path.join(get_project_base_path(), project_name)
    return os.path.exists(project_path), project_name

def get_python_path(project_name):
    """Get the Python path for an existing project's virtual environment"""
    project_path = os.path.join(get_project_base_path(), project_name)
    venv_path = os.path.join(project_path, "venv")
    
    if os.name == 'nt':  # Windows
        python_path = os.path.join(venv_path, "Scripts", "python.exe")
    else:  # Unix/Linux
        python_path = os.path.join(venv_path, "bin", "python")
        
    if not os.path.exists(python_path):
        print(f"❌ Python not found at: {python_path}")
        print("Checking alternative locations...")
        # Try alternative locations
        if os.name == 'nt':
            alt_paths = [
                os.path.join(venv_path, "Scripts", "python.exe"),
                os.path.join(venv_path, "Scripts", "python"),
                os.path.join(venv_path, "python.exe"),
                os.path.join(venv_path, "python")
            ]
            for path in alt_paths:
                if os.path.exists(path):
                    print(f"✅ Found Python at: {path}")
                    return path
    return python_path if os.path.exists(python_path) else None

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

    # Check if project already exists
    project_exists, project_name = check_existing_project(selected_issue.key)
    
    if project_exists:
        print(f"\n📂 Found existing project: {project_name}")
        action = input("\nWhat would you like to do?\n1. Run existing project\n2. Regenerate project\nEnter choice (1/2): ").strip()
        
        if action == "1":
            python_path = get_python_path(project_name)
            if python_path:
                if run_project(project_name, python_path):
                    print("\n✅ Project is running! You can access it in your browser.")
                else:
                    print("\n❌ Failed to run project. Please check the error messages above.")
            else:
                print("❌ Could not find Python in virtual environment. Please regenerate the project.")
        elif action == "2":
            print("\n🔄 Regenerating project...")
            # Continue with existing generation flow
        else:
            print("❌ Invalid choice.")
            exit(1)
    else:
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
                success, python_path = setup_virtual_environment(project_data["project_name"])
                if success:
                    project_path = os.path.join(get_project_base_path(), project_data["project_name"])
                    print(f"\n✨ Successfully created application!")
                    print(f"📂 Project location: {project_path}")
                    print("\n📚 Please check the README.md file for setup and running instructions.")
                    
                    # Ask user if they want to run the project
                    run_now = input("\n🚀 Would you like to run the project now? (y/n): ").lower().strip()
                    if run_now == 'y':
                        if run_project(project_data["project_name"], python_path):
                            print("\n✅ Project is running! You can access it in your browser.")
                        else:
                            print("\n❌ Failed to run project. Please check the error messages above.")
                else:
                    print("❌ Failed to set up virtual environment")
            else:
                print("❌ Failed to create application files")
        else:
            print("❌ Failed to generate application code")

except Exception as e:
    print(f"❌ Error fetching tickets: {e}")
