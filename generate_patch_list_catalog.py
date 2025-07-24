import json
from pathlib import Path

HEADER = (
    "# 🗃️ Bundle Patch List Catalog\n"
    "This catalog includes all API v4 (.RVP) patch bundles, each with a detailed list of patches, including their names, descriptions, supported applications, and compatible versions. You can quickly search the catalog using CTRL + F (Windows) or Command + F (Mac). **Currently, API v3 (.jar) bundles patch lists aren't available here.** Support for API v3 patch bundles may be added in the future.\n"
)


def load_patch_info(bundle_dir: Path):
    bundle_name = bundle_dir.name.replace("-patch-bundles", "")
    pattern = f"{bundle_name}-*-patches-list.json"
    patch_order = []
    patches = {}
    for list_file in bundle_dir.glob(pattern):
        with list_file.open(encoding="utf-8") as f:
            data = json.load(f)
        for patch in data.get("patches", []):
            name = patch.get("name", "N/A")
            if name not in patches:
                patch_order.append(name)
            description = patch.get("description")
            description = description if description is not None else "None"
            comp = patch.get("compatiblePackages")
            if comp is None:
                apps = "Universal"
                versions_str = ""
            else:
                apps = ", ".join(comp.keys())
                version_parts = []
                for versions in comp.values():
                    if versions is None:
                        continue
                    elif isinstance(versions, list):
                        version_parts.extend(versions)
                    else:
                        version_parts.append(str(versions))
                versions_str = ", ".join(version_parts)
            patches[name] = {
                "description": description,
                "apps": apps,
                "versions": versions_str,
            }
    return patch_order, patches


def format_bundle_section(bundle_name: str, order, patches):
    lines = [
        f"### 🧩 {bundle_name.title()} Bundle Patch List:",
        "<details open>",
        "<summary><b>Click To Collapse Patch List</b></summary>",
    ]
    for name in order:
        info = patches[name]
        lines.append(f"Name: {name}")
        lines.append(f"Description: {info['description']}")
        lines.append(f"Compatible apps: {info['apps']}")
        if info["versions"]:
            lines.append(f"Supported app versions: {info['versions']}")
        lines.append("")
    lines.append("\n</details>")
    return "\n".join(lines)


def read_catalog_patch_names(catalog_path: Path) -> set[str]:
    """Return patch names currently present in the catalog file."""
    names: set[str] = set()
    if not catalog_path.exists():
        return names
    for line in catalog_path.read_text(encoding="utf-8").splitlines():
        if line.startswith("Name: "):
            names.add(line[len("Name: ") :].strip())
    return names


def main() -> int:
    bundle_root = Path("patch-bundles")
    lines = [HEADER.strip(), ""]
    new_patch_names: set[str] = set()
    for bundle_dir in sorted(bundle_root.glob("*-patch-bundles")):
        if not bundle_dir.is_dir():
            continue
        if bundle_dir.name == "PATCH-LIST-CATALOG.md":
            continue
        order, patches = load_patch_info(bundle_dir)
        if not order:
            continue
        bundle_name = bundle_dir.name.replace("-patch-bundles", "")
        lines.append(format_bundle_section(bundle_name, order, patches))
        lines.append("\n---")
        new_patch_names.update(order)
    catalog_path = bundle_root / "PATCH-LIST-CATALOG.md"
    old_patch_names = read_catalog_patch_names(catalog_path)
    if new_patch_names.issubset(old_patch_names):
        print("Catalog already contains all patches.")
        return 1
    catalog_path.write_text("\n".join(lines).strip() + "\n", encoding="utf-8")
    print("Catalog updated with new patches.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
