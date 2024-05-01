import asyncio
import json
from httpx import AsyncClient

async def get_latest_release(repo_url, prerelease=False):
    async def get_version_url(release):
        version = release['tag_name']
        for asset in release["assets"]:
            if asset["browser_download_url"].endswith(".jar") or asset["browser_download_url"].endswith(".apk"):
                asset_url = asset['browser_download_url']
                return version, asset_url
        print(f"No asset found for the {version}")
        return None, None

    api_url = f"{repo_url}/releases"
    response = await AsyncClient().get(api_url)
    if response.status_code == 200:
        releases = response.json()
        target_release = None
        for release in releases:
            if prerelease == release["prerelease"]:
                target_release = release
                break
        if not target_release:
            print(f"No {'pre' if prerelease else ''}release found for {repo_url}")
            return None, None
        version, asset_url = await get_version_url(target_release)
        return version, asset_url

async def main():
    with open('bundle-sources.json') as file:
        sources = json.load(file)

    for source, repo in sources.items():
        patches_version, patches_asset_url = await get_latest_release(repo.get('patches'), repo.get('prerelease', False))
        if not patches_version:  # If no pre-release found, try regular release
            patches_version, patches_asset_url = await get_latest_release(repo.get('patches'))
        integration_version, integration_asset_url = await get_latest_release(repo.get('integration'), repo.get('prerelease', False))
        if not integration_version:  # If no pre-release found, try regular release
            integration_version, integration_asset_url = await get_latest_release(repo.get('integration'))
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

if __name__ == "__main__":
    asyncio.run(main())
