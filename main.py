from github_fetcher import GitHubProfileFetcher

# Initialize the fetcher
fetcher = GitHubProfileFetcher(
    access_token="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"  # Token in quotes
)

# Fetch the profiles
profiles = fetcher.fetch_bulk_profiles(
    total_count=1000,
    output_file="github_profiles_1000.json"
)

print(f"Successfully fetched {len(profiles)} profiles")