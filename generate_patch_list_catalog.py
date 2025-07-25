import json
import re
from pathlib import Path
from typing import List, Tuple, Dict


def load_patch_info(bundle_dir: Path) -> Tuple[List[str], Dict[str, dict]]:
    bundle_name = bundle_dir.name.replace("-patch-bundles", "")
    patch_order: List[str] = []
    patches: Dict[str, dict] = {}

    # 1. Load the 'latest' list to get the master order + metadata
    latest_path = next(bundle_dir.glob(f"{bundle_name}-latest-patch-list.json"), None)
    if not latest_path:
        print(f"Warning: no latest-patch-list.json for {bundle_name}; skipping")
        return [], {}
    text = latest_path.read_text(encoding="utf-8").strip()
    if not text:
        print(f"Warning: {latest_path} is empty; skipping")
        return [], {}
    try:
        latest_data = json.loads(text)
    except json.JSONDecodeError as e:
        print(f"Warning: invalid JSON in {latest_path}: {e}; skipping")
        return [], {}

    for patch in latest_data.get("patches", []):
        name = patch.get("name") or "N/A"
        description = patch.get("description") or "N/A"
        comp = patch.get("compatiblePackages")
        if not comp:
            apps = "Universal"
            versions_str = "All versions"
        else:
            apps = ", ".join(comp.keys())
            version_parts = []
            for vs in comp.values():
                if not vs:
                    continue
                if isinstance(vs, list):
                    version_parts.extend(str(v) for v in vs)
                else:
                    version_parts.append(str(vs))
            versions_str = ", ".join(version_parts) if version_parts else "All versions"

        patches[name] = {
            "description": description,
            "apps": apps,
            "versions": versions_str,
            "stable": False,
            "dev": False,
        }
        patch_order.append(name)

    # 2. Mark which of those master patches appear in stable/dev
    for release in ("stable", "dev"):
        for path in bundle_dir.glob(f"{bundle_name}-{release}-patches-list.json"):
            text = path.read_text(encoding="utf-8").strip()
            if not text:
                print(f"Warning: {path} is empty; skipping")
                continue
            try:
                data = json.loads(text)
            except json.JSONDecodeError as e:
                print(f"Warning: invalid JSON in {path}: {e}; skipping")
                continue

            for patch in data.get("patches", []):
                name = patch.get("name") or "N/A"
                # only mark those that exist in latest
                if name in patches:
                    patches[name][release] = True

    return patch_order, patches


def format_patch_lines(order: List[str], patches: Dict[str, dict]) -> List[str]:
    lines: List[str] = []
    lines.append(
        "| **Name** | **Description** | **Compatible Apps** | **Compatible Versions** | **Release Type** |"
    )
    lines.append(
        "|----------|---------------|---------------------|-------------------------|---------------|"
    )

    for name in order:
        info = patches[name]
        stable = bool(info.get("stable"))
        dev = bool(info.get("dev"))

        # Decide icon:
        if not stable and dev:
            icon = "🟡"    # missing from stable
        elif not dev or stable:
            icon = "🟢"    # missing from dev OR present in stable
        else:
            icon = "N/A"   # fallback

        lines.append(
            f"| {name} | {info['description']} | {info['apps']} | {info['versions']} | {icon} |"
        )
    lines.append("")  # trailing newline
    return lines


def read_catalog_patch_names(catalog_path: Path) -> set[str]:
    names: set[str] = set()
    if not catalog_path.exists():
        return names
    for line in catalog_path.read_text(encoding="utf-8").splitlines():
        if line.startswith("**Name:** "):
            names.add(line[len("**Name:** ") :].strip())
    return names


def inject_patch_lines(
    catalog_lines: List[str], bundle_name: str, patch_lines: List[str]
) -> bool:
    header_regex = re.compile(
        rf"^### 🧩 {re.escape(bundle_name)} Bundle Patch List:", re.IGNORECASE
    )
    for i, line in enumerate(catalog_lines):
        if header_regex.match(line.strip()):
            # find the end of the <summary> block
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
            # find </details>
            k = start
            while k < len(catalog_lines) and catalog_lines[k].strip() != "</details>":
                k += 1
            if k == len(catalog_lines):
                return False

            catalog_lines[start:k] = ["", *patch_lines]
            return True
    return False


def main() -> int:
    bundle_root = Path("patch-bundles")
    catalog_path = bundle_root / "PATCH-LIST-CATALOG.md"
    catalog_text = catalog_path.read_text(encoding="utf-8")
    catalog_lines = catalog_text.splitlines()

    new_patch_names: set[str] = set()

    for bundle_dir in sorted(bundle_root.glob("*-patch-bundles")):
        if not bundle_dir.is_dir():
            continue
        bundle_name = bundle_dir.name.replace("-patch-bundles", "")
        order, patches = load_patch_info(bundle_dir)
        if not order:
            continue

        patch_lines = format_patch_lines(order, patches)
        if not inject_patch_lines(catalog_lines, bundle_name, patch_lines):
            print(f"Warning: section for '{bundle_name}' not found; skipping.")
            continue
        new_patch_names.update(order)

    old_patch_names = read_catalog_patch_names(catalog_path)
    new_text = "\n".join(catalog_lines).rstrip() + "\n"

    if new_text == catalog_text and new_patch_names.issubset(old_patch_names):
        print("Catalog already contains all patches.")
        return 1

    catalog_path.write_text(new_text, encoding="utf-8")
    print("Catalog updated.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
