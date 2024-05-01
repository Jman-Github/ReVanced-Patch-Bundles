import requests
import json

def get_latest_release(repo_url, prerelease=False):
    """
    Get the latest release information from a GitHub repository.

    Args:
        repo_url (str): The URL of the GitHub repository.
        prerelease (bool, optional): Whether to consider pre-releases. Defaults to False.

    Returns:
        tuple: A tuple containing the latest version and asset URL.
    """
    def get_version_url(release):
        """
        Extract version and asset URL from a release.

        Args:
            release (dict): Release information.

        Returns:
            tuple: A tuple containing the version and asset URL.
        """
        version = release['tag_name']
        for asset in release["assets"]:
            if (asset["browser_download_url"].find(".jar") != -1) or \
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
                if not release["prerelease"]:
                    version, asset_url = get_version_url(release)
                    return version, asset_url

def main():
    """
    Main function to update bundle files with latest release information.
    """
    with open('bundle-sources.json') as file:
        sources = json.load(file)

    for source in sources:
        patches_version, patches_asset_url = get_latest_release(
            sources.get(source).get('patches'), 
            sources.get(source).get('prerelease', False)
        )
        if patches_version is None or patches_asset_url is None:
            print(f"No releases found for patches of {source}")
            continue
        
        integration_version, integration_asset_url = get_latest_release(
            sources.get(source).get('integration'),
            sources.get(source).get('prerelease', False)
        )
        if integration_version is None or integration_asset_url is None:
            print(f"No releases found for integration of {source}")
            continue
        
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
    main()
