import requests
import base64
from typing import Dict, List, Optional

class GitHubFetcher:
    def __init__(self, token: Optional[str] = None):
        """
        Initialize the GitHub API fetcher.
        
        Args:
            token (str, optional): GitHub personal access token for authentication
        """
        self.base_url = "https://api.github.com"
        self.headers = {
            "Accept": "application/vnd.github.v3+json"
        }
        if token:
            self.headers["Authorization"] = f"token {token}"

    def get_user_repos(self, username: str) -> List[Dict]:
        """
        Fetch all public repositories for a given username.
        
        Args:
            username (str): GitHub username
            
        Returns:
            List[Dict]: List of repository information
        """
        url = f"{self.base_url}/users/{username}/repos"
        response = requests.get(url, headers=self.headers)
        
        if response.status_code != 200:
            raise Exception(f"Failed to fetch repositories: {response.status_code}")
            
        repos = response.json()
        return [{
            'url' : "https://github.com/"+username+"/"+repo['name'],
            'name': repo['name'],
            'description': repo['description'],
            'stars': repo['stargazers_count'],
            'forks': repo['forks_count'],
            'language': repo['language'],
            'created_at': repo['created_at'],
            'updated_at': repo['updated_at'],
            'clone_url': repo['clone_url'],
            'homepage': repo['homepage']
        } for repo in repos]

    def get_readme(self, username: str, repo_name: str) -> str:
        """
        Fetch the README content for a specific repository.
        
        Args:
            username (str): GitHub username
            repo_name (str): Repository name
            
        Returns:
            str: README content in plain text
        """
        url = f"{self.base_url}/repos/{username}/{repo_name}/readme"
        response = requests.get(url, headers=self.headers)
        
        if response.status_code != 200:
            raise Exception(f"Failed to fetch README: {response.status_code}")
            
        content = response.json()['content']
        return base64.b64decode(content).decode('utf-8')

def main():
    # Example usage
    github_token = "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"  # Optional
    fetcher = GitHubFetcher(github_token)
    
    try:
        # Get username from user input
        username = input("Enter GitHub username: ")
        
        # Fetch and display repositories
        print(f"\nFetching repositories for {username}...")
        repos = fetcher.get_user_repos(username)
        
        print(f"\nFound {len(repos)} repositories:")
        for i, repo in enumerate(repos, 1):
            print(f"\n{i}. {repo['name']}")
            print(f"   Description: {repo['description']}")
            print(f"   Language: {repo['language']}")
            print(f"   Stars: {repo['stars']}")
            print(f"   Forks: {repo['forks']}")
            print(f"   url : {repo['url']}")
        
        # Get README for a specific repository
        repo_choice = input("\nEnter repository name to fetch README (or press Enter to skip): ")
        if repo_choice:
            readme_content = fetcher.get_readme(username, repo_choice)
            print(f"\nREADME for {repo_choice}:")
            print("=" * 50)
            print(readme_content)
            
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()