import json
import re
from pathlib import Path
from typing import List


def load_patch_info(bundle_dir: Path):
    bundle_name = bundle_dir.name.replace("-patch-bundles", "")
    patch_order: List[str] = []
    patches: dict[str, dict[str, str]] = {}

    # Only load the latest-patches-list.json for this bundle
    pattern = f"{bundle_name}-latest-patches-list.json"
    for list_file in bundle_dir.glob(pattern):
        text = list_file.read_text(encoding="utf-8").strip()
        if not text:
            print(f"Warning: {list_file} is empty; skipping")
            continue

        try:
            data = json.loads(text)
        except json.JSONDecodeError as e:
            print(f"Warning: invalid JSON in {list_file}: {e}; skipping")
            continue

        for patch in data.get("patches", []):
            name = patch.get("name", "N/A")
            if name not in patches:
                patch_order.append(name)
                description = patch.get("description") or "None"
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
                    versions_str = (
                        ", ".join(version_parts) if version_parts else "All versions"
                    )
                patches[name] = {
                    "description": description,
                    "apps": apps,
                    "versions": versions_str,
                }

    return patch_order, patches


def format_patch_lines(order, patches) -> List[str]:
    """Return a list of lines representing a Markdown table for all patches."""
    lines: List[str] = []
    lines.append(
        "| **Name** | **Description** | **Compatible Apps** | **Compatible Versions** |"
    )
    lines.append(
        "|----------|---------------|---------------------|-------------------------|"
    )
    for name in order:
        info = patches[name]
        lines.append(
            f"| {name} | {info['description']} | {info['apps']} | {info['versions']} |"
        )
    lines.append("")
    return lines


def read_catalog_patch_names(catalog_path: Path) -> set[str]:
    """Return patch names currently present in the catalog file."""
    names: set[str] = set()
    if not catalog_path.exists():
        return names
    for line in catalog_path.read_text(encoding="utf-8").splitlines():
        if not line.startswith("|"):
            continue
        parts = [p.strip() for p in line.strip().split("|")]
        if len(parts) < 3:
            continue
        name = parts[1]
        if not name or name in {"**Name**", "----------"}:
            continue
        names.add(name)
    return names


def inject_patch_lines(
    catalog_lines: List[str], bundle_name: str, patch_lines: List[str]
) -> bool:
    """Inject patch lines for a bundle into the catalog."""
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
        if not bundle_dir.is_dir() or bundle_dir.name == "PATCH-LIST-CATALOG.md":
            continue
        order, patches = load_patch_info(bundle_dir)
        if not order:
            continue

        bundle_name = bundle_dir.name.replace("-patch-bundles", "")
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
