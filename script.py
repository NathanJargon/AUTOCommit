import os
import requests
import base64
import schedule
import time
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

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

def debug_commit_files():
    for i in range(1, 3):
        file_path = f'file_{i}.txt'
        if not os.path.exists(file_path):
            with open(file_path, 'w') as f:
                f.write(f"This is file number {i}")

        with open('.gitignore', 'a') as f:
            f.write('\n' + file_path)

        with open(file_path, 'r') as f:
            content = base64.b64encode(f.read().encode('utf-8')).decode('utf-8')

        message = f'Commit message for file_{i}.txt'
        committer = {'name': username, 'email': email} 
        data = {'message': message, 'committer': committer, 'content': content}

        response = requests.put(url.format(owner=username, repo=repo, path=file_path), headers=headers, json=data)
        print(response.status_code)

def debug_delete_files():
    for i in range(1, 3):
        file_path = f'file_{i}.txt'
        if os.path.exists(file_path):
            response = requests.get(url.format(owner=username, repo=repo, path=file_path), headers=headers)
            if response.status_code == 200:
                sha = response.json()['sha']
                data = {'message': f'Delete message for {file_path}', 'sha': sha}

                response = requests.delete(url.format(owner=username, repo=repo, path=file_path), headers=headers, json=data)
                print(response.status_code)

            with open('.gitignore', 'r') as f:
                lines = f.readlines()
            with open('.gitignore', 'w') as f:
                for line in lines:
                    if line.strip("\n") != file_path:
                        f.write(line)
      
debug_commit_files()
debug_delete_files()              
   
schedule.every().day.at("09:00").do(commit_file)
schedule.every().day.at("12:00").do(delete_file)
schedule.every().day.at("18:00").do(delete_file)


while True:
    schedule.run_pending()