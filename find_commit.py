import os
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Function to get the details of the latest workflow run
def get_latest_workflow_run():
    url = f"https://api.github.com/repos/{os.getenv('GITHUB_REPOSITORY')}/actions/runs"
    headers = {"Authorization": f"token {os.getenv('GITHUB_TOKEN')}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        if "workflow_runs" in data:
            workflow_runs = data["workflow_runs"]
            for run in workflow_runs:
                if run["workflow_id"] == 1729913:  # ID of the bundle_updater.yml workflow
                    return run
    return None

# Function to get the names of the .json files changed in the latest workflow run
def get_changed_json_files(run_id):
    url = f"https://api.github.com/repos/{os.getenv('GITHUB_REPOSITORY')}/actions/runs/{run_id}/artifacts"
    headers = {"Authorization": f"token {os.getenv('GITHUB_TOKEN')}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        artifacts = response.json()["artifacts"]
        changed_json_files = []
        for artifact in artifacts:
            if artifact["name"].endswith(".json"):
                changed_json_files.append(artifact["name"])
        return changed_json_files
    return None

# Get the latest workflow run
latest_run = get_latest_workflow_run()

if latest_run:
    run_id = latest_run["id"]
    changed_json_files = get_changed_json_files(run_id)
    if changed_json_files:
        with open('changed_files.txt', 'w') as f:
            f.write("Changed JSON files:\n")
            for file_name in changed_json_files:
                f.write(f"- {file_name}\n")
            f.write(f"\n[View Workflow Run](https://github.com/{os.getenv('GITHUB_REPOSITORY')}/actions/runs/{run_id})\n")
    else:
        print("No .json files found.")
else:
    print("No workflow runs found.")
