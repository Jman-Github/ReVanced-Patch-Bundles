import os, subprocess, json, re, sys

def read_git(rev, path):
    try:
        return subprocess.check_output(["git", "show", f"{rev}:{path}"], text=True)
    except subprocess.CalledProcessError:
        return ""

def resolve_path(path):
    if "/" in path:
        return path
    try:
        matches = subprocess.check_output(["git", "ls-files", f"**/{path}"], text=True).splitlines()
    except subprocess.CalledProcessError:
        matches = []
    if not matches:
        return None
    exact = [item for item in matches if item.endswith("/" + path)]
    return exact[0] if exact else matches[0]

def get_version(s):
    if not s:
        return None
    try:
        data = json.loads(s)
        for k in ["version", "Version", "bundleVersion", "patchesVersion", "latestVersion"]:
            if isinstance(data, dict) and k in data and isinstance(data[k], str):
                return data[k]
    except Exception:
        pass
    m = re.search(r'"(?:version|Version|latestVersion)"\s*:\s*"([^"]+)"', s)
    return m.group(1) if m else None

def write_env(key, value):
    path = os.environ.get("GITHUB_ENV")
    if not path:
        return
    with open(path, "a", encoding="utf-8") as f:
        f.write(f"{key}={value}\n")

try:
    with open("changed_files.txt", "r", encoding="utf-8") as fh:
        changed = [l.strip() for l in fh if l.strip()]
except OSError:
    changed = []

targets = [n for n in changed if n.endswith("-patches-bundle.json")]

if not targets:
    write_env("has_bundle_updates", "false")
    sys.exit(0)

lines = []
for path in targets:
    repo_path = resolve_path(path)
    if not repo_path:
        continue
    new = read_git("HEAD", repo_path)
    old = read_git("HEAD~1", repo_path)
    v_new = get_version(new) or "?"
    v_old = get_version(old) or "?"
    name = repo_path.rsplit("/", 1)[-1]
    lines.append(f"{name.replace('-patches-bundle.json','')}: {v_old} ---> {v_new}")

if not lines:
    write_env("has_bundle_updates", "false")
    sys.exit(0)

with open("updated-bundles.txt", "w", encoding="utf-8") as out:
    out.write("\n".join(lines))

write_env("has_bundle_updates", "true")

print("\n".join(lines))
