import os
import requests
import zipfile

def download_latest_artifact(artifact_url):
    response = requests.get(artifact_url)
    with open("artifact.zip", "wb") as f:
        f.write(response.content)
    with zipfile.ZipFile("artifact.zip", "r") as zip_ref:
        zip_ref.extractall("artifact")

def update_readme(artifact_url):
    readme_path = "README.md"

    with open(readme_path, "r") as f:
        lines = f.readlines()

    lines[63] = f"- [Download Latest Artifact]({artifact_url})\n"

    with open(readme_path, "w") as f:
        f.writelines(lines)

if __name__ == "__main__":
    artifact_url = os.getenv("ARTIFACT_URL")
    download_latest_artifact(artifact_url)
    update_readme(artifact_url)