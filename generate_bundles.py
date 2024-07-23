import asyncio
import json
import os
import random
from github import Github
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Function to get the PAT from an environment variable
def get_github_pat():
    return os.getenv('GITHUB_PAT')

def exponential_backoff(attempt):
    """Implements exponential backoff with jitter."""
    base = 2
    max_delay = 60  # Maximum delay in seconds
    jitter = 0.2  # Jitter factor

    delay = min(base ** attempt * random.uniform(1 - jitter, 1 + jitter), max_delay)
    return delay

def get_latest_release(repo_url, prerelease, latest_flag=False):
    async def get_version_urls(release):
        version = release.tag_name
        patches_url = None
        integrations_url = None
        for asset in release.assets:
            if asset.name.endswith(".jar"):
                patches_url = asset.url
            elif asset.name.endswith(".apk"):
                integrations_url = asset.url
        return version, patches_url, integrations_url

    # Ensure the URL ends with /releases
    if not repo_url.endswith("/releases"):
        repo_url += "/releases"

    with Github(get_github_pat()) as github:
        repo = github.get_repo(repo_url)
        try:
            releases = repo.get_releases()
        except Exception as e:
            logging.error(f"Error fetching releases for {repo_url}: {e}")
            return None, None, None

        if not releases:
            logging.warning(f"No releases found for {repo_url}")
            return None, None, None

        if latest_flag:
            target_release = max(releases, key=lambda x: x.created_at)
        elif prerelease:
            target_release = max((release for release in releases if release.prerelease), key=lambda x: x.created_at, default=None)
        else:
            target_release = max((release for release in releases if not release.prerelease), key=lambda x: x.created_at, default=None)

        if target_release:
            return get_version_urls(target_release)
        else:
            logging.warning(f"No {'pre' if prerelease else ''}release found for {repo_url}")
            return None, None, None

async def fetch_release_data(source, repo):
    prerelease = repo.get('prerelease', False)
    latest_flag = repo.get('latest', False)
    attempt = 0
    max_retries = 3  # Maximum retry attempts

    while attempt < max_retries:
        try:
            patches_version, patches_asset_url, integrations_url = get_latest_release(repo.get('patches'), prerelease, latest_flag)
            integrations_version, integrations_asset_url, _ = get_latest_release(repo.get('integration'), prerelease, latest_flag)
            break
        except Exception as e:
            logging.error(f"Error fetching release data for {source}: {e}")
            attempt += 1
            if attempt >= max_retries:
                logging.error(f"Max retries reached for {source}")
                return
            delay = exponential_backoff(attempt)
            logging.warning(f"Retrying in {delay} seconds due to error")
            await asyncio.sleep(delay)

    if patches_version and patches_asset_url and integrations_version and integrations_asset_url:
        info_dict = {
            "patches": {
                "version": patches_version,
                "url": patches_asset_url
            },
            "integrations": {
                "version": integrations_version,
                "url": integrations_asset_url
            }
        }
        with open(f'{source}-patches-bundle.json', 'w') as file:
            json.dump(info_dict, file, indent=2)
        logging.info(f"Latest release information saved to {source}-patches-bundle.json")
    else:
        logging.error(f"Error: Unable to fetch release information for {source}")

async def main():
    with open('bundle-sources.json') as file:
        sources = json.load(file)

    # No need for configuring Git user as PyGithub handles authentication

    for source, repo in sources.items():
        await fetch_release_data(source, repo)
        await asyncio.sleep(5)  # Add a cooldown of 5 seconds between requests

    # No need for manual commit as PyGithub can manage commits

if __name__ == "__main__":
    asyncio.run(main())
