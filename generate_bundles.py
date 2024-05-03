import json
import os
import requests

def get_latest_release(api_url):
    response = requests.get(api_url)
    if response.status_code == 200:
        releases = response.json()
        if releases:
            latest_release = releases[0]
            version = latest_release['tag_name']
            assets = latest_release['assets']
            asset_url = None
            for asset in assets:
                if asset['name'].endswith(('.jar', '.apk')):
                    asset_url = asset['browser_download_url']
                    break
            return version, asset_url
    return None, None

def update_bundle(source_name, patches_version, patches_asset_url, integration_version, integration_asset_url):
    filename = f"{source_name}-patches-bundle.json"
    data = {
        "patches_version": patches_version,
        "patches_asset_url": patches_asset_url,
        "integration_version": integration_version,
        "integration_asset_url": integration_asset_url
    }
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)

def process_source(source_name, patches_api_url, integration_api_url):
    print(f"Processing source: {source_name}")
    
    patches_version, patches_asset_url = get_latest_release(patches_api_url)
    print(f"Patches version: {patches_version}")
    print(f"Patches asset URL: {patches_asset_url}")
    
    integration_version, integration_asset_url = get_latest_release(integration_api_url)
    print(f"Integration version: {integration_version}")
    print(f"Integration asset URL: {integration_asset_url}")
    
    update_bundle(source_name, patches_version, patches_asset_url, integration_version, integration_asset_url)
    print(f"Latest release information saved to {source_name}-patches-bundle.json")

sources = {
    "piko": {
        "patches_api_url": "https://api.github.com/repos/crimera/piko/releases",
        "integration_api_url": "https://api.github.com/repos/crimera/revanced-integrations/releases"
    },
    "anddea": {
        "patches_api_url": "https://api.github.com/repos/anddea/revanced-patches/releases",
        "integration_api_url": "https://api.github.com/repos/anddea/revanced-integrations/releases"
    },
    "experimental": {
        "patches_api_url": "https://api.github.com/repos/Aunali321/ReVancedExperiments/releases",
        "integration_api_url": "https://api.github.com/repos/revanced/revanced-integrations/releases"
    },
    "privacy": {
        "patches_api_url": "https://api.github.com/repos/jkennethcarino/privacy-revanced-patches/releases",
        "integration_api_url": "https://api.github.com/repos/jkennethcarino/privacy-revanced-integrations/releases"
    },
    "rex": {
        "patches_api_url": "https://api.github.com/repos/YT-Advanced/ReX-patches/releases",
        "integration_api_url": "https://api.github.com/repos/YT-Advanced/ReX-integrations/releases"
    },
    "twitter": {
        "patches_api_url": "https://api.github.com/repos/IndusAryan/twitter-patches/releases",
        "integration_api_url": "https://api.github.com/repos/ReVanced/revanced-integrations/releases"
    },
    "rufusin": {
        "patches_api_url": "https://api.github.com/repos/rufusin/revanced-patches/releases",
        "integration_api_url": "https://api.github.com/repos/rufusin/revanced-integrations/releases"
    },
    "dropped": {
        "patches_api_url": "https://api.github.com/repos/indrastorms/dropped-patches/releases",
        "integration_api_url": "https://api.github.com/repos/ReVanced/revanced-integrations/releases"
    }
}

for source_name, urls in sources.items():
    process_source(source_name, urls["patches_api_url"], urls["integration_api_url"])
