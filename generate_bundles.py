import asyncio
import json
import subprocess
import os
import logging
from github import Github

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def install_dependencies():
    logger.info("Installing required dependencies")
    subprocess.run(["pip", "install", "-r", "requirements.txt"])

def get_github_pat():
    pat = os.getenv('GH_PAT')
    if not pat:
        raise ValueError("GitHub PAT is not set in the environment variables")
    return pat

async def get_latest_release(repo_url, prerelease, latest_flag=False):
    try:
        logger.debug(f"Fetching releases for {repo_url}")
        gh = Github(get_github_pat())
        repo = gh.get_repo(repo_url.split("/")[-2:])

        releases = repo.get_releases()

        if latest_flag:
            target_release = max(releases, key=lambda x: x.published_at)
        elif prerelease:
            target_release = max((release for release in releases if release.prerelease), key=lambda x: x.published_at, default=None)
        else:
            target_release = max((release for release in releases if not release.prerelease), key=lambda x: x.published_at, default=None)

        if target_release:
            logger.debug(f"Found latest release: {target_release.tag_name}")
            patches_url = next((asset.browser_download_url for asset in target_release.assets if asset.name.endswith(".jar")), None)
            integrations_url = next((asset.browser_download_url for asset in target_release.assets if asset.name.endswith(".apk")), None)
            return target_release.tag_name, patches_url, integrations_url
        else:
            logger.warning(f"No {'pre' if prerelease else ''}release found for {repo_url}")
            return None, None, None

    except Exception as e:
        logger.error(f"Error fetching releases for {repo_url}: {str(e)}")
        return None, None, None

async def fetch_release_data(source, repo):
    logger.debug(f"Fetching release data for {source}")
    prerelease = repo.get('prerelease', False)
    latest_flag = repo.get('latest', False)
    patches_version, patches_asset_url, integrations_url = await get_latest_release(repo.get('patches'), prerelease, latest_flag)
    integrations_version, integrations_asset_url, _ = await get_latest_release(repo.get('integration'), prerelease, latest_flag)

    if patches_version and patches_asset_url and integrations_version and integrations_asset_url:
        logger.info(f"Successfully fetched release data for {source}")
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
        logger.info(f"Saved release information to {source}-patches-bundle.json")

        subprocess.run(["git", "add", f"{source}-patches-bundle.json"])  # Stage the changes made to the JSON file
    else:
        logger.error(f"Error fetching release information for {source}")

async def main():
    logger.info("Starting script execution")
    with open('bundle-sources.json') as file:
        sources = json.load(file)

    # Configure Git user name and email
    subprocess.run(["git", "config", "user.email", "41898282+github-actions[bot]@users.noreply.github.com"])
    subprocess.run(["git", "config", "user.name", "github-actions[bot]"])

    for source, repo in sources.items():
        logger.debug(f"Processing source: {source}")
        await fetch_release_data(source, repo)
        await asyncio.sleep(15)  # 15-second cooldown between requests

    # Commit the changes
    logger.info("Committing changes")
    subprocess.run(["git", "commit", "-m", "Update patch-bundle.json to latest"])

if __name__ == "__main__":
    try:
        install_dependencies()
        asyncio.run(main())
    except ValueError as e:
        logger.error(str(e))
