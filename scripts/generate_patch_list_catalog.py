import json
import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def load_patch_info(bundle_dir: Path) -> list[dict[str, str]]:
    bundle_name = bundle_dir.name.replace("-patch-bundles", "")
    patches: list[dict[str, str]] = []

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
        apps, versions_str = format_compatible_packages(patch.get("compatiblePackages"))

        patches.append(
            {
                "name": name,
                "description": description,
                "apps": apps,
                "versions": versions_str,
            }
        )

    return patches


def _version_parts(versions: object) -> list[str]:
    if not versions:
        return []
    if isinstance(versions, list):
        return [str(v) for v in versions if v is not None]
    return [str(versions)]


def format_compatible_packages(comp: object) -> tuple[str, str]:
    if not comp:
        return "Universal", "All versions"

    app_names: list[str] = []
    version_parts: list[str] = []

    if isinstance(comp, dict):
        app_names.extend(str(app) for app in comp.keys())
        for versions in comp.values():
            version_parts.extend(_version_parts(versions))
    elif isinstance(comp, list):
        for entry in comp:
            if isinstance(entry, dict):
                package_name = entry.get("name") or entry.get("packageName")
                if package_name:
                    app_names.append(str(package_name))
                version_parts.extend(_version_parts(entry.get("versions")))
            elif entry:
                app_names.append(str(entry))
    else:
        app_names.append(str(comp))

    apps = ", ".join(app_names) if app_names else "Universal"
    versions_str = ", ".join(version_parts) if version_parts else "All versions"
    return apps, versions_str


def _squash_whitespace(value: str) -> str:
    if value is None:
        return "N/A"
    return re.sub(r"\s+", " ", str(value)).strip()


def _patch_sort_key(info: dict[str, str]) -> tuple[str, str]:
    apps = _squash_whitespace(info.get("apps", "N/A")).lower()
    name = _squash_whitespace(info.get("name", "N/A")).lower()
    return apps, name


def format_patch_lines(patches: list[dict[str, str]]) -> list[str]:
    lines: list[str] = []
    lines.append("")
    lines.append("| **Name** | **Description** | **Compatible Apps** | **Compatible Versions** |")
    lines.append("|----------|---------------|---------------------|-------------------------|")
    sorted_patches = sorted(patches, key=_patch_sort_key)
    for info in sorted_patches:
        name_cell = f"```{_squash_whitespace(info.get('name', 'N/A'))}```"
        desc_cell = f"```{_squash_whitespace(info.get('description', 'N/A'))}```"
        apps_cell = f"```{_squash_whitespace(info.get('apps', 'N/A'))}```"
        vers_cell = f"```{_squash_whitespace(info.get('versions', 'N/A'))}```"
        lines.append(f"| {name_cell} | {desc_cell} | {apps_cell} | {vers_cell} |")
    lines.append("")
    return lines


def _display_name_from_header(header: str) -> str:
    value = header.strip()
    value = re.sub(r"^###\s+", "", value)
    value = re.sub(r"^[^\w#]+", "", value, flags=re.UNICODE)
    return value.removesuffix("Bundle Patch List:").strip()


def _patch_summary(display_name: str, patches: list[dict[str, str]]) -> str:
    patch_word = "patch" if len(patches) == 1 else "patches"
    apps = {
        app.strip()
        for patch in patches
        for app in _squash_whitespace(patch.get("apps", "Universal")).split(",")
        if app.strip()
    }
    app_word = "app" if len(apps) == 1 else "apps"
    return (
        f"<summary><b>{display_name}</b> - "
        f"{len(patches)} {patch_word}, {len(apps)} {app_word}</summary>"
    )


def inject_patch_lines(
    catalog_lines: list[str],
    bundle_name: str,
    patch_lines: list[str],
    patches: list[dict[str, str]],
) -> bool:
    for i, line in enumerate(catalog_lines):
        if not line.strip().startswith("### ") or " Bundle Patch List:" not in line:
            continue

        display_name = _display_name_from_header(line)
        if display_name.casefold() == bundle_name.casefold():
            summary_line = _patch_summary(display_name, patches)
            j = i + 1
            while j < len(catalog_lines) and not catalog_lines[j].strip().startswith("<summary"):
                j += 1
            if j == len(catalog_lines):
                return False
            catalog_lines[j] = summary_line
            start = j + 1
            k = start
            while k < len(catalog_lines) and catalog_lines[k].strip() != "</details>":
                k += 1
            if k == len(catalog_lines):
                return False

            catalog_lines[start:k] = patch_lines
            return True
    return False


def normalize_pending_sections(catalog_lines: list[str]) -> None:
    for i, line in enumerate(catalog_lines):
        if not line.strip().startswith("### ") or " Bundle Patch List:" not in line:
            continue

        display_name = _display_name_from_header(line)
        j = i + 1
        while j < len(catalog_lines) and catalog_lines[j].strip() != "</details>":
            is_pending_summary = (
                catalog_lines[j].strip().startswith("<summary")
                and "pending patch list" in catalog_lines[j]
            )
            if is_pending_summary:
                catalog_lines[j] = f"<summary><b>{display_name}</b> - pending patch list</summary>"
                break
            j += 1


def _cell_text(cell: str) -> str:
    cell = cell.strip()
    if cell.startswith("```") and cell.endswith("```"):
        cell = cell[3:-3]
    return _squash_whitespace(cell)


def _section_patch_stats(lines: list[str]) -> tuple[int | None, int | None]:
    patch_count = 0
    apps: set[str] = set()
    found_table = False
    for line in lines:
        if not line.startswith("|"):
            continue
        parts = [part.strip() for part in line.strip().split("|")]
        if len(parts) < 5:
            continue
        name = parts[1]
        app_cell = parts[3]
        if name in {"**Name**", "----------"}:
            found_table = True
            continue
        if not found_table:
            continue
        patch_count += 1
        for app in _cell_text(app_cell).split(","):
            if app.strip():
                apps.add(app.strip())
    if not found_table:
        return None, None
    return patch_count, len(apps)


def _bundle_type_from_link(link_line: str) -> str:
    lowered = link_line.lower()
    if "api-v4" in lowered:
        return "API v4"
    if "morphe" in lowered:
        return "Morphe"
    if "legacy" in lowered:
        return "Legacy"
    return "Unknown"


def _index_row(name: str, anchor: str, patches: int | None, apps: int | None, status: str) -> str:
    patch_text = str(patches) if patches is not None else "-"
    app_text = str(apps) if apps is not None else "-"
    return f"| [{name}]({anchor}) | {patch_text} | {app_text} | {status} |"


def rebuild_index(catalog_lines: list[str]) -> list[str]:
    entries: list[dict[str, object]] = []
    i = 0
    while i < len(catalog_lines):
        line = catalog_lines[i]
        if not line.strip().startswith("### ") or " Bundle Patch List:" not in line:
            i += 1
            continue
        name = _display_name_from_header(line)
        link_line = catalog_lines[i + 1] if i + 1 < len(catalog_lines) else ""
        anchor_match = re.search(r"\((#[^)]+)\)", link_line)
        anchor = anchor_match.group(1) if anchor_match else f"#-{name.lower()}-bundle-patch-list"
        bundle_type = _bundle_type_from_link(link_line)
        j = i + 1
        while j < len(catalog_lines) and catalog_lines[j].strip() != "</details>":
            j += 1
        section_lines = catalog_lines[i:j]
        patches, apps = _section_patch_stats(section_lines)
        status = "Generated" if patches is not None else "Pending patch list"
        entries.append(
            {
                "name": name,
                "anchor": anchor,
                "type": bundle_type,
                "patches": patches,
                "apps": apps,
                "status": status,
            }
        )
        i = j + 1

    if not entries:
        return catalog_lines

    grouped: dict[str, list[dict[str, object]]] = {
        "API v4": [],
        "Morphe": [],
        "Legacy": [],
        "Unknown": [],
    }
    for entry in entries:
        grouped.setdefault(str(entry["type"]), []).append(entry)

    index_lines = [
        "## 🔑 Patch Bundle Index",
        (
            "Patch lists are collapsed by default. "
            "Expand a bundle to inspect its generated patch table."
        ),
        "",
    ]
    for bundle_type, type_entries in grouped.items():
        if not type_entries:
            continue
        index_lines.extend(
            [
                f"### {bundle_type}",
                "| Bundle | Patches | Apps | Status |",
                "| --- | ---: | ---: | --- |",
            ]
        )
        for entry in type_entries:
            index_lines.append(
                _index_row(
                    str(entry["name"]),
                    str(entry["anchor"]),
                    entry["patches"] if isinstance(entry["patches"], int) else None,
                    entry["apps"] if isinstance(entry["apps"], int) else None,
                    str(entry["status"]),
                )
            )
        index_lines.append("")

    section_start = next(
        (
            idx
            for idx, value in enumerate(catalog_lines)
            if value.startswith("### ") and " Bundle Patch List:" in value
        ),
        None,
    )
    index_start = next(
        (idx for idx, value in enumerate(catalog_lines) if value == "## 🔑 Patch Bundle Index"),
        None,
    )
    if section_start is None:
        return catalog_lines
    if index_start is None:
        preamble_end = next(
            (idx for idx, value in enumerate(catalog_lines) if value.startswith("## ")),
            2,
        )
        return catalog_lines[:preamble_end] + index_lines + ["---"] + catalog_lines[section_start:]
    return catalog_lines[:index_start] + index_lines + ["---"] + catalog_lines[section_start:]


def main() -> int:
    bundle_root = PROJECT_ROOT / "patch-bundles"
    catalog_path = bundle_root / "PATCH-LIST-CATALOG.md"
    catalog_text = catalog_path.read_text(encoding="utf-8")
    catalog_lines = catalog_text.splitlines()

    for bundle_dir in sorted(bundle_root.glob("*-patch-bundles")):
        if not bundle_dir.is_dir() or bundle_dir.name == "PATCH-LIST-CATALOG.md":
            continue
        patches = load_patch_info(bundle_dir)
        if not patches:
            continue

        bundle_name = bundle_dir.name.replace("-patch-bundles", "")
        patch_lines = format_patch_lines(patches)
        if not inject_patch_lines(catalog_lines, bundle_name, patch_lines, patches):
            print(f"Warning: section for '{bundle_name}' not found; skipping.")
            continue

    normalize_pending_sections(catalog_lines)
    catalog_lines = rebuild_index(catalog_lines)
    new_text = "\n".join(catalog_lines).rstrip() + "\n"

    if new_text == catalog_text:
        print("Catalog already contains all patches.")
        return 0

    catalog_path.write_text(new_text, encoding="utf-8")
    print("Catalog updated.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
