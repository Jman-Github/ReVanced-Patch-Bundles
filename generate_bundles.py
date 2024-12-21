import asyncio
import json
import subprocess
import os
import re
from httpx import AsyncClient, Timeout

GH_PAT = os.getenv('GH_PAT')

def is_empty(value):
    return value is None or (isinstance(value, str) and not value.strip())

def get_nested_value(d, key_path):
    keys = key_path.split('.')
    for k in keys:
        if isinstance(d, dict) and k in d:
            d = d[k]
        else:
            return None
    return d

def set_nested_value(d, key_path, value):
    keys = key_path.split('.')
    for k in keys[:-1]:
        if k not in d or not isinstance(d[k], dict):
            d[k] = {}
        d = d[k]
    d[keys[-1]] = value

def scenario_fields(info_dict):
    if all(key in info_dict for key in ["created_at", "description", "download_url", "signature_download_url", "version"]):
        return "rvp", ["created_at", "description", "download_url", "signature_download_url", "version"]
    elif "patches" in info_dict and "integrations" in info_dict:
        return "apkjar", ["patches.version", "patches.url", "integrations.version", "integrations.url"]
    else:
        return "rvp", ["created_at", "description", "download_url", "signature_download_url", "version"]

def get_value(d, field, scenario):
    if scenario == "rvp":
        return d.get(field, None)
    else:
        return get_nested_value(d, field)

def set_value(d, field, scenario, value):
    if scenario == "rvp":
        d[field] = value
    else:
        set_nested_value(d, field, value)

def determine_updates(new_data, fields, scenario):
    for field in fields:
        new_val = get_value(new_data, field, scenario)
        if not is_empty(new_val):
            return True
    return False

def merge_data(old_data, new_data, scenario, fields):
    updates = determine_updates(new_data, fields, scenario)

    print(f"[DEBUG] Scenario: {scenario}")
    print(f"[DEBUG] Fields: {fields}")
    print(f"[DEBUG] Updates detected? {updates}")
    for field in fields:
        old_val = get_value(old_data, field, scenario)
        new_val = get_value(new_data, field, scenario)
        print(f"[DEBUG] Field: {field}, Old: {old_val}, New: {new_val}")

    for field in fields:
        old_val = get_value(old_data, field, scenario)
        new_val = get_value(new_data, field, scenario)

        if updates:
            if is_empty(new_val):
                set_value(new_data, field, scenario, "N/A")
                print(f"[DEBUG] Updates=true; {field} empty => N/A")
            else:
                set_value(new_data, field, scenario, new_val)
                print(f"[DEBUG] Updates=true; {field} non-empty => {new_val}")
        else:
            if is_empty(new_val):
                if is_empty(old_val):
                    set_value(new_data, field, scenario, "N/A")
                    print(f"[DEBUG] Updates=false; {field} new empty, old empty => N/A")
                else:
                    set_value(new_data, field, scenario, old_val)
                    print(f"[DEBUG] Updates=false; {field} new empty, old not empty => keep old {old_val}")
            else:
                set_value(new_data, field, scenario, new_val)
                print(f"[DEBUG] Updates=false; {field} new not empty => {new_val}")

    for field in fields:
        final_val = get_value(new_data, field, scenario)
        print(f"[DEBUG] Final {field}: {final_val}")

    return new_data

async def get_latest_release(repo_url, prerelease, latest_flag=False):
    async def get_version_urls(release, file_types):
        version = release['tag_name']
        published_at = re.sub(r'[A-Za-z]+$', '', release['published_at'])
        description = release.get('body', '')
        download_urls = {ext: None for ext in file_types}
        signature_url = None

        for asset in release["assets"]:
            for ext in file_types:
                if asset["browser_download_url"].endswith(ext):
                    download_urls[ext] = asset['browser_download_url']
            if asset["browser_download_url"].endswith(".rvp.asc"):
                signature_url = asset['browser_download_url']

        return version, published_at, description, download_urls, signature_url

    api_url = f"{repo_url}/releases"
    headers = {'Authorization': f'token {GH_PAT}'}
    timeout = Timeout(connect=None, read=None, write=None, pool=None)

    async with AsyncClient(timeout=timeout, headers=headers) as client:
        response = await client.get(api_url)

    if response.status_code == 200:
        releases = response.json()
        if not releases:
            print(f"No releases found for {repo_url}")
            return None, None, None, None, None

        if latest_flag:
            filtered_releases = sorted(releases, key=lambda x: x["published_at"], reverse=True)
        elif prerelease:
            filtered_releases = sorted(
                (r for r in releases if r["prerelease"]),
                key=lambda x: x["published_at"],
                reverse=True
            )
        else:
            filtered_releases = sorted(
                (r for r in releases if not r["prerelease"]),
                key=lambda x: x["published_at"],
                reverse=True
            )

        file_types = [".jar", ".apk", ".rvp"]

        for release in filtered_releases:
            version, created_at, description, download_urls, signature_url = await get_version_urls(release, file_types)
            if any(download_urls[ext] for ext in file_types):
                return version, created_at, description, download_urls, signature_url

        print(f"No suitable release with .jar, .apk, or .rvp assets found for {repo_url}")
        return None, None, None, None, None

    else:
        print(f"Failed to fetch releases from {repo_url}")
        return None, None, None, None, None


async def fetch_release_data(source, repo):
    try:
        prerelease = repo.get('prerelease', False)
        latest_flag = repo.get('latest', False)
        
        (
            patches_version, 
            patches_created_at, 
            patches_description, 
            patches_download_urls, 
            patches_signature_url
        ) = await get_latest_release(repo.get('patches'), prerelease, latest_flag)

        if not patches_download_urls:
            return

        # Construct info_dict based on what we have
        if patches_download_urls[".rvp"]:
            # RVP scenario
            info_dict = {
                "created_at": patches_created_at,
                "description": patches_description,
                "download_url": patches_download_urls[".rvp"],
                "signature_download_url": patches_signature_url,
                "version": patches_version
            }

        else:
            jar_url = patches_download_urls[".jar"]
            if jar_url:
                (
                    integrations_version, 
                    integrations_created_at, 
                    integrations_description, 
                    integrations_download_urls, 
                    integrations_signature_url
                ) = await get_latest_release(repo.get('integration'), prerelease, latest_flag)

                if integrations_download_urls and integrations_download_urls[".apk"]:
                    apk_url = integrations_download_urls[".apk"]
                    info_dict = {
                        "patches": {
                            "version": patches_version,
                            "url": jar_url
                        },
                        "integrations": {
                            "version": integrations_version,
                            "url": apk_url
                        }
                    }
                else:
                    print(f"No relevant .apk asset found in integration repo for {source}")
                    return
            else:
                print(f"No relevant .rvp or .jar assets found for {source}")
                return

        base_source = source.replace('-dev', '').replace('-latest', '').replace('-stable', '')
        directory = os.path.join('patch-bundles', f"{base_source}-patch-bundles")
        os.makedirs(directory, exist_ok=True)

        filepath = os.path.join(directory, f'{source}-patches-bundle.json')

        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                old_data = json.load(f)
        else:
            old_data = {}

        scenario, fields = scenario_fields(info_dict)

        print(f"[DEBUG] Processing {filepath}")
        final_data = merge_data(old_data, info_dict, scenario, fields)

        with open(filepath, 'w') as file:
            json.dump(final_data, file, indent=2)
        print(f"Latest release information saved to {filepath}")

        subprocess.run(["git", "add", filepath], check=True)
        print(f"File {filepath} staged for commit.")

    except Exception as e:
        print(f"Error in fetch_release_data for {source}: {e}")


async def main():
    try:
        with open('bundle-sources.json') as file:
            sources = json.load(file)

        subprocess.run(["git", "config", "user.email", "41898282+github-actions[bot]@users.noreply.github.com"], check=True)
        subprocess.run(["git", "config", "user.name", "github-actions[bot]"], check=True)

        subprocess.run(["git", "pull", "origin", "bundles"], check=True)

        for source, repo in sources.items():
            await fetch_release_data(source, repo)
            await asyncio.sleep(0)
        
        subprocess.run(["git", "commit", "-m", "Update patch-bundle.json to latest"], check=True)
        
        subprocess.run(["git", "push", "origin", "bundles"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Subprocess failed: {e}")
    except Exception as e:
        print(f"Error in main: {e}")


if __name__ == "__main__":
    asyncio.run(main())
