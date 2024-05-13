import asyncio
import json
import subprocess
from httpx import AsyncClient, Timeout

async def get_latest_release(repo_url, prerelease, latest_flag=False):
    async def get_version_url(release):
        version = release['tag_name']
        for asset in release["assets"]:
            if asset["browser_download_url"].endswith(".jar") or asset["browser_download_url"].endswith(".apk"):
                asset_url = asset['browser_download_url']
                return version, asset_url
        print(f"No asset found for the {version}")
        return None, None

    api_url = f"{repo_url}/releases"
    timeout = Timeout(connect=30.0, read=60.0, write=None, pool=None)
    response = await AsyncClient().get(api_url, timeout=timeout)
    if response.status_code == 200:
        releases = response.json()
        if latest_flag:
            target_release = max(releases, key=lambda x: x["published_at"])
        else:
            if prerelease:
                target_release = max((release for release in releases if release["prerelease"]), key=lambda x: x["published_at"], default=None)
            else:
                target_release = max((release for release in releases if not release["prerelease"]), key=lambda x: x["published_at"], default=None)
        
        if target_release:
            version, asset_url = await get_version_url(target_release)
            return version, asset_url
        else:
            print(f"No {'pre' if prerelease else ''}release found for {repo_url}")
            return None, None
    else:
        print("Failed to fetch releases")
        return None, None

async def main():
    with open('bundle-sources.json') as file:
        sources = json.load(file)

    # Configure Git user name and email
    subprocess.run(["git", "config", "user.email", "41898282+github-actions[bot]@users.noreply.github.com"])
    subprocess.run(["git", "config", "user.name", "github-actions[bot]"])

    for source, repo in sources.items():
        prerelease = repo.get('prerelease', False)
        latest_flag = repo.get('latest', False)  # Retrieving the 'latest' flag
        patches_version, patches_asset_url = await get_latest_release(repo.get('patches'), prerelease, latest_flag)
        integration_version, integration_asset_url = await get_latest_release(repo.get('integration'), prerelease, latest_flag)
        
        # Check if patches_version, patches_asset_url, integration_version, and integration_asset_url are not None
        if patches_version is not None and patches_asset_url is not None and integration_version is not None and integration_asset_url is not None:
            info_dict = {
                "patches": {
                    "version": patches_version,
                    "url": patches_asset_url
                },
                "integrations": {
                    "version": integration_version,
                    "url": integration_asset_url
                }
            }
            with open(f'{source}-patches-bundle.json', 'w') as file:
                json.dump(info_dict, file, indent=2)
            print(f"Latest release information saved to {source}-patches-bundle.json")
            
            # Stage the changes made to the JSON file
            subprocess.run(["git", "add", f"{source}-patches-bundle.json"])
        else:
            print(f"Error: Unable to fetch release information for {source}")
    
    # Commit the changes
    subprocess.run(["git", "commit", "-m", "Update patch-bundle.json to latest"])
    

if __name__ == "__main__":
    asyncio.run(main())