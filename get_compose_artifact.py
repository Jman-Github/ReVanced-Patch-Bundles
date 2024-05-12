import os
import requests
import zipfile

def download_latest_artifact():
    artifact_url = os.environ["ARTIFACT_URL"]
    response = requests.get(artifact_url)
    with open("artifact.zip", "wb") as f:
        f.write(response.content)
    with zipfile.ZipFile("artifact.zip", "r") as zip_ref:
        zip_ref.extractall("artifact")

def update_readme():
    artifact_url = os.environ["ARTIFACT_URL"]
    readme_path = "README.md"

    with open(readme_path, "r") as f:
        lines = f.readlines()

    lines[63] = f"- [Download Latest Artifact]({artifact_url})\n"

    with open(readme_path, "w") as f:
        f.writelines(lines)

if __name__ == "__main__":
    download_latest_artifact()
    update_readme()