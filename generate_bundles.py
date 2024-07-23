import asyncio
import json
import subprocess
from httpx import AsyncClient, Timeout
import os

def get_gh_pat():
    return os.getenv('GH_PAT')

async def print_rate_limit_status(client):
    rate_limit_url = "https://api.github.com/rate_limit"
    response = await client.get(rate_limit_url)
    if response.status_code == 200:
        rate_limit = response.json()
        print(f"Rate limit: {rate_limit['rate']['remaining']} remaining out of {rate_limit['rate']['limit']}")
    else:
        print(f"Failed to fetch rate limit status: {response.status_code} - {response.text}")

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
    print(f"Fetching from URL: {api_url}")
    timeout = Timeout(connect=None, read=None, write=None, pool=None)
    headers = {"Authorization": f"token {get_gh_pat()}"}
    async with AsyncClient(timeout=timeout, headers=headers) as client:
        await print_rate_limit_status(client)
        response = await client.get(api_url)
        print(f"API response status: {response.status_code} - {response.text}")

    if response.status_code == 200:
        releases = response.json()
        if latest_flag:
            target_release = max(releases, key=lambda x: x["published_at"])
        elif prerelease:
            target_release = max((release for release in releases if release["prerelease"]), key=lambda x: x["published_at"], default=None)
        else:
            target_release = max((release for release in releases if not release["prerelease"]), key=lambda x: x["published_at"], default=None)
        
        if target_release:
            version, patches_url, integrations_url = await get_version_urls(target_release)
            if not patches_url or not integrations_url:
                print(f"Release {target_release['tag_name']} does not contain required assets (.jar or .apk)")
            return version, patches_url, integrations_url
        else:
            print(f"No {'pre' if prerelease else ''}release found for {repo_url}")
            return None, None, None
    else:
        print(f"Failed to fetch releases from {repo_url} - {response.text}")
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
        
        subprocess.run(["git", "add", f"{source}-patches-bundle.json"])
    else:
        print(f"Error: Unable to fetch release information for {source}. Check if the releases contain .jar and .apk assets.")

async def main():
    with open('bundle-sources.json') as file:
        sources = json.load(file)

    subprocess.run(["git", "config", "user.email", "41898282+github-actions[bot]@users.noreply.github.com"])
    subprocess.run(["git", "config", "user.name", "github-actions[bot]"])

    for source, repo in sources.items():
        await fetch_release_data(source, repo)
        await asyncio.sleep(5)  # Add a cooldown of 5 seconds between requests
    
    subprocess.run(["git", "commit", "-m", "Update patch-bundle.json to latest"])

if __name__ == "__main__":
    asyncio.run(main())
