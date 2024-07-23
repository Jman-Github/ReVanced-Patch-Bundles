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
            print(f"Fetching release data for source: {source}")
            release_url = None
            # ... (rest of your release URL logic)

            if release_url:
                print(f"Making request to: {release_url}")
                response = requests.get(release_url, headers={'Authorization': f'token {get_github_pat()}'})
                response.raise_for_status()  # Raise an exception for error HTTP status codes
                release_data = response.json()

                # ... (rest of your release data processing)

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

    print("Starting to fetch release data")
    tasks = [fetch_release_data(source, repo_data) for source, repo_data in sources.items()]
    await asyncio.gather(*tasks)
    print("Finished fetching release data")

if __name__ == "__main__":
    asyncio.run(main())
