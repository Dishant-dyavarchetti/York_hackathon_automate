import os
import git
from github import Github
from git import Repo
import sys
from pathlib import Path
from dotenv import load_dotenv
import shutil

def load_env_token():
    """Load GitHub token from .env file."""
    load_dotenv()
    token = os.getenv('GITHUB_TOKEN')
    if not token:
        print("Error: GITHUB_TOKEN not found in .env file")
        print("Please create a .env file with your GitHub token:")
        print("GITHUB_TOKEN=your_token_here")
        sys.exit(1)
    return token

def check_github_auth():
    """Check if user is authenticated with GitHub."""
    try:
        github_token = load_env_token()
        g = Github(github_token)
        user = g.get_user()
        print(f"\nSuccessfully authenticated as: {user.login}")
        return github_token, user.login
    except Exception as e:
        print(f"\nError during GitHub authentication: {str(e)}")
        print("Please make sure you have a valid GitHub token in your .env file")
        sys.exit(1)

def get_project_directories():
    """Get list of project directories from generated_projects folder."""
    base_dir = "generated_projects"
    if not os.path.exists(base_dir):
        print(f"Error: {base_dir} directory not found")
        sys.exit(1)
    
    projects = [d for d in os.listdir(base_dir) 
               if os.path.isdir(os.path.join(base_dir, d)) 
               and not d.startswith('.')]
    
    if not projects:
        print(f"No project directories found in {base_dir}")
        sys.exit(1)
    
    return projects

def initialize_git_repo():
    """Initialize a new git repository if it doesn't exist."""
    try:
        repo = Repo('.')
        print("Git repository already exists.")
        return repo
    except git.exc.InvalidGitRepositoryError:
        print("Initializing new git repository...")
        repo = Repo.init('.', initial_branch='main')
        # Create an initial commit if none exists
        dummy_path = Path("README.md")
        dummy_path.write_text("# Initial Commit\n")
        repo.index.add([str(dummy_path)])
        repo.index.commit("Initial commit")
        print("Git repository initialized and first commit created.")
        return repo

def create_github_repo(token, username):
    """Create a new private GitHub repository."""
    try:
        g = Github(token)
        user = g.get_user()
        repo = user.create_repo("yorkhack", private=True, auto_init=True)
        print(f"Created new private GitHub repository: {username}/yorkhack")
        return repo
    except Exception as e:
        print(f"Error creating GitHub repository: {str(e)}")
        sys.exit(1)

def setup_remote(repo, token, username):
    """Set up remote repository."""
    try:
        # Configure Git user if not already configured
        try:
            repo.config_reader().get_value('user', 'name')
            repo.config_reader().get_value('user', 'email')
        except:
            print("\nGit user configuration not found. Please set up your Git identity:")
            name = input("Enter your name: ").strip()
            email = input("Enter your email: ").strip()
            repo.config_writer().set_value('user', 'name', name).release()
            repo.config_writer().set_value('user', 'email', email).release()
            print("Git identity configured successfully.")

        # Set up remote
        remote_url = f"https://{token}@github.com/{username}/yorkhack.git"
        try:
            repo.delete_remote('origin')
        except:
            pass
        repo.create_remote('origin', remote_url)
        print(f"Remote repository configured: {username}/yorkhack")
                
    except Exception as e:
        print(f"Error setting up remote: {str(e)}")
        sys.exit(1)

# def push_project_to_branch(repo, project_name, token, username):
#     """Push project content to its corresponding branch."""
    # try:
    #     # Store current branch
    #     current_branch = "main"
        
    #     # Create and switch to project branch
    #     try:
    #         repo.git.checkout('-b', project_name)
    #         print(f"Created and switched to branch: {project_name}")
    #     except git.exc.GitCommandError:
    #         repo.git.checkout(project_name)
    #         print(f"Switched to existing branch: {project_name}")
        
    #     # Get the project directory path
    #     project_path = os.path.join('generated_projects', project_name)
    #     print(project_path)
        
    #     # Add all files in the project directory
    #     repo.git.add(f'generated_projects/{project_name}')  # Add all files including untracked files
        
    #     # Check if there are changes
    #     if not repo.is_dirty() and not repo.untracked_files:
    #         print(f"No changes to commit for project: {project_name}")
    #         # Switch back to original branch
    #         # repo.git.checkout(current_branch)
    #         return
        
    #     # Create commit message
    #     commit_message = f"Update {project_name} project"
        
    #     # Commit changes
    #     repo.git.commit('-m', commit_message)
        
    #     # Push to remote
    #     try:
    #         repo.git.push('origin', project_name)
    #         print(f"\nSuccessfully pushed {project_name} to its branch.")
    #     except git.exc.GitCommandError as e:
    #         print(f"Error pushing {project_name} to its branch: {str(e)}")
    #         raise e
    #     print(f"Currently on branch: {repo.active_branch.name}")
    #     print(list(repo.branches))
    #     # Switch back to original branch
    #     # repo.git.checkout(current_branch)
    #     print(f"Switched back to branch: {current_branch}")
                
    # except Exception as e:
    #     print(f"Error processing project {project_name}: {str(e)}")
    #     # Try to switch back to original branch in case of error
    #     # try:
    #     #     repo.git.checkout(current_branch)
    #     # except:
    #     #     print("Error switching back to original branch")
    #     #     pass
    #     sys.exit(1)
    # # repo.git.checkout(current_branch)
def push_project_to_branch(repo, project_name, token, username):
    """Push project content to its corresponding branch."""
    try:
        current_branch = repo.active_branch.name  # detect current branch dynamically

        # Project-specific branch
        try:
            repo.git.checkout('-b', project_name)
            print(f"Created and switched to branch: {project_name}")
        except git.exc.GitCommandError:
            repo.git.checkout(project_name)
            print(f"Switched to existing branch: {project_name}")
        
        # Project directory path
        project_path = os.path.join('generated_projects', project_name)

        # Reset index to avoid staging leftover files
        repo.git.reset('--mixed')  # unstages everything
        project_path = os.path.join('generated_projects', project_name)
        for item in os.listdir(project_path):
            s = os.path.join(project_path, item)
            d = os.path.join('.', item)
            if os.path.isdir(s):
                shutil.copytree(s, d)
            else:
                shutil.copy2(s, d)

        # Stage all new files
        repo.git.add(all=True)

        # Check if there are any staged changes
        if not repo.is_dirty() and not repo.untracked_files:
            print(f"No changes to commit for project: {project_name}")
            repo.git.checkout(current_branch)
            return

        # Commit and push
        commit_message = f"Update {project_name} project"
        repo.git.commit('-m', commit_message)

        repo.git.push('origin', project_name)
        print(f"✅ Successfully pushed {project_name} to its branch.")

        # Switch back to the main (original) branch
        repo.git.checkout(current_branch)
        print(f"Switched back to branch: {current_branch}")

    except Exception as e:
        print(f"❌ Error processing project {project_name}: {str(e)}")
        try:
            repo.git.checkout(current_branch)
        except:
            print("⚠️ Failed to switch back to original branch")
        sys.exit(1)

def main():
    # Check GitHub authentication
    github_token, username = check_github_auth()
    
    # Get list of project directories
    projects = get_project_directories()
    print(f"\nFound {len(projects)} projects: {', '.join(projects)}")
    # Initialize or get existing repository
    repo = initialize_git_repo()
    
    # Check if remote exists
    try:
        remote = repo.remote('origin')
        print("Remote repository already exists.")
    except ValueError:
        # Create new GitHub repository and set up remote
        github_repo = create_github_repo(github_token, username)
        setup_remote(repo, github_token, username)

    try:
        repo.git.checkout('main')
    except git.exc.GitCommandError:
        repo.git.checkout('-b', 'main')    
        repo.git.push('--set-upstream', 'origin', 'main')
  
    # Push each project to its corresponding branch
    for project in projects:
        print(f"\nProcessing project: {project}")
        push_project_to_branch(repo, project, github_token, username)

if __name__ == "__main__":
    main() 