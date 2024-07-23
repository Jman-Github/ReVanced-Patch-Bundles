import asyncio
import json
import os
import random
import logging

import aiohttp

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

async def fetch_release_data(session, source, repo_data):
    attempt = 0
    max_retries = 3  # Maximum retry attempts

    while attempt < max_retries:
        try:
            release_url = None
            # ... (rest of your release URL logic)

            if release_url:
                async with session.get(release_url, headers={'Authorization': f'token {get_github_pat()}'}) as response:
                    response.raise_for_status()
                    release_data = await response.json()

                    # ... (rest of your release data processing)

                    break
            else:
                logging.warning(f"No appropriate URL found for {source}")

        except RequestException as e:
            # Handle errors and retries as before
            pass

async def main():
    with open('bundle-sources.json') as file:
        sources = json.load(file)

    async with aiohttp.ClientSession() as session:
        tasks = [fetch_release_data(session, source, repo_data) for source, repo_data in sources.items()]
        await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())
