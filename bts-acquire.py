"""
A module for obtaining repo readme and language data from the github API.

Before using this module, read through it, and follow the instructions marked
TODO.

After doing so, run it like this:

    python acquire.py

To create the `data.json` file that contains the data.
"""
import os
import json
from typing import Dict, List, Optional, Union, cast
import requests
from requests import get
from bs4 import BeautifulSoup
from env import github_token, github_username

# TODO: Make a github personal access token.
#     1. Go here and generate a personal access token https://github.com/settings/tokens
#        You do _not_ need select any scopes, i.e. leave all the checkboxes unchecked
#     2. Save it in your env.py file under the variable `github_token`
# TODO: Add your github username to your env.py file under the variable `github_username`
# TODO: Add more repositories to the `REPOS` list below.

def get_all_repository_urls(url): # repository url
    # Get max page.
    response = get(url)
    soup = BeautifulSoup(response.text)
    print('Finding max page for repositories...')
    max_page = int(soup.find('div', role='navigation').text[-6])
    print(f'Max page found: {max_page}')
    page = 1
    repository_links = []
    print('Starting loop...')
    for n in range(max_page):
        print(n+1, 'iteration')
        print(f'Pulling data from {url}')
        # Reset soup.
        response = get(url)
        soup = BeautifulSoup(response.text)
        # Get all the repositories from the page.
        repositories = soup.find_all('a', itemprop='name codeRepository') 
        print('Fetching links for repositories...')
        git = 'https://github.com/'
        for repo in repositories:
            repository_links.append(repo.get('href')[1:])
        next_page = soup.find('a', class_='next_page').get('href')[:-1]
        ## Use this line of code to get the url for the next page.
        if page <= 4:
            url = git + next_page + str(page + 1)
            page += 1
        else:
            return repository_links

repository_links = get_all_repository_urls('https://github.com/orgs/apple/repositories')

REPOS = repository_links

headers = {"Authorization": f"token {github_token}", "User-Agent": github_username}

if headers["Authorization"] == "token " or headers["User-Agent"] == "":
    raise Exception(
        "You need to follow the instructions marked TODO in this script before trying to use it"
    )

print('Get response data...')
def github_api_request(url: str) -> Union[List, Dict]:
    response = requests.get(url, headers=headers)
    response_data = response.json()
    if response.status_code != 200:
        raise Exception(
            f"Error response from github api! status code: {response.status_code}, "
            f"response: {json.dumps(response_data)}"
        )
    return response_data
print('Response data obtained.')

print('Getting repository language...')
def get_repo_language(repo: str) -> str:
    url = f"https://api.github.com/repos/{repo}"
    repo_info = github_api_request(url)
    if type(repo_info) is dict:
        repo_info = cast(Dict, repo_info)
        if "language" not in repo_info:
            raise Exception(
                "'language' key not round in response\n{}".format(json.dumps(repo_info))
            )
        return repo_info["language"]
    raise Exception(
        f"Expecting a dictionary response from {url}, instead got {json.dumps(repo_info)}"
    )
print('Acquired repository language.')

print('Getting repository contents...')
def get_repo_contents(repo: str) -> List[Dict[str, str]]:
    url = f"https://api.github.com/repos/{repo}/contents/"
    contents = github_api_request(url)
    if type(contents) is list:
        contents = cast(List, contents)
        return contents
    raise Exception(
        f"Expecting a list response from {url}, instead got {json.dumps(contents)}"
    )
print('Repository contents acquired.')


print('Getting readme url...')
def get_readme_download_url(files: List[Dict[str, str]]) -> str:
    """
    Takes in a response from the github api that lists the files in a repo and
    returns the url that can be used to download the repo's README file.
    """
    for file in files:
        if file["name"].lower().startswith("readme"):
            return file["download_url"]
    return ""
print('Readme url obtained.')

print('Processing repository...')
def process_repo(repo: str) -> Dict[str, str]:
    """
    Takes a repo name like "gocodeup/codeup-setup-script" and returns a
    dictionary with the language of the repo and the readme contents.
    """
    contents = get_repo_contents(repo)
    readme_download_url = get_readme_download_url(contents)
    if readme_download_url == "":
        readme_contents = ""
    else:
        readme_contents = requests.get(readme_download_url).text
    return {
        "repo": repo,
        "language": get_repo_language(repo),
        "readme_contents": readme_contents,
    }
print('Repository processed.')

print('Scraping github...')
def scrape_github_data() -> List[Dict[str, str]]:
    """
    Loop through all of the repos and process them. Returns the processed data.
    """
    return [process_repo(repo) for repo in REPOS]
print('Scraping complete.)

if __name__ == "__main__":
    data = scrape_github_data()
    json.dump(data, open("data.json", "w"), indent=1)
