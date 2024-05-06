import os
import json
import sys

def find_changed_files():
    changed_files = []
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith('.json'):
                full_path = os.path.join(root, file)
                if os.path.getmtime(full_path) > float(sys.argv[1]):
                    changed_files.append(full_path)
    return changed_files

if __name__ == "__main__":
    changed_files = find_changed_files()
    for file in changed_files:
        print(file)
