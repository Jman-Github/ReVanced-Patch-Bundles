import requests
import json

def get_latest_release(repo_url, prerelease = False):
    def get_version_url(release):
        version = release['tag_name']
        for asset in release["assets"]:
            if (asset["browser_download_url"].find(".jar") != -1) or\
               (asset["browser_download_url"].find(".apk") != -1):
                asset_url = asset['browser_download_url']
                return version, asset_url
        return None, None

    api_url = f"{repo_url}/releases"
    response = requests.get(api_url)
    if response.status_code == 200:
        releases = response.json()
        if prerelease:
            for release in releases:
                if release["prerelease"]:
                    version, asset_url = get_version_url(release)
                    return version, asset_url
        else:
            for release in releases:
                if release["prerelease"] is False:
                    version, asset_url = get_version_url(release)
                    return version, asset_url



def main():
    with open('sources.json') as file:
        sources = json.load(file)

    for source in sources:
        patches_version, patches_asset_url = get_latest_release(sources.get(source).get('patches'), 
                               sources.get(source).get('prerelease', False))
        integration_version, integration_asset_url = get_latest_release(sources.get(source).get('integration'),
                               sources.get(source).get('prerelease', False))
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
        with open(f'{source}-bundle.json', 'w') as file:
            json.dump(info_dict, file, indent=2)
        print(f"Latest release information saved to {source}-bundle.json")

if __name__ == "__main__":
    main()
