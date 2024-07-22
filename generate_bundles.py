import asyncio
import json
import subprocess
import time
import os
from github import Github

# Function to get the PAT from an environment variable
def get_github_pat():
    pat = os.getenv('GH_PAT')
    if not pat:
        raise ValueError("GitHub PAT is not set in the environment variables")
    return pat

async def get_latest_release(repo_url, prerelease, latest_flag=False):
    try:
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
            patches_url = None
            integrations_url = None
            for asset in target_release.assets:
                if asset.name.endswith(".jar"):
                    patches_url = asset.browser_download_url
                elif asset.name.endswith(".apk"):
                    integrations_url = asset.browser_download_url
            return target_release.tag_name, patches_url, integrations_url
        else:
            print(f"No {'pre' if prerelease else ''}release found for {repo_url}")
            return None, None, None

    except Exception as e:
        print(f"Error fetching releases for {repo_url}: {str(e)}")
        return None, None, None

async def fetch_release_data(source, repo):
    prerelease = repo.get('prerelease', False)
    latest_flag = repo.get('latest', False)
    patches_version, patches_asset_url, integrations_url = await get_latest_release(repo.get('patches'), prerelease, latest_flag)
    integrations_version, integrations_asset_url, _ = await get_latest_release(repo.get('integration'), prerelease, latest_flag)

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
        print(f"Latest release information saved to {source}-patches-bundle.json")

        # Stage the changes made to the JSON file
        subprocess.run(["git", "add", f"{source}-patches-bundle.json"])
    else:
        print(f"Error: Unable to fetch release information for {source}")

async def main():
    with open('bundle-sources.json') as file:
        sources = json.load(file)

    # Configure Git user name and email
    subprocess.run(["git", "config", "user.email", "41898282+github-actions[bot]@users.noreply.github.com"])
    subprocess.run(["git", "config", "user.name", "github-actions[bot]"])

    for source, repo in sources.items():
        await fetch_release_data(source, repo)
        await asyncio.sleep(15)  # 15-second cooldown between requests

    # Commit the changes
    subprocess.run(["git", "commit", "-m", "Update patch-bundle.json to latest"])

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except ValueError as e:
        print(str(e))
