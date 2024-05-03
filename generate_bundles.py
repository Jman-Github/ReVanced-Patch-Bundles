import asyncio
import json
from httpx import AsyncClient

async def get_latest_release(repo_url):
    async def get_version_url(release):
        if release is None:
            print("No release found")
            return None, None

        version = release['tag_name']
        for asset in release["assets"]:
            if asset["browser_download_url"].endswith(".jar") or asset["browser_download_url"].endswith(".apk"):
                asset_url = asset['browser_download_url']
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

    latest_prerelease = None
    latest_regular_release = None
    for release in releases:
        if release["prerelease"]:
            if not latest_prerelease or release["published_at"] > latest_prerelease["published_at"]:
                latest_prerelease = release
        else:
            if not latest_regular_release or release["published_at"] > latest_regular_release["published_at"]:
                latest_regular_release = release
    if latest_regular_release and (not latest_prerelease or latest_regular_release["published_at"] > latest_prerelease["published_at"]):
        target_release = latest_regular_release
    else:
        target_release = latest_prerelease
    version, asset_url = await get_version_url(target_release)
    return version, asset_url

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
