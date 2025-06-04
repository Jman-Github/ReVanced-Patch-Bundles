import json
from pathlib import Path


def main():
    summary = {}
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
        if version:
            bundle_name = file_path.stem.replace('-patches-bundle', '')
            summary[bundle_name] = version

    with open('updated-bundles.txt', 'w') as f:
        json.dump(summary, f, indent=2)
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
