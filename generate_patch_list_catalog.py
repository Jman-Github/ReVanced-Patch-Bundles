import json
import re
from pathlib import Path
from typing import List, Tuple, Dict


def load_patch_info(bundle_dir: Path) -> Tuple[List[str], Dict[str, dict]]:
    bundle_name = bundle_dir.name.replace("-patch-bundles", "")
    patch_order: List[str] = []
    patches: Dict[str, dict] = {}

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
            version_parts: List[str] = []
            for versions in comp.values():
                if not versions:
                    continue
                if isinstance(versions, list):
                    version_parts.extend(str(v) for v in versions)
                else:
                    version_parts.append(str(versions))
            versions_str = ", ".join(version_parts) if version_parts else "All versions"

        patches[name] = {
            "description": description,
            "apps": apps,
            "versions": versions_str,
            "stable": False,
            "dev": False,
        }
        patch_order.append(name)

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

        if not stable and dev:
            icon = "🟡"
        elif not dev or stable:
            icon = "🟢"
        else:
            icon = "N/A"

        lines.append(
            f"| {name} | {info['description']} | {info['apps']} | {info['versions']} | {icon} |"
        )
    lines.append("")
    return lines


def inject_patch_lines(
    catalog_lines: List[str], bundle_name: str, patch_lines: List[str]
) -> bool:
    """Inject or update the patch table for a bundle.

    In addition to replacing the table rows, this function normalizes the
    surrounding markdown formatting so minor differences are also detected.
    """

    header_regex = re.compile(
        rf"^### 🧩 {re.escape(bundle_name)} Bundle Patch List:", re.IGNORECASE
    )

    canonical_header = f"### 🧩 {bundle_name} Bundle Patch List:"
    canonical_details = "<details open>"
    canonical_summary = "<summary><b>Click To Collapse Patch List</b></summary>"
    canonical_close = "</details>"

    for i, line in enumerate(catalog_lines):
        if header_regex.match(line.strip()):
            changed = False

            # Ensure preceding separator line
            if i > 0 and catalog_lines[i - 1].strip() != "---":
                catalog_lines[i - 1] = "---"
                changed = True

            if catalog_lines[i] != canonical_header:
                catalog_lines[i] = canonical_header
                changed = True

            j = i + 1
            if j >= len(catalog_lines) or catalog_lines[j].strip() != canonical_details:
                if j < len(catalog_lines):
                    catalog_lines[j] = canonical_details
                else:
                    catalog_lines.append(canonical_details)
                changed = True

            j += 1
            if j >= len(catalog_lines) or catalog_lines[j].strip() != canonical_summary:
                if j < len(catalog_lines):
                    catalog_lines[j] = canonical_summary
                else:
                    catalog_lines.append(canonical_summary)
                changed = True

            j += 1
            if j >= len(catalog_lines) or catalog_lines[j].strip() != "":
                if j < len(catalog_lines):
                    catalog_lines[j] = ""
                else:
                    catalog_lines.append("")
                changed = True

            start = j + 1

            k = start
            while (
                k < len(catalog_lines) and catalog_lines[k].strip() != canonical_close
            ):
                k += 1
            if k == len(catalog_lines):
                return False

            existing_lines = [l.rstrip() for l in catalog_lines[start:k]]
            if existing_lines != [l.rstrip() for l in patch_lines]:
                catalog_lines[start:k] = patch_lines
                changed = True

            if catalog_lines[k] != canonical_close:
                catalog_lines[k] = canonical_close
                changed = True

            end = k + 1
            if end >= len(catalog_lines) or catalog_lines[end].strip() != "":
                if end < len(catalog_lines):
                    catalog_lines[end] = ""
                else:
                    catalog_lines.append("")
                changed = True

            return changed

    return False


def main() -> int:
    bundle_root = Path("patch-bundles")
    catalog_path = bundle_root / "PATCH-LIST-CATALOG.md"
    catalog_text = catalog_path.read_text(encoding="utf-8")
    catalog_lines = catalog_text.splitlines()

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

    new_text = "\n".join(catalog_lines).rstrip() + "\n"

    if new_text == catalog_text:
        print("No changes detected; skipping update.")
        return 1

    catalog_path.write_text(new_text, encoding="utf-8")
    print("Catalog updated.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
