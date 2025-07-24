import sys
import os
import requests
import base64

def update_readme(artifact_url):
    headers = {
        "Authorization": f"Bearer {os.environ['GIT_TOKEN']}",
        "Content-Type": "application/json"
    }
    branch = os.environ.get("TARGET_BRANCH") or os.environ.get("GITHUB_REF_NAME", "bundles")
    response = requests.get(
        f"https://api.github.com/repos/{os.environ['GITHUB_REPOSITORY']}/contents/README.md",
        headers=headers,
        params={"ref": branch}
    )
    if response.status_code == 200:
        readme_content = response.json()
        readme_content_decoded = base64.b64decode(readme_content["content"]).decode("utf-8")
        lines = readme_content_decoded.split("\n")

        try:
            marker_index = lines.index("#### 📩 Latest Download:") + 1
        except ValueError:
            marker_index = None

        if marker_index is not None and marker_index < len(lines):
            lines[marker_index] = artifact_url
        elif marker_index is not None:
            lines.append(artifact_url)
        else:
            print("Marker for latest download not found, appending section.")
            lines.append("#### 📩 Latest Download:")
            lines.append(artifact_url)
        new_content = "\n".join(lines)
        update_data = {
            "message": "feat: Update manager download link to latest",
            "content": base64.b64encode(new_content.encode()).decode("utf-8"),
            "sha": readme_content["sha"],
            "branch": branch,
            "committer": {
                "name": "github-actions[bot]",
                "email": "41898282+github-actions[bot]@users.noreply.github.com"
            },
            "author": {
                "name": "github-actions[bot]",
                "email": "41898282+github-actions[bot]@users.noreply.github.com"
            }
        }
        response = requests.put(
            f"https://api.github.com/repos/{os.environ['GITHUB_REPOSITORY']}/contents/README.md",
            headers=headers,
            json=update_data
        )
        if response.status_code == 200:
            print("README updated successfully.")
        else:
            print(f"Failed to update README. Status code: {response.status_code}")
    else:
        print(f"Failed to fetch README. Status code: {response.status_code}")

if __name__ == "__main__":
    artifact_url = sys.argv[1]
    update_readme(artifact_url)
