from crewai.tools import BaseTool
import os
import requests
from .github_app_auth import GitHubAppAuth
from dotenv import load_dotenv

load_dotenv()

class GitHubIssueCreatorTool(BaseTool):
    name: str = "Create GitHub Issue"
    description: str = (
        "Creates a new issue in the repository. "
        "Useful for logging high-volatility alerts or important events. "
        "Requires 'title' and 'body' as input."
    )

    def _run(self, title: str, body: str) -> str:
        # Load credentials
        app_id = os.getenv("GITHUB_APP_ID")
        private_key_path = os.getenv("GITHUB_PRIVATE_KEY_PATH")
        
        # Handle Owner/Repo
        owner = os.getenv("GITHUB_OWNER")
        repo = os.getenv("GITHUB_REPO")
        
        if repo and "/" in repo and not owner:
            # If repo is "owner/repo" and owner is missing, parse it
            parts = repo.split("/")
            if len(parts) == 2:
                owner = parts[0]
                repo = parts[1]

        if not all([app_id, private_key_path, owner, repo]):
            return f"Error: Missing configuration. Found: AppID={bool(app_id)}, KeyPath={bool(private_key_path)}, Owner={owner}, Repo={repo}"

        try:
            # Authenticate
            auth = GitHubAppAuth(app_id, private_key_path)
            installation_id = auth.get_installation_id(owner, repo)
            token = auth.get_installation_access_token(installation_id)

            # Create Issue
            url = f"https://api.github.com/repos/{owner}/{repo}/issues"
            headers = {
                "Authorization": f"Token {token}",
                "Accept": "application/vnd.github+json"
            }
            data = {
                "title": title,
                "body": body
            }

            response = requests.post(url, headers=headers, json=data)
            
            if response.status_code == 201:
                issue_url = response.json().get("html_url")
                return f"Successfully created GitHub issue: {issue_url}"
            else:
                return f"Failed to create issue. Status: {response.status_code}. Response: {response.text}"

        except Exception as e:
            return f"Error creating GitHub issue: {str(e)}"
