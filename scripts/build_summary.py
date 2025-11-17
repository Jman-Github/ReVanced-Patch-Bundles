from pathlib import Path

from bundle_updates import CHANGED_FILES_PATH, collect_bundle_updates

PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_PATH = PROJECT_ROOT / "updated-bundles.txt"


def main() -> None:
    if not CHANGED_FILES_PATH.is_file():
        print('changed_files.txt not found')
        return

    updates = collect_bundle_updates()
    if not updates:
        print('No bundle updates detected.')
        return

    summary_lines = [update.format_line() for update in updates]

    OUTPUT_PATH.write_text("\n".join(summary_lines), encoding='utf-8')

    print("\n".join(summary_lines))


if __name__ == '__main__':
    main()
