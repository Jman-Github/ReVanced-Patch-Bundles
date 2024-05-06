import requests
from bs4 import BeautifulSoup

repo = "Jman-Github/ReVanced-Patch-Bundles"
author = "github-actions[bot]"

url = f"https://github.com/{repo}/commits?author={author}"
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')

commit_links = soup.find_all('a', class_='link-gray-dark no-underline h4 js-navigation-open')
latest_commit_link = commit_links[0]['href'] if commit_links else None

if latest_commit_link:
    commit_url = f"https://github.com{latest_commit_link}"
    commit_response = requests.get(commit_url)
    commit_soup = BeautifulSoup(commit_response.text, 'html.parser')
    files_modified = commit_soup.find_all('div', class_='file-info flex-auto min-width-0')
    
    print("Changed files:")
    for file_info in files_modified:
        file_name = file_info.find('a', class_='link-gray-dark text-bold js-navigation-open').text.strip()
        file_path = file_info.find('a', class_='link-gray').get('title')
        print(f"- [{file_name}]({file_path})")
else:
    print("No commits found.")
