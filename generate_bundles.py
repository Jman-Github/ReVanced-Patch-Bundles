import asyncio
import json
from httpx import AsyncClient

async def get_latest_release(repo_url):
    async def get_version_url(release):
        if release is None or 'tag_name' not in release:
            print("No valid release found")
            return None, None

        version = release['tag_name']

        assets = release.get("assets", [])
        if not assets:
            print(f"No assets found for the {version}")
            return None, None

        for asset in assets:
            if asset.get("browser_download_url", "").endswith(".jar") or asset.get("browser_download_url", "").endswith(".apk"):
                asset_url = asset.get('browser_download_url')
                return version, asset_url
        print(f"No asset found for the {version}")
        return None, None

    api_url = f"{repo_url}/releases"
    releases = []
    page = 1
    while True:
        response = await AsyncClient().get(api_url, params={"page": page})
        if response.status_code == 200:
            page_releases = response.json()
            if not page_releases:
                break
            releases.extend(page_releases)
            page += 1
        else:
            break

    latest_release = None
    for release in releases:
        if release.get("prerelease"):
            if not latest_release or release.get("published_at") > latest_release.get("published_at", ""):
                latest_release = release
        else:
            if not latest_release or release.get("published_at") > latest_release.get("published_at", ""):
                latest_release = release

    if latest_release:
        version, asset_url = await get_version_url(latest_release)
        return version, asset_url
    else:
        print("No latest release found")
        return None, None

async def main():
    with open('bundle-sources.json') as file:
        sources = json.load(file)

    for source, repo in sources.items():
        patches_version, patches_asset_url = await get_latest_release(repo.get('patches'))
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
