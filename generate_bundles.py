import asyncio
import json
import subprocess
from httpx import AsyncClient, Timeout, HTTPStatusError
import time
import os

# Function to get the PAT from an environment variable or a secure location
def get_github_pat():
    return os.getenv('GH_PAT')  # Ensure you have set this environment variable

async def get_latest_release(repo_url, prerelease, latest_flag=False):
    async def get_version_urls(release):
        version = release['tag_name']
        patches_url = None
        integrations_url = None
        for asset in release["assets"]:
            if asset["browser_download_url"].endswith(".jar"):
                patches_url = asset['browser_download_url']
            elif asset["browser_download_url"].endswith(".apk"):
                integrations_url = asset['browser_download_url']
        return version, patches_url, integrations_url

    api_url = f"{repo_url}/releases"
    timeout = Timeout(connect=None, read=None, write=None, pool=None)  # No timeouts
    headers = {"Authorization": f"token {get_github_pat()}"}
    
    async with AsyncClient(timeout=timeout, headers=headers) as client:
        try:
            response = await client.get(api_url)
            response.raise_for_status()
            
            # Handle rate limit
            rate_limit_remaining = int(response.headers.get('X-RateLimit-Remaining', 1))
            if rate_limit_remaining == 0:
                reset_time = int(response.headers.get('X-RateLimit-Reset', time.time()))
                sleep_time = reset_time - time.time() + 1
                print(f"Rate limit reached. Sleeping for {sleep_time} seconds.")
                await asyncio.sleep(sleep_time)
                return await get_latest_release(repo_url, prerelease, latest_flag)

            releases = response.json()
            if latest_flag:
                target_release = max(releases, key=lambda x: x["published_at"])
            elif prerelease:
                target_release = max((release for release in releases if release["prerelease"]), key=lambda x: x["published_at"], default=None)
            else:
                target_release = max((release for release in releases if not release["prerelease"]), key=lambda x: x["published_at"], default=None)

            if target_release:
                return await get_version_urls(target_release)
            else:
                print(f"No {'pre' if prerelease else ''}release found for {repo_url}")
                return None, None, None

        except HTTPStatusError as e:
            if e.response.status_code == 403:
                print(f"Rate limit reached or access denied for {repo_url}")
            else:
                print(f"Failed to fetch releases from {repo_url}: {e.response.status_code} {e.response.text}")
            return None, None, None
        except Exception as e:
            print(f"Failed to fetch releases from {repo_url}: {str(e)}")
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
    asyncio.run(main())
