import asyncio
import json
from httpx import AsyncClient

async def get_latest_release(repo_url):
    async def get_version_url(releases):
        for release in releases:
            print("Checking release:", release['tag_name'])
            version = release['tag_name']
            for asset in release["assets"]:
                print("Checking asset:", asset["browser_download_url"])
                if asset["browser_download_url"].endswith(".jar") or asset["browser_download_url"].endswith(".apk"):
                    asset_url = asset['browser_download_url']
                    return version, asset_url
            print(f"No asset found for the {version}")
        return None, None

    api_url = f"{repo_url}/releases"
    print("API URL:", api_url)
    response = await AsyncClient().get(api_url)
    print("Response status code:", response.status_code)
    if response.status_code == 200:
        releases = response.json()
        print("Number of releases:", len(releases))
        version, asset_url = await get_version_url(releases)
        return version, asset_url
    else:
        print("Failed to fetch releases")
        return None, None

async def main():
    with open('bundle-sources.json') as file:
        sources = json.load(file)

    for source, repo in sources.items():
        print("Processing source:", source)
        patches_version, patches_asset_url = await get_latest_release(repo.get('patches'))
        print("Patches version:", patches_version)
        print("Patches asset URL:", patches_asset_url)
        integration_version, integration_asset_url = await get_latest_release(repo.get('integration'))
        print("Integration version:", integration_version)
        print("Integration asset URL:", integration_asset_url)
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
