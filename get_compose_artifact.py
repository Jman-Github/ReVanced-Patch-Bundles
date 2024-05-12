name: Check for compose manager updates

on:
  workflow_dispatch:
  schedule:
    - cron: "0 0 * * *"

jobs:
  get-artifact-and-run:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v2

      - name: Install Python dependencies
        run: |
          sudo apt-get install jq -y
          python -m pip install requests

      - name: Get artifact URL and run Python script
        run: |
          ARTIFACT_URL=$(curl -sS "https://api.github.com/repos/ReVanced/revanced-manager/actions/workflows/pr-build.yml/runs?event=pull_request&status=success" | jq -r '.workflow_runs[0].artifacts_url')
          ARTIFACT_ID=$(curl -sS "$ARTIFACT_URL" | jq -r '.artifacts[0].id')
          ARTIFACT_DOWNLOAD_URL=$(curl -sS "https://api.github.com/repos/ReVanced/revanced-manager/actions/artifacts/$ARTIFACT_ID/zip" | jq -r '.archive_download_url')
          echo "::set-env name=ARTIFACT_URL::$ARTIFACT_DOWNLOAD_URL"
          wget -O artifact.zip "${ARTIFACT_DOWNLOAD_URL}"
          unzip -q artifact.zip -d artifact
          python get_compose_artifact.py