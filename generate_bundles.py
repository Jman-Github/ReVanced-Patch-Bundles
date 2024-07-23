import asyncio
import json
import os
import random
import requests
import logging

from requests.exceptions import RequestException

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Function to get the PAT from an environment variable
def get_github_pat():
    return os.getenv('GH_PAT')

def exponential_backoff(attempt):
    """Implements exponential backoff with jitter."""
    base = 2
    max_delay = 60  # Maximum delay in seconds
    jitter = 0.2  # Jitter factor

    delay = min(base ** attempt * random.uniform(1 - jitter, 1 + jitter), max_delay)
    return delay

async def fetch_release_data(source, repo_data):
    attempt = 0
    max_retries = 3  # Maximum retry attempts

    while attempt < max_retries:
        try:
            release_url = None
            if "latest" in repo_data:
                release_url = f"{repo_data['patches']}/releases/latest"
            elif "prerelease" in repo_data and repo_data["prerelease"]:
                # Handle logic for fetching pre-releases (if applicable)
                # You might need to add specific logic for the repository's pre-release strategy
                logging.warning(f"Pre-release fetching not implemented for {source}")
            else:
                release_url = f"{repo_data['patches']}/releases/tags/{repo_data.get('tag')}"  # Use 'tag' key if provided

            if release_url:
                response = requests.get(release_url, headers={'Authorization': f'token {get_github_pat()}'})
                response.raise_for_status()  # Raise an exception for error HTTP status codes
                release_data = response.json()

                # Assuming the release data structure is similar to PyGithub
                # You might need to adapt the following logic based on the actual response
                latest_release = release_data[0]  # Assuming latest release is the first in the list
                patches_url = None
                integrations_url = None
                for asset in latest_release['assets']:
                    if asset['name'].endswith(".jar"):
                        patches_url = asset['browser_download_url']
                    elif asset['name'].endswith(".apk"):
                        integrations_url = asset['browser_download_url']

                # ... rest of the logic to process patches_url and integrations_url

                break
            else:
                logging.warning(f"No appropriate URL found for {source}")

        except RequestException as e:
            logging.error(f"Error fetching release data for {source}: {e}")
            logging.error(f"Request URL: {release_url}")
            logging.error(f"Response status code: {e.response.status_code if hasattr(e, 'response') else 'N/A'}")
            logging.error(f"Response text: {e.response.text if hasattr(e, 'response') else 'N/A'}")
            attempt += 1
            if attempt >= max_retries:
                logging.error(f"Max retries reached for {source}")
                return
            delay = exponential_backoff(attempt)
            logging.warning(f"Retrying in {delay} seconds due to error")
            await asyncio.sleep(delay)

async def main():
    with open('bundle-sources.json') as file:
        sources = json.load(file)

    tasks = [fetch_release_data(source, repo_data) for source, repo_data in sources.items()]
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())
