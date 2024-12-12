import asyncio
import json
import subprocess
import os
from httpx import AsyncClient, Timeout

GH_PAT = os.getenv('GH_PAT')

async def get_latest_release(repo_url, prerelease, latest_flag=False):
    async def get_version_urls(release, file_types):
        version = release['tag_name']
        created_at = release['published_at']
        description = release['body']
        download_urls = {ext: None for ext in file_types}
        signature_url = None

        for asset in release["assets"]:
            for ext in file_types:
                if asset["browser_download_url"].endswith(ext):
                    download_urls[ext] = asset['browser_download_url']
            if asset["browser_download_url"].endswith(".rvp.asc"):
                signature_url = asset['browser_download_url']

        return version, created_at, description, download_urls, signature_url

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
            file_types = [".jar", ".apk", ".rvp"]
            return await get_version_urls(target_release, file_types)
        else:
            print(f"No {'pre' if prerelease else ''}release found for {repo_url}")
            return None, None, None, None, None
    else:
        print(f"Failed to fetch releases from {repo_url}")
        return None, None, None, None, None

async def fetch_release_data(source, repo):
    try:
        prerelease = repo.get('prerelease', False)
        latest_flag = repo.get('latest', False)
        
        patches_version, created_at, description, download_urls, signature_url = await get_latest_release(repo.get('patches'), prerelease, latest_flag)

        if download_urls[".rvp"]:
            # Create .rvp-specific JSON format
            info_dict = {
                "createdAt": created_at
                "description": description or "",
                "downloadUrl": download_urls[".rvp"],
                "signatureDownloadUrl": signature_url if signature_url else "null",
                "version": patches_version
            }
        elif download_urls[".jar"] or download_urls[".apk"]:
            # Create .jar/.apk-specific JSON format
            integrations_version, _, integration_asset_url = await get_latest_release(repo.get('integration'), prerelease, latest_flag)
            info_dict = {
                "patches": {
                    "version": patches_version,
                    "url": download_urls[".jar"]
                },
                "integrations": {
                    "version": integrations_version,
                    "url": integration_asset_url
                }
            }
        else:
            print(f"No relevant assets found for {source}")
            return

        base_source = source.replace('-dev', '').replace('-latest', '').replace('-stable', '')
        directory = os.path.join('patch-bundles', f"{base_source}-patch-bundles")
        os.makedirs(directory, exist_ok=True)
        
        filepath = os.path.join(directory, f'{source}-patches-bundle.json')
        with open(filepath, 'w') as file:
            json.dump(info_dict, file, indent=2)
        print(f"Latest release information saved to {filepath}")
        
        # Stage the changes made to the JSON file
        subprocess.run(["git", "add", filepath], check=True)
        print(f"File {filepath} staged for commit.")
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
