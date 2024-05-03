import json
import requests

# Load bundle sources from bundle-sources.json
with open("bundle-sources.json", "r") as json_file:
    bundle_sources = json.load(json_file)

for source_name, source_info in bundle_sources.items():
    print(f"Processing source: {source_name}")
    
    # Get patches info
    print("API URL:", f"{source_info['patches']}/releases")
    response = requests.get(f"{source_info['patches']}/releases")
    print("Response status code:", response.status_code)
    releases = response.json()
    print("Number of releases:", len(releases))
    
    # Fetch patches
    patches_info = {}
    for release in releases:
        print("Checking release:", release['tag_name'])
        for asset in release['assets']:
            if asset['name'].endswith('.jar'):
                patches_info['version'] = release['tag_name']
                patches_info['url'] = asset['browser_download_url']
                break
    print("Patches version:", patches_info.get('version', 'Not Found'))
    print("Patches asset URL:", patches_info.get('url', 'Not Found'))
    
    # Get integrations info
    print("API URL:", f"{source_info['integration']}/releases")
    response = requests.get(f"{source_info['integration']}/releases")
    print("Response status code:", response.status_code)
    releases = response.json()
    print("Number of releases:", len(releases))
    
    # Fetch integrations
    integrations_info = {}
    for release in releases:
        print("Checking release:", release['tag_name'])
        for asset in release['assets']:
            if asset['name'].endswith('.apk'):
                integrations_info['version'] = release['tag_name']
                integrations_info['url'] = asset['browser_download_url']
                break
    print("Integration version:", integrations_info.get('version', 'Not Found'))
    print("Integration asset URL:", integrations_info.get('url', 'Not Found'))
    
    # Save information to a JSON file
    bundle_info = {
        "patches_version": patches_info.get('version', 'Not Found'),
        "patches_url": patches_info.get('url', 'Not Found'),
        "integration_version": integrations_info.get('version', 'Not Found'),
        "integration_url": integrations_info.get('url', 'Not Found')
    }
    with open(f"{source_name}-patches-bundle.json", "w") as json_file:
        json.dump(bundle_info, json_file, indent=4)

print("Latest release information saved to *_patches-bundle.json")
