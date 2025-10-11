import json
import re
from pathlib import Path
from typing import List, Dict


def load_patch_info(bundle_dir: Path) -> List[Dict[str, str]]:
    bundle_name = bundle_dir.name.replace("-patch-bundles", "")
    patches: List[Dict[str, str]] = []

    list_file = None
    for suffix in ("latest", "stable", "dev"):
        candidate = bundle_dir / f"{bundle_name}-{suffix}-patches-list.json"
        if candidate.exists():
            list_file = candidate
            break
    if not list_file:
        return patches

    text = list_file.read_text(encoding="utf-8").strip()
    if not text:
        print(f"Warning: {list_file} is empty; skipping")
        return patches

    try:
        data = json.loads(text)
    except json.JSONDecodeError as e:
        print(f"Warning: invalid JSON in {list_file}: {e}; skipping")
        return patches

    for patch in data.get("patches", []):
        if (
            patch.get("name") == "Example Patch"
            and patch.get("description") == "This is an example patch to start with."
        ):
            continue

        name = patch.get("name") or "N/A"
        description = patch.get("description") or "N/A"
        comp = patch.get("compatiblePackages")
        if not comp:
            apps = "Universal"
            versions_str = "All versions"
        else:
            apps = ", ".join(comp.keys())
            version_parts: List[str] = []
            for versions in comp.values():
                if not versions:
                    continue
                if isinstance(versions, list):
                    version_parts.extend(str(v) for v in versions)
                else:
                    version_parts.append(str(versions))
            versions_str = ", ".join(version_parts) if version_parts else "All versions"

        patches.append(
            {
                "name": name,
                "description": description,
                "apps": apps,
                "versions": versions_str,
            }
        )

    return patches


def _squash_whitespace(value: str) -> str:
    if value is None:
        return "N/A"
    return re.sub(r"\s+", " ", str(value)).strip()


def format_patch_lines(patches: List[Dict[str, str]]) -> List[str]:
    count = len(patches)
    patch_word = "Patch" if count == 1 else "Patches"
    lines: List[str] = []
    lines.append("")
    lines.append(f"***{count} {patch_word}***")
    lines.append(
        "| **Name** | **Description** | **Compatible Apps** | **Compatible Versions** |"
    )
    lines.append(
        "|----------|---------------|---------------------|-------------------------|"
    )
    for info in patches:
        name_cell = f"```{_squash_whitespace(info.get('name', 'N/A'))}```"
        desc_cell = f"```{_squash_whitespace(info.get('description', 'N/A'))}```"
        apps_cell = f"```{_squash_whitespace(info.get('apps', 'N/A'))}```"
        vers_cell = f"```{_squash_whitespace(info.get('versions', 'N/A'))}```"
        lines.append(f"| {name_cell} | {desc_cell} | {apps_cell} | {vers_cell} |")
    lines.append("")
    return lines


def read_catalog_patch_names(catalog_path: Path) -> set[str]:
    names: set[str] = set()
    if not catalog_path.exists():
        return names
    text = catalog_path.read_text(encoding="utf-8")
    for line in text.splitlines():
        if not line.startswith("|"):
            continue
        parts = [p.strip() for p in line.strip().split("|")]
        if len(parts) < 3:
            continue
        name = parts[1]
        if not name or name in {"**Name**", "----------"}:
            continue
        if name.startswith("```") and name.endswith("```"):
            name = name[3:-3]
        name = _squash_whitespace(name)
        names.add(name)
    return names


def inject_patch_lines(
    catalog_lines: List[str], bundle_name: str, patch_lines: List[str]
) -> bool:
    header_regex = re.compile(
        rf"^### 🧩 {re.escape(bundle_name)} Bundle Patch List:", re.IGNORECASE
    )

    for i, line in enumerate(catalog_lines):
        if header_regex.match(line.strip()):
            j = i + 1
            while (
                j < len(catalog_lines)
                and catalog_lines[j].strip()
                != "<summary><b>Click To Collapse Patch List</b></summary>"
            ):
                j += 1
            if j == len(catalog_lines):
                return False
            start = j + 1
            k = start
            while k < len(catalog_lines) and catalog_lines[k].strip() != "</details>":
                k += 1
            if k == len(catalog_lines):
                return False

            catalog_lines[start:k] = patch_lines
            return True
    return False


def main() -> int:
    bundle_root = Path("patch-bundles")
    catalog_path = bundle_root / "PATCH-LIST-CATALOG.md"
    catalog_text = catalog_path.read_text(encoding="utf-8")
    catalog_lines = catalog_text.splitlines()

    new_patch_names: set[str] = set()

    for bundle_dir in sorted(bundle_root.glob("*-patch-bundles")):
        if not bundle_dir.is_dir() or bundle_dir.name == "PATCH-LIST-CATALOG.md":
            continue
        patches = load_patch_info(bundle_dir)
        if not patches:
            continue

        bundle_name = bundle_dir.name.replace("-patch-bundles", "")
        patch_lines = format_patch_lines(patches)
        if not inject_patch_lines(catalog_lines, bundle_name, patch_lines):
            print(f"Warning: section for '{bundle_name}' not found; skipping.")
            continue

        new_patch_names.update(_squash_whitespace(p["name"]) for p in patches)

    old_patch_names = read_catalog_patch_names(catalog_path)
    new_text = "\n".join(catalog_lines).rstrip() + "\n"

    if new_text == catalog_text and new_patch_names.issubset(old_patch_names):
        print("Catalog already contains all patches.")
        return 0

    catalog_path.write_text(new_text, encoding="utf-8")
    print("Catalog updated.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
