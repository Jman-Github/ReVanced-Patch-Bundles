import requests
from bs4 import BeautifulSoup

# URL for the commits page
url = "https://github.com/Jman-Github/ReVanced-Patch-Bundles/commits?author=github-actions%5Bbot%5D"
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')

# Find the latest commit link
commit_link = soup.find('a', class_='js-navigation-open link-gray-dark no-underline')
if commit_link:
    latest_commit_url = "https://github.com" + commit_link['href']
    
    # Get the latest commit page
    latest_commit_response = requests.get(latest_commit_url)
    latest_commit_soup = BeautifulSoup(latest_commit_response.text, 'html.parser')
    
    # Find all the modified files in the latest commit
    files_modified = latest_commit_soup.find_all('div', class_='file-info flex-auto min-width-0')

    # Print file names and links
    with open('changed_files.txt', 'w') as f:
        print("Changed files:")
        for file_info in files_modified:
            file_name = file_info.find('a', class_='link-gray-dark text-bold js-navigation-open').text.strip()
            file_path = file_info.find('a', class_='link-gray').get('title')
            f.write(f"- [{file_name}]({file_path})\n")
            print(f"- [{file_name}]({file_path})")
else:
    print("No commits found.")
