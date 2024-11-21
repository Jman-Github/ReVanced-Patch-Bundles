import asyncio
import json
import os
import subprocess
from pathlib import Path
from httpx import AsyncClient, Timeout, HTTPStatusError

GH_PAT = os.getenv("GH_PAT")
HEADERS = {"Authorization": f"token {GH_PAT}"}
TIMEOUT = Timeout(connect=10, read=10, write=10, pool=10)


async def fetch_api(url: str) -> dict:
    """Fetch data from the GitHub API with error handling."""
    async with AsyncClient(timeout=TIMEOUT, headers=HEADERS) as client:
        response = await client.get(url)
        try:
            response.raise_for_status()
            return response.json()
        except HTTPStatusError as e:
            print(f"Failed to fetch {url}: {e.response.status_code} - {e.response.text}")
            return {}


async def get_latest_release(repo_url: str, prerelease: bool = False, latest: bool = False) -> tuple:
    """
    Fetch the latest or prerelease version details from a GitHub repository.
    Returns a tuple of (version, patches_url, integrations_url).
    """
    releases = await fetch_api(f"{repo_url}/releases")
    if not releases:
        return None, None, None

    filtered_releases = (
        [r for r in releases if r["prerelease"]] if prerelease else [r for r in releases if not r["prerelease"]]
    )
    if latest:
        target_release = max(releases, key=lambda x: x["published_at"], default=None)
    else:
        target_release = max(filtered_releases, key=lambda x: x["published_at"], default=None)

    if not target_release:
        print(f"No {'pre' if prerelease else ''}release found for {repo_url}")
        return None, None, None

    version = target_release["tag_name"]
    patches_url = next((a["browser_download_url"] for a in target_release["assets"] if a["name"].endswith(".jar")), None)
    integrations_url = next((a["browser_download_url"] for a in target_release["assets"] if a["name"].endswith(".apk")), None)

    return version, patches_url, integrations_url


async def process_source(source: str, repo: dict, base_dir: Path):
    """
    Process a single source by fetching the latest release data
    and saving it to a JSON file if there are updates.
    """
    try:
        patches_version, patches_url, _ = await get_latest_release(repo["patches"], repo.get("prerelease", False))
        integrations_version, _, integrations_url = await get_latest_release(
            repo["integration"], repo.get("prerelease", False)
        )

        if not (patches_version and patches_url and integrations_version and integrations_url):
            print(f"Skipping {source}: Incomplete release data.")
            return

        # Build data structure
        bundle_data = {
            "patches": {"version": patches_version, "url": patches_url},
            "integrations": {"version": integrations_version, "url": integrations_url},
        }

        # Prepare output directory and file
        sanitized_source = source.replace("-dev", "").replace("-latest", "").replace("-stable", "")
        output_dir = base_dir / f"{sanitized_source}-patch-bundles"
        output_dir.mkdir(parents=True, exist_ok=True)
        output_file = output_dir / f"{source}-patches-bundle.json"

        # Avoid overwriting files if content is unchanged
        if output_file.exists():
            with output_file.open("r") as existing_file:
                if json.load(existing_file) == bundle_data:
                    print(f"No changes detected for {output_file}. Skipping...")
                    return

        # Save updated content
        with output_file.open("w") as new_file:
            json.dump(bundle_data, new_file, indent=2)

        print(f"Updated bundle for {source}: {output_file}")

        # Stage changes in Git
        subprocess.run(["git", "add", str(output_file)], check=True)

    except Exception as e:
        print(f"Error processing {source}: {e}")


async def main():
    base_dir = Path("patch-bundles")
    base_dir.mkdir(exist_ok=True)

    try:
        # Load sources from JSON
        with open("bundle-sources.json", "r") as f:
            sources = json.load(f)

        # Configure Git
        subprocess.run(["git", "config", "user.email", "41898282+github-actions[bot]@users.noreply.github.com"], check=True)
        subprocess.run(["git", "config", "user.name", "github-actions[bot]"], check=True)

        # Pull latest changes
        subprocess.run(["git", "pull", "origin", "bundles"], check=True)

        # Process each source asynchronously
        await asyncio.gather(*(process_source(source, repo, base_dir) for source, repo in sources.items()))

        # Commit and push changes if any
        if subprocess.run(["git", "diff", "--cached", "--quiet"]).returncode != 0:
            subprocess.run(["git", "commit", "-m", "Update patch-bundle.json to latest"], check=True)
            subprocess.run(["git", "push", "origin", "bundles"], check=True)
        else:
            print("No changes to commit.")

    except subprocess.CalledProcessError as e:
        print(f"Git command failed: {e}")
    except Exception as e:
        print(f"Error in main: {e}")


if __name__ == "__main__":
    asyncio.run(main())