"""
Validate generated JSON bundle artifacts against the repository schemas.
"""

from __future__ import annotations

import argparse
import json
from collections.abc import Iterable
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
BUNDLE_DIR = ROOT / "patch-bundles"
SCHEMA_DIR = ROOT / "schemas"

BUNDLE_SCHEMA = json.loads((SCHEMA_DIR / "patch_bundle.schema.json").read_text(encoding="utf-8"))
PATCH_LIST_SCHEMA = json.loads((SCHEMA_DIR / "patch_list.schema.json").read_text(encoding="utf-8"))

BUNDLE_VALIDATOR = Draft202012Validator(BUNDLE_SCHEMA)
PATCH_LIST_VALIDATOR = Draft202012Validator(PATCH_LIST_SCHEMA)


def _discover_targets(paths: Iterable[Path] | None) -> list[Path]:
    if paths:
        return [p for p in paths if p.suffix == ".json" and p.is_file()]

    return sorted(BUNDLE_DIR.rglob("*.json"))


def _pick_validator(path: Path) -> Draft202012Validator | None:
    name = path.name
    if name.endswith("-patches-bundle.json"):
        return BUNDLE_VALIDATOR
    if name.endswith("-patches-list.json"):
        return PATCH_LIST_VALIDATOR
    return None


def _validate(path: Path) -> list[str]:
    validator = _pick_validator(path)
    if validator is None:
        return []

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        rel = path.relative_to(ROOT)
        return [f"{rel}: invalid JSON: {exc}"]

    errors: list[str] = []
    for error in validator.iter_errors(payload):
        rel = path.relative_to(ROOT)
        location = " -> ".join(map(str, error.absolute_path)) or "<root>"
        errors.append(f"{rel}: {location}: {error.message}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate JSON bundle artifacts.")
    parser.add_argument("paths", nargs="*", type=Path, help="Optional JSON files to validate.")
    args = parser.parse_args()

    targets = _discover_targets(args.paths)
    failures: list[str] = []

    for target in targets:
        failures.extend(_validate(target))

    if failures:
        print("Validation failed:")
        for failure in failures:
            print(f"  - {failure}")
        return 1

    print(f"Validated {len(targets)} JSON file(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
