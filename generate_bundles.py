import asyncio
import json
import os
import random
import aiohttp
import logging
import time

from aiohttp import ClientSession
from requests.exceptions import RequestException, Timeout

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
    timeout = 10  # Timeout for requests in seconds

    while attempt < max_retries:
        try:
            release_url = None
            if "latest" in repo_data:
                release_url = f"{repo_data['patches']}/releases/latest"
            elif "prerelease" in repo_data and repo_data["prerelease"]:
                logging.warning(f"Pre-release fetching not implemented for {source}")
            else:
                release_url = f"{repo_data['patches']}/releases/tags/{repo_data.get('tag')}"

            if release_url:
                headers = {'Authorization': f'token {get_github_pat()}'}
                start_time = time.time()
                async with session.get(release_url, headers=headers, timeout=timeout) as response:
                    response.raise_for_status()  # Raise an exception for error HTTP status codes
                    release_data = await response.json()
                    logging.info(f"Fetched release data for {source} in {time.time() - start_time} seconds")

                    # Assuming the release data structure is similar to PyGithub
                    latest_release = release_data  # Use the full response data
                    patches_url = None
                    integrations_url = None
                    for asset in latest_release['assets']:
                        if asset['name'].endswith(".jar"):
                            patches_url = asset['browser_download_url']
                        elif asset['name'].endswith(".apk"):
                            integrations_url = asset['browser_download_url']

                    # ... rest of the logic to process patches_url and integrations_url
                    logging.info(f"Processed release data for {source}")

                    break
            else:
                logging.warning(f"No appropriate URL found for {source}")

        except (RequestException, Timeout, aiohttp.ClientError) as e:
            logging.error(f"Error fetching release data for {source}: {e}")
            logging.error(f"Request URL: {release_url}")
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

    tasks = []
    async with ClientSession() as session:
        sem = asyncio.Semaphore(5)  # Limit to 5 concurrent requests

        async def limited_fetch_release_data(source, repo_data):
            async with sem:
                await fetch_release_data(session, source, repo_data)

        tasks = [limited_fetch_release_data(source, repo_data) for source, repo_data in sources.items()]
        await asyncio.gather(*tasks)

if __name__ == "__main__":
    start_time = time.time()
    asyncio.run(main())
    logging.info(f"Total execution time: {time.time() - start_time} seconds")
