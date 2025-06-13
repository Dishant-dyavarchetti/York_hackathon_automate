# 🛠️ York Hackathon Project Code Automation Tool

This project automates code generation and project setup from accepted JIRA tickets using the JIRA API and OpenAI's LLMs. It also supports codespace generation, local execution, and (coming soon) GitHub repository automation.

## 🚀 Features

- ✅ Fetch accepted tasks from JIRA using the JIRA API  
- 🤖 Automatically generate project code and structure using OpenAI API  
- 🗂️ Save all generated files and folders inside a `generated_projects` directory  
- 💻 Execute the generated project to validate functionality  
- ⛓️ (Upcoming) GitHub automation: create a new repo, push code to a new branch, and set up CI/CD workflows  

## 🧪 How It Works

1. **JIRA Task Fetching**: Automatically retrieves tasks marked as accepted.  
2. **Code Generation**: Uses LLMs to generate code solutions.  
3. **Project Scaffolding**: Creates all necessary files and folders under `generated_projects`.  
4. **Execution Prompt**: Asks the user to run the project.  
5. **Git Automation**: *(In Progress)* Will soon automate pushing code to GitHub.  

## 📦 Tech Stack

- **Language**: Python  
- **LLM**: OpenAI GPT  
- **API Integration**: JIRA REST API  
- **Automation**: Python threading and subprocess modules  
- **Version Control**: GitHub (via PyGit2/GitPython in future)  

## 📅 Future Work

- [ ] Automate GitHub repo creation  
- [ ] Branch push automation for each project  
- [ ] Codespace link generation  
- [ ] Web interface to manage tickets and see code output (Streamlit or Flask)  

## 👥 Contributors

- **Dishant Dyavarchetti**  
  [LinkedIn](www.linkedin.com/in/dishant-dyavarchetti-8a269729a/)

- **Parshva Modi**   
  [LinkedIn](https://www.linkedin.com/in/parshva-modi/)

- **Bhavya Jani**   
  [LinkedIn](https://www.linkedin.com/in/bhavya-jani-631568332/)

- **Nikhil Bhatia**   
  [LinkedIn](https://www.linkedin.com/in/nikhil-bhatia2405/)

https://www.linkedin.com/in/bhavya-jani-631568332/

## 🏃‍♂️ How to Run

1. Clone the repo:
    ```bash
    git clone https://github.com/your-repo/York_hackathon_automate.git
    ```

2. Navigate and install dependencies:
    ```bash
    cd York_hackathon_automate/main
    pip install -r requirements.txt
    ```

3. Run the project:
    ```bash
    python integrations/main.py
    ```

Make sure your `.env` has your JIRA and OpenAI credentials.

## 📬 Contact

For contributions or questions, feel free to open an issue or pull request.  
You can also reach out to [Dishant Dyavarchetti on LinkedIn](www.linkedin.com/in/dishant-dyavarchetti-8a269729a/).

---
