import time
import requests
from github import Github, GithubException
from ratelimit import limits, sleep_and_retry

# Define your GitHub token
GITHUB_TOKEN = 'your_github_token'

# Initialize the GitHub client
g = Github(GITHUB_TOKEN)

# Constants for rate limit handling
CALLS = 5000
PERIOD = 3600

# Decorator to handle rate limiting
@sleep_and_retry
@limits(calls=CALLS, period=PERIOD)
def get_repo_release_data(repo_name):
    try:
        repo = g.get_repo(repo_name)
        releases = repo.get_releases()
        return [release.tag_name for release in releases]
    except GithubException as e:
        if e.status == 404:
            print(f"Error fetching release data for {repo_name}: {e.data['message']}")
        else:
            raise

def fetch_release_data(repos):
    release_data = {}
    for repo in repos:
        retries = 3
        while retries > 0:
            try:
                print(f"Fetching release data for {repo}")
                release_data[repo] = get_repo_release_data(repo)
                break
            except GithubException as e:
                print(f"Error fetching release data for {repo}: {e.data['message']}")
                retries -= 1
                if retries > 0:
                    sleep_time = (4 - retries) ** 2  # Exponential backoff
                    print(f"Retrying in {sleep_time} seconds...")
                    time.sleep(sleep_time)
                else:
                    print(f"Max retries reached for {repo}")
    return release_data

# Ensures this block runs only when the script is executed directly
if __name__ == "__main__":
    # List of repositories to fetch release data for
    repos = [
        'experimental-dev',
        'experimental-stable',
        'experimental-latest',
        'privacy-dev',
        'privacy-stable',
        'privacy-latest',
        'rex-dev',
        'rex-stable',
        'rex-latest',
        'twitter-dev',
        'twitter-latest',
        'twitter-stable',
        'rufusin-dev',
        'rufusin-stable',
        'rufusin-latest',
        'dropped-dev',
        'dropped-latest',
        'dropped-stable',
        'inotia00-dev',
        'inotia00-stable',
        'inotia00-latest',
        'biliroamingx-dev',
        'biliroamingx-stable',
        'biliroamingx-latest',
        'wyse--dev',
        'wyse--latest',
        'wyse--stable',
        'bholeykabhakt-dev',
        'bholeykabhakt-stable',
        'bholeykabhakt-latest',
        'andronedev-dev',
        'andronedev-stable',
        'andronedev-latest',
        '1fexd-dev',
        '1fexd-stable',
        '1fexd-latest',
        'revanced-dev',
        'revanced-latest',
        'piko-latest',
        'piko-dev',
        'piko-stable',
        'anddea-latest',
        'anddea-dev',
        'anddea-stable'
    ]
        
    # Fetch release data for the specified repositories
    release_data = fetch_release_data(repos)
    
    # Print the fetched release data
    for repo, releases in release_data.items():
        print(f"{repo}: {releases}")
