import os
import sys

def update_readme(artifact_url):
    readme_path = "README.md"

    with open(readme_path, "r") as f:
        lines = f.readlines()

    lines[63] = f"- [Download Latest Artifact]({artifact_url})\n"

    with open(readme_path, "w") as f:
        f.writelines(lines)

if __name__ == "__main__":
    artifact_url = sys.argv[1]
    update_readme(artifact_url)