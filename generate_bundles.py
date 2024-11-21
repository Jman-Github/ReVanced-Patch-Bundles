import asyncio
import json
import subprocess
import os
from httpx import AsyncClient, Timeout

GH_PAT = os.getenv('GH_PAT')

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
    headers = {'Authorization': f'token {GH_PAT}'}
    timeout = Timeout(connect=None, read=None, write=None, pool=None)
    async with AsyncClient(timeout=timeout, headers=headers) as client:
        response = await client.get(api_url)
    if response.status_code == 200:
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
    else:
        print(f"Failed to fetch releases from {repo_url}: {response.text}")
        return None, None, None

async def fetch_release_data(source, repo):
    try:
        prerelease = repo.get('prerelease', False)
        latest_flag = repo.get('latest', False)
        patches_version, patches_asset_url, _ = await get_latest_release(repo.get('patches'), prerelease, latest_flag)
        integrations_version, _, integration_asset_url = await get_latest_release(repo.get('integration'), prerelease, latest_flag)
        
        if patches_version and patches_asset_url and integrations_version and integration_asset_url:
            info_dict = {
                "patches": {
                    "version": patches_version,
                    "url": patches_asset_url
                },
                "integrations": {
                    "version": integrations_version,
                    "url": integration_asset_url
                }
            }

            base_source = source.replace('-dev', '').replace('-latest', '').replace('-stable', '')
            directory = os.path.join('patch-bundles', f"{base_source}-patch-bundles")
            os.makedirs(directory, exist_ok=True)
            
            filepath = os.path.join(directory, f'{source}-patches-bundle.json')
            
            # Check for existing content
            if os.path.exists(filepath):
                with open(filepath, 'r') as file:
                    existing_data = file.read()
                if json.dumps(info_dict, indent=2) == existing_data:
                    print(f"No changes detected for {filepath}. Skipping write.")
                    return

            with open(filepath, 'w') as file:
                json.dump(info_dict, file, indent=2)
            print(f"Latest release information saved to {filepath}")
            
            # Stage the changes made to the JSON file
            subprocess.run(["git", "add", filepath], check=True)
        else:
            print(f"Error: Unable to fetch release information for {source}")
    except Exception as e:
        print(f"Error in fetch_release_data for {source}: {e}")

async def main():
    try:
        with open('bundle-sources.json') as file:
            sources = json.load(file)

        # Configure Git user name and email
        subprocess.run(["git", "config", "user.email", "41898282+github-actions[bot]@users.noreply.github.com"], check=True)
        subprocess.run(["git", "config", "user.name", "github-actions[bot]"], check=True)

        # Pull the latest changes from the remote branch
        subprocess.run(["git", "pull", "origin", "bundles"], check=True)

        for source, repo in sources.items():
            await fetch_release_data(source, repo)
            await asyncio.sleep(0)
        
        # Commit the changes
        subprocess.run(["git", "commit", "-m", "Update patch-bundle.json to latest"], check=True)
        
        # Push the changes to the remote branch
        subprocess.run(["git", "push", "origin", "bundles"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Subprocess failed: {e}")
    except Exception as e:
        print(f"Error in main: {e}")

if __name__ == "__main__":
    asyncio.run(main())