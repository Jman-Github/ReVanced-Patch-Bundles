import json
from pathlib import Path

import pytest

from scripts.generate_patch_list_catalog import (
    format_compatible_packages,
    format_patch_lines,
    load_patch_info,
)


def test_compatible_packages_falls_back_to_target_versions() -> None:
    apps, versions = format_compatible_packages(
        [
            {
                "name": "RailOne",
                "targets": [
                    {"version": "2.1.62"},
                    {"version": None},
                    {"version": "2.1.62"},
                    {"version": "2.1.63"},
                ],
            }
        ]
    )

    assert apps == "RailOne"
    assert versions == "2.1.62, 2.1.63"


def test_compatible_packages_respects_explicit_null_versions() -> None:
    apps, versions = format_compatible_packages(
        [{"name": "RailOne", "versions": None, "targets": [{"version": "2.1.62"}]}]
    )

    assert apps == "RailOne"
    assert versions == "All versions"


def test_format_patch_lines_escapes_markdown_table_pipes() -> None:
    lines = format_patch_lines(
        [
            {
                "name": "Enable Premium",
                "description": "Forces premium state to always be active.",
                "apps": "NextGP | Calendar F1 MotoGP",
                "versions": "9.0",
            }
        ]
    )

    assert r"```NextGP \| Calendar F1 MotoGP```" in lines[3]


def test_load_patch_info_skips_non_object_entries(tmp_path: Path) -> None:
    bundle_dir = tmp_path / "demo-patch-bundles"
    bundle_dir.mkdir()
    (bundle_dir / "demo-latest-patches-list.json").write_text(
        json.dumps({"patches": ["broken", None, 42, [], {"name": "Valid patch"}]}),
        encoding="utf-8",
    )

    patches = load_patch_info(bundle_dir)

    assert [patch["name"] for patch in patches] == ["Valid patch"]


@pytest.mark.parametrize("payload", [[], None, {"patches": None}, {"patches": "broken"}])
def test_load_patch_info_skips_invalid_payload(tmp_path: Path, payload: object) -> None:
    bundle_dir = tmp_path / "demo-patch-bundles"
    bundle_dir.mkdir()
    (bundle_dir / "demo-latest-patches-list.json").write_text(json.dumps(payload), encoding="utf-8")

    assert load_patch_info(bundle_dir) == []


def test_load_patch_info_skips_invalid_names(tmp_path: Path) -> None:
    bundle_dir = tmp_path / "demo-patch-bundles"
    bundle_dir.mkdir()
    (bundle_dir / "demo-latest-patches-list.json").write_text(
        json.dumps({"patches": [{}, {"name": 42}, {"name": " "}, {"name": "Valid"}]}),
        encoding="utf-8",
    )

    assert [patch["name"] for patch in load_patch_info(bundle_dir)] == ["Valid"]


def test_catalog_generation_survives_string_patch(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from scripts import generate_patch_list_catalog as catalog

    monkeypatch.setattr(catalog, "PROJECT_ROOT", tmp_path)
    bundle_dir = tmp_path / "patch-bundles" / "demo-patch-bundles"
    bundle_dir.mkdir(parents=True)
    (bundle_dir / "demo-latest-patches-list.json").write_text(
        json.dumps({"patches": ["broken", {"name": "Valid patch"}]}), encoding="utf-8"
    )
    catalog_path = bundle_dir.parent / "PATCH-LIST-CATALOG.md"
    catalog_path.write_text(
        "# Catalog\n\n### Demo Bundle Patch List:\n"
        "[Demo](#-demo-bundle-patch-list)\n<details>\n"
        "<summary>pending patch list</summary>\n</details>\n",
        encoding="utf-8",
    )

    assert catalog.main() == 0
    assert "Valid patch" in catalog_path.read_text(encoding="utf-8")
    assert "broken" not in catalog_path.read_text(encoding="utf-8")
    assert catalog.main() == 0
