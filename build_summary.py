import json
import subprocess
from pathlib import Path


def main() -> None:
    summary: dict[str, str] = {}
    changed_path = Path('changed_files.txt')
    if not changed_path.is_file():
        print('changed_files.txt not found')
        return

    for line in changed_path.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        file_path = Path(line)
        if not file_path.is_file():
            print(f'File not found: {line}')
            continue
        if file_path.name.endswith("patches-list.json"):
            print(f'Skipping since it\'s a patches file: {line}')
            continue
        try:
            with open(file_path) as f:
                data = json.load(f)
        except Exception as e:
            print(f'Failed to load {line}: {e}')
            continue
        version = None
        if isinstance(data, dict):
            if 'version' in data:
                version = data['version']
            elif 'patches' in data and isinstance(data['patches'], dict):
                version = data['patches'].get('version')

        old_version = None
        try:
            old_content = subprocess.check_output(
                ['git', 'show', f'HEAD^:{file_path!s}'], text=True
            )
            old_data = json.loads(old_content)
            if isinstance(old_data, dict):
                if 'version' in old_data:
                    old_version = old_data['version']
                elif 'patches' in old_data and isinstance(old_data['patches'], dict):
                    old_version = old_data['patches'].get('version')
        except Exception as exc:
            print(f'Failed to inspect previous version for {line}: {exc}')

        if version:
            bundle_name = file_path.stem.replace('-patches-bundle', '')
            display_old = old_version if old_version else 'N/A'
            summary[bundle_name] = f"{display_old} ---> {version}"

    summary_lines = [f"{name}: {info}" for name, info in summary.items()]

    with open('updated-bundles.txt', 'w') as f:
        f.write("\n".join(summary_lines))

    print("\n".join(summary_lines))


if __name__ == '__main__':
    main()
