import jwt
import time
import requests
import os
from dotenv import load_dotenv

load_dotenv()

class GitHubAppAuth:
    def __init__(self, app_id: str, private_key_path: str):
        self.app_id = app_id
        self.private_key_path = private_key_path

    def generate_jwt(self) -> str:
        """Generates a JWT for GitHub App authentication."""
        with open(self.private_key_path, 'r') as f:
            private_key = f.read()

        payload = {
            # Issued at time, 60 seconds in the past to allow for clock drift
            'iat': int(time.time()) - 60,
            # JWT expiration time (10 minute maximum, using 9 to be safe)
            'exp': int(time.time()) + (9 * 60),
            # GitHub App's identifier
            'iss': self.app_id
        }

        encoded_jwt = jwt.encode(payload, private_key, algorithm='RS256')
        return encoded_jwt

    def get_installation_access_token(self, installation_id: str) -> str:
        """Exchanges the JWT for an installation access token."""
        jwt_token = self.generate_jwt()
        headers = {
            'Authorization': f'Bearer {jwt_token}',
            'Accept': 'application/vnd.github+json',
            'X-GitHub-Api-Version': '2022-11-28'
        }
        
        url = f'https://api.github.com/app/installations/{installation_id}/access_tokens'
        response = requests.post(url, headers=headers)
        
        if response.status_code == 201:
            return response.json()['token']
        else:
            raise Exception(f"Failed to get installation token: {response.status_code} {response.text}")
    
    def get_installation_id(self, owner: str, repo: str) -> str:
        """Gets the installation ID for a specific repository."""
        jwt_token = self.generate_jwt()
        headers = {
            'Authorization': f'Bearer {jwt_token}',
            'Accept': 'application/vnd.github+json',
            'X-GitHub-Api-Version': '2022-11-28'
        }
        
        url = f'https://api.github.com/repos/{owner}/{repo}/installation'
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            return response.json()['id']
        else:
             raise Exception(f"Failed to get installation ID for repo {owner}/{repo}: {response.status_code} {response.text}")
