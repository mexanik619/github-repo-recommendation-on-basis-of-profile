import requests
import random
import time
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List
import logging

class GitHubProfileFetcher:
    def __init__(self, access_token: Optional[str] = None, batch_size: int = 50):
        """
        Initialize the GitHub Profile Fetcher.
        
        Args:
            access_token (str, optional): GitHub Personal Access Token to increase rate limits
            batch_size (int): Number of profiles to fetch in each batch
        """
        self.base_url = "https://api.github.com"
        self.headers = {
            "Accept": "application/vnd.github.v3+json"
        }
        if access_token:
            self.headers["Authorization"] = f"token {access_token}"
        
        self.batch_size = batch_size
        self._setup_logging()
    
    def _setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('github_fetcher.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def _make_request(self, endpoint: str) -> Dict:
        """Make a request to the GitHub API with rate limit handling."""
        while True:
            response = requests.get(f"{self.base_url}/{endpoint}", headers=self.headers)
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 403:
                rate_limit_reset = int(response.headers.get('X-RateLimit-Reset', 0))
                wait_time = max(rate_limit_reset - time.time(), 0)
                if wait_time > 0:
                    self.logger.warning(f"Rate limit reached. Waiting {wait_time:.0f} seconds...")
                    time.sleep(wait_time + 1)
                    continue
            elif response.status_code == 404:
                raise ValueError("Not Found")
            else:
                raise Exception(f"API request failed with status code: {response.status_code}")
    
    def _format_user_data(self, data: Dict) -> Dict:
        """Format the user data to include only relevant information."""
        return {
            "username": data.get("login"),
            "name": data.get("name"),
            "bio": data.get("bio"),
            "location": data.get("location"),
            "public_repos": data.get("public_repos"),
            "followers": data.get("followers"),
            "following": data.get("following"),
            "created_at": data.get("created_at"),
            "profile_url": data.get("html_url"),
            "avatar_url": data.get("avatar_url"),
            "company": data.get("company"),
            "blog": data.get("blog"),
            "twitter_username": data.get("twitter_username"),
            "public_gists": data.get("public_gists"),
            "fetched_at": datetime.now().isoformat()
        }
    
    def fetch_bulk_profiles(self, total_count: int, output_file: str = None) -> List[Dict]:
        """
        Fetch multiple GitHub user profiles in batches with progress tracking and data saving.
        
        Args:
            total_count (int): Total number of profiles to fetch
            output_file (str, optional): File to save the results
            
        Returns:
            List[Dict]: List of user profile information
        """
        if output_file is None:
            output_file = f"github_profiles_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        output_path = Path(output_file)
        existing_data = []
        
        # Load existing data if file exists
        if output_path.exists():
            with output_path.open('r', encoding='utf-8') as f:
                existing_data = json.load(f)
            self.logger.info(f"Loaded {len(existing_data)} existing profiles from {output_file}")
        
        users = existing_data
        remaining = total_count - len(users)
        batch_number = 1
        
        while remaining > 0:
            batch_size = min(self.batch_size, remaining)
            self.logger.info(f"Fetching batch {batch_number} ({batch_size} profiles)")
            
            batch_users = []
            for _ in range(batch_size):
                try:
                    # Get a random user ID
                    random_id = random.randint(1, 100_000_000)
                    user_data = self._make_request(f"user/{random_id}")
                    formatted_data = self._format_user_data(user_data)
                    batch_users.append(formatted_data)
                    
                    # Add small delay between requests
                    time.sleep(0.5)
                    
                except ValueError:  # Not Found
                    continue
                except Exception as e:
                    self.logger.error(f"Error fetching user: {str(e)}")
                    continue
            
            # Add batch to users list
            users.extend(batch_users)
            remaining = total_count - len(users)
            
            # Save progress after each batch
            with output_path.open('w', encoding='utf-8') as f:
                json.dump(users, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Saved {len(users)} profiles to {output_file}")
            batch_number += 1
        
        return users