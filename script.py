import os
import requests
import base64
import schedule
import time
from datetime import datetime

url = "https://api.github.com/repos/{owner}/{repo}/contents/{path}"

email = os.getenv('GITHUB_EMAIL')
username = os.getenv('REPO_OWNER')
repo = os.getenv('REPO_NAME')
path = 'your_file.txt'  

token = os.getenv('GITHUB_TOKEN')

headers = {
    'Authorization': 'token ' + token,
    'Accept': 'application/vnd.github.v3+json',
}

if not os.path.exists(path):
    with open(path, 'w') as f:
        f.write("Hello, World!")

with open('.gitignore', 'a') as f:
    f.write('\n' + path)

def commit_file():
    with open(path, 'r') as f:
        content = base64.b64encode(f.read().encode('utf-8')).decode('utf-8')
    message = 'Commit message'
    committer = {'name': username, 'email': email} 
    data = {'message': message, 'committer': committer, 'content': content}

    response = requests.put(url.format(owner=username, repo=repo, path=path), headers=headers, json=data)
    print(response.status_code)

def delete_file():
    response = requests.get(url.format(owner=username, repo=repo, path=path), headers=headers)
    sha = response.json()['sha']
    data = {'message': 'Delete message', 'sha': sha}

    response = requests.delete(url.format(owner=username, repo=repo, path=path), headers=headers, json=data)
    print(response.status_code)

# Schedule the tasks
schedule.every().day.at("09:00").do(commit_file)
schedule.every().day.at("12:00").do(delete_file)
schedule.every().day.at("18:00").do(delete_file)

while True:
    schedule.run_pending()
    time.sleep(1)