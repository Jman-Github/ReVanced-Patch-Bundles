import asyncio
import json
import subprocess
import os
from httpx import AsyncClient, Timeout

GH_PAT = os.getenv('GH_PAT')

async def get_latest_release(repo_url, prerelease=False, latest_flag=False):
    """Fetch the latest release information from a GitHub repository."""
    async def get_version_urls(release):
        version = release.get('tag_name')
        patches_url = next(
            (asset['browser_download_url'] for asset in release['assets'] if asset['browser_download_url'].endswith('.jar')), None
        )
        integrations_url = next(
            (asset['browser_download_url'] for asset in release['assets'] if asset['browser_download_url'].endswith('.apk')), None
        )
        return version, patches_url, integrations_url

    api_url = f"{repo_url}/releases"
    headers = {'Authorization': f'token {GH_PAT}'}
    timeout = Timeout(30.0)  # Set a 30-second timeout for all operations

    async with AsyncClient(timeout=timeout, headers=headers) as client:
        response = await client.get(api_url)
    
    if response.status_code == 200:
        releases = response.json()
        if latest_flag:
            target_release = max(releases, key=lambda x: x.get("published_at", ""))
        elif prerelease:
            target_release = max(
                (release for release in releases if release.get("prerelease", False)),
                key=lambda x: x.get("published_at", ""),
                default=None,
            )
        else:
            target_release = max(
                (release for release in releases if not release.get("prerelease", False)),
                key=lambda x: x.get("published_at", ""),
                default=None,
            )

        if target_release:
            return await get_version_urls(target_release)
        print(f"No {'pre' if prerelease else ''}release found for {repo_url}")
    else:
        print(f"Failed to fetch releases from {repo_url}. HTTP status: {response.status_code}")
    
    return None, None, None

async def fetch_release_data(source, repo):
    """Fetch and save release data for a given source and repository."""
    try:
        prerelease = repo.get('prerelease', False)
        latest_flag = repo.get('latest', False)

        patches_version, patches_asset_url, _ = await get_latest_release(repo.get('patches'), prerelease, latest_flag)
        integrations_version, _, integration_asset_url = await get_latest_release(repo.get('integration'), prerelease, latest_flag)

        if patches_version and patches_asset_url and integrations_version and integration_asset_url:
            info_dict = {
                "patches": {"version": patches_version, "url": patches_asset_url},
                "integrations": {"version": integrations_version, "url": integration_asset_url},
            }

            base_source = source.replace('-dev', '').replace('-latest', '').replace('-stable', '')
            directory = os.path.join('patch-bundles', f"{base_source}-patch-bundles")
            os.makedirs(directory, exist_ok=True)

            filepath = os.path.join(directory, f'{source}-patches-bundle.json')

            if os.path.exists(filepath):
                with open(filepath, 'r') as file:
                    existing_data = json.load(file)
                if info_dict == existing_data:
                    print(f"No changes detected for {source}, skipping...")
                    return

            with open(filepath, 'w') as file:
                json.dump(info_dict, file, indent=2)
            print(f"Latest release information saved to {filepath}")

            subprocess.run(["git", "add", filepath], check=True)
        else:
            print(f"Error: Missing release information for {source}")
    except Exception as e:
        print(f"Error in fetch_release_data for {source}: {e}")

async def main():
    """Main entry point for the script."""
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

        # Commit the changes if any files were staged
        commit_result = subprocess.run(
            ["git", "commit", "-m", "Update patch-bundle.json to latest"], capture_output=True, text=True
        )
        if "nothing to commit" in commit_result.stdout:
            print("No changes to commit.")
        else:
            # Push the changes to the remote branch
            subprocess.run(["git", "push", "origin", "bundles"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Git subprocess failed: {e}")
    except Exception as e:
        print(f"Error in main: {e}")

if __name__ == "__main__":
    asyncio.run(main())
