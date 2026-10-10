"""Refresh in phases and publish checkpoints through the existing GitHub branch.

Only --publish inside GitHub Actions commits or pushes. Local runs never change Git.
"""

import argparse
import base64
import os
import re
import shutil
import subprocess
import sys
import time
import uuid
from datetime import UTC, datetime
from pathlib import Path

from generate_database import (
    ROOT,
    build_database,
    build_site,
    encoded,
    read_json,
    restore_catalog_cache,
)
from source_policy import write_extraction_policy
from validate_database import validate


def instant():
    return datetime.now(UTC).isoformat()


class Refresh:
    def __init__(self, root, publish=False, interval=30):
        self.root = Path(root)
        self.publish = publish
        self.interval = interval
        self.last_publish = 0
        self.jobs = []
        self.run_id = os.environ.get("GITHUB_RUN_ID", str(uuid.uuid4()))
        self.run_attempt = int(os.environ.get("GITHUB_RUN_ATTEMPT", "1"))
        if publish and (
            os.environ.get("GITHUB_ACTIONS") != "true" or not os.environ.get("GIT_TOKEN")
        ):
            raise ValueError("Publishing requires GitHub Actions and GIT_TOKEN")
        for kind in ("BUNDLES", "PATCHES"):
            self.jobs.append(
                {
                    "job_id": str(
                        uuid.uuid5(uuid.NAMESPACE_URL, f"{self.run_id}/{self.run_attempt}/{kind}")
                    ),
                    "job_type": kind,
                    "actions_run_id": self.run_id,
                    "actions_run_attempt": self.run_attempt,
                    "status": "STARTED",
                    "started_at": instant(),
                    "completed_at": None,
                    "error": None,
                }
            )

    def save_jobs(self):
        path = self.root / "internal/cache/refresh-jobs.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        temp = path.with_suffix(".tmp")
        temp.write_bytes(encoded(self.jobs))
        temp.replace(path)

    def checkpoint(self, force=False):
        if not force and time.monotonic() - self.last_publish < self.interval:
            return
        self.save_jobs()
        build_database(self.root, restore=False)
        validate(self.root)
        if self.publish:
            self.push()
        self.last_publish = time.monotonic()

    def push(self):
        executable = shutil.which("git")
        if not executable:
            raise RuntimeError("Git is required to publish catalog checkpoints")

        def git(*args, **kwargs):
            # Arguments are constructed here; no commands originate from catalog data.
            return subprocess.run(  # noqa: S603
                [executable, *args], cwd=self.root, **kwargs
            )

        def commit(message):
            git(
                "-c",
                "user.name=github-actions[bot]",
                "-c",
                "user.email=41898282+github-actions[bot]@users.noreply.github.com",
                "commit",
                "-m",
                message,
                check=True,
            )

        git("add", "--", "database", check=True)
        if git("diff", "--cached", "--quiet").returncode:
            commit("chore: publish patch catalog progress")
        manifest_path = self.root / "database/manifest.json"
        manifest = read_json(manifest_path)
        if not manifest:
            raise ValueError("A catalog manifest is required for publication")
        if not manifest.get("snapshot_ref"):
            reference = git(
                "rev-parse", "HEAD", check=True, capture_output=True, text=True
            ).stdout.strip()
            if not re.fullmatch(r"[a-f0-9]{40}", reference):
                raise ValueError("Invalid publication commit")
            manifest["snapshot_ref"] = reference
            temporary = manifest_path.with_suffix(".tmp")
            temporary.write_bytes(encoded(manifest))
            temporary.replace(manifest_path)
            git("add", "--", "database/manifest.json", check=True)
            commit("chore: anchor catalog snapshot reads")
        # Always retry the push, even if an earlier attempt committed successfully.
        # Credentials stay out of command arguments and error messages.
        authorization = ("x-access-token:" + os.environ["GIT_TOKEN"]).encode()
        credentials = base64.b64encode(authorization).decode()
        env = {
            **os.environ,
            "GIT_CONFIG_COUNT": "1",
            "GIT_CONFIG_KEY_0": "http.https://github.com/.extraheader",
            "GIT_CONFIG_VALUE_0": "AUTHORIZATION: basic " + credentials,
            "GIT_TRACE": "0",
            "GIT_CURL_VERBOSE": "0",
        }
        branch = read_json(self.root / "config/site.json")["data_branch"]
        git("push", "origin", "HEAD:refs/heads/" + branch, env=env, check=True)

    def phase(self, kind, command, optional=False):
        job = next(row for row in self.jobs if row["job_type"] == kind)
        job.update(status="STARTED", started_at=instant())
        self.checkpoint(force=True)
        try:
            # Commands come from run(), not repository metadata or API requests.
            process = subprocess.Popen(command, cwd=self.root)  # noqa: S603
        except OSError:
            job.update(status="FAILED", completed_at=instant(), error=f"Could not start {kind}")
            self.checkpoint(force=True)
            if not optional:
                raise
            return
        checkpoint_error = None
        try:
            while process.poll() is None:
                time.sleep(2)
                try:
                    self.checkpoint()
                except Exception as error:
                    checkpoint_error = error
                    print(
                        "Intermediate publication failed; the next checkpoint will retry.",
                        file=sys.stderr,
                    )
            code = process.returncode
        finally:
            if process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait()
        job.update(
            status="COMPLETED" if code == 0 else "FAILED",
            completed_at=instant(),
            error=None if code == 0 else f"{kind} refresh exited with code {code}",
        )
        self.checkpoint(force=True)
        if code and not optional:
            raise RuntimeError(job["error"]) from checkpoint_error

    def run(self):
        try:
            self._run()
        except BaseException:
            for job in self.jobs:
                if job["status"] in ("STARTED", "PENDING", "RUNNING"):
                    job.update(
                        status="FAILED",
                        completed_at=instant(),
                        error="Refresh stopped before this phase completed",
                    )
            try:
                self.checkpoint(force=True)
            except Exception:
                print("Final progress publication failed.", file=sys.stderr)
            raise

    def _run(self):
        restore_catalog_cache(self.root)
        python = sys.executable
        self.phase("BUNDLES", [python, "scripts/discover_releases.py"], optional=True)
        subprocess.run(  # noqa: S603 -- fixed interpreter and local script
            [python, "scripts/refresh_source_metadata.py"], cwd=self.root, check=False
        )
        write_extraction_policy(self.root)
        wrapper = self.root / "bundle-parser" / ("gradlew.bat" if os.name == "nt" else "gradlew")
        if os.name != "nt":
            wrapper.chmod(wrapper.stat().st_mode | 0o111)
        self.phase("PATCHES", [str(wrapper), "--project-dir", "bundle-parser", "run"])
        self.checkpoint(force=True)
        build_site(self.root)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--publish", action="store_true")
    args = parser.parse_args()
    Refresh(ROOT, publish=args.publish).run()
