import subprocess
import os
from crewai.tools import BaseTool
from typing import Type, List
from pydantic import BaseModel, Field
from datetime import datetime


class GitStatusToolInput(BaseModel):
    pass

class GitStatusTool(BaseTool):
    name: str = "Git Status Tool"
    description: str = "Check the current git repository status, including modified files and branch."
    args_schema: Type[BaseModel] = GitStatusToolInput

    def _run(self) -> str:
        try:
            result = subprocess.run(
                ['git', 'status', '--short'],
                capture_output=True,
                text=True,
                cwd=os.getcwd()
            )
            if result.returncode == 0:
                return f"Git Status:\n{result.stdout}" if result.stdout else "Working tree clean"
            return f"Error: {result.stderr}"
        except Exception as e:
            return f"Error checking git status: {str(e)}"


class GitBranchToolInput(BaseModel):
    branch_name: str = Field(..., description="Name of the new branch to create")

class GitBranchTool(BaseTool):
    name: str = "Git Branch Tool"
    description: str = "Create a new git branch from the current branch."
    args_schema: Type[BaseModel] = GitBranchToolInput

    def _run(self, branch_name: str) -> str:
        try:
            # Checkout new branch
            result = subprocess.run(
                ['git', 'checkout', '-b', branch_name],
                capture_output=True,
                text=True,
                cwd=os.getcwd()
            )
            if result.returncode == 0:
                return f"Successfully created and switched to branch '{branch_name}'"
            return f"Error creating branch: {result.stderr}"
        except Exception as e:
            return f"Error: {str(e)}"


class GitCommitToolInput(BaseModel):
    message: str = Field(..., description="Semantic commit message (e.g., 'feat: add new feature', 'fix: resolve bug')")
    files: List[str] = Field(default=[], description="Optional list of specific files to stage. Empty = stage all changes.")

class GitCommitTool(BaseTool):
    name: str = "Git Commit Tool"
    description: str = (
        "Stage files and create a semantic commit. "
        "Use conventional commit format: type(scope): description. "
        "Types: feat, fix, docs, test, refactor, chore."
    )
    args_schema: Type[BaseModel] = GitCommitToolInput

    def _run(self, message: str, files: List[str] = []) -> str:
        try:
            # Stage files
            if files:
                for file in files:
                    subprocess.run(['git', 'add', file], cwd=os.getcwd())
            else:
                subprocess.run(['git', 'add', '.'], cwd=os.getcwd())

            # Commit
            result = subprocess.run(
                ['git', 'commit', '-m', message],
                capture_output=True,
                text=True,
                cwd=os.getcwd()
            )
            if result.returncode == 0:
                return f"Commit successful: {message}\n{result.stdout}"
            return f"Commit failed: {result.stderr}"
        except Exception as e:
            return f"Error: {str(e)}"


class GitPushToolInput(BaseModel):
    branch_name: str = Field(..., description="Branch name to push to remote")
    set_upstream: bool = Field(default=True, description="Set upstream for new branches")

class GitPushTool(BaseTool):
    name: str = "Git Push Tool"
    description: str = "Push commits to the remote repository."
    args_schema: Type[BaseModel] = GitPushToolInput

    def _run(self, branch_name: str, set_upstream: bool = True) -> str:
        try:
            cmd = ['git', 'push']
            if set_upstream:
                cmd.extend(['-u', 'origin', branch_name])
            else:
                cmd.append('origin')
                cmd.append(branch_name)

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=os.getcwd()
            )
            if result.returncode == 0:
                return f"Successfully pushed to {branch_name}"
            return f"Push failed: {result.stderr}"
        except Exception as e:
            return f"Error: {str(e)}"


class GitHubPRToolInput(BaseModel):
    title: str = Field(..., description="Pull request title")
    body: str = Field(..., description="Pull request description/body")
    head_branch: str = Field(..., description="Source branch (your feature branch)")
    base_branch: str = Field(default="main", description="Target branch (usually 'main' or 'develop')")

class GitHubPRTool(BaseTool):
    name: str = "GitHub Pull Request Tool"
    description: str = (
        "Create a Pull Request on GitHub using the GitHub API. "
        "Requires GITHUB_APP authentication."
    )
    args_schema: Type[BaseModel] = GitHubPRToolInput

    def _run(self, title: str, body: str, head_branch: str, base_branch: str = "main") -> str:
        try:
            from .github_app_auth import get_installation_token
            import requests

            # Get repo from .env
            repo = os.getenv("GITHUB_REPO")
            if not repo:
                return "Error: GITHUB_REPO not set in .env"

            # Get auth token
            token = get_installation_token()

            # Create PR
            url = f"https://api.github.com/repos/{repo}/pulls"
            headers = {
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28"
            }
            data = {
                "title": title,
                "body": body,
                "head": head_branch,
                "base": base_branch
            }

            response = requests.post(url, headers=headers, json=data)
            if response.status_code == 201:
                pr_url = response.json().get('html_url')
                return f"Pull Request created successfully: {pr_url}"
            else:
                return f"Failed to create PR: {response.status_code} - {response.text}"

        except Exception as e:
            return f"Error creating PR: {str(e)}"
