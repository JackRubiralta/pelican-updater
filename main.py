import json
import requests
import base64
# Your GitHub Personal Access Token
GITHUB_TOKEN = 'your_github_token_here'
REPO_NAME = 'JackRubiralta/pelican-api'  # Your repository
BRANCH = 'master'  # The branch you're targeting
FILE_PATH = 'data.json'  # Path to your file within the repository

def get_file_sha(repo_name, file_path):
    """Retrieve the SHA hash of the file to be updated."""
    url = f"https://api.github.com/repos/{repo_name}/contents/{file_path}"
    headers = {'Authorization': f'token {GITHUB_TOKEN}'}
    response = requests.get(url, headers=headers)
    return response.json()['sha']

def update_file(repo_name, file_path, content, message="Update data.json via API"):
    """Update a file in the repository."""
    sha = get_file_sha(repo_name, file_path)
    url = f"https://api.github.com/repos/{repo_name}/contents/{file_path}"
    headers = {
        'Authorization': f'token {GITHUB_TOKEN}',
        'Accept': 'application/vnd.github.v3+json'
    }
    data = {
        'message': message,
        'content': content,
        'branch': BRANCH,
        'sha': sha
    }
    response = requests.put(url, headers=headers, data=json.dumps(data))
    if response.status_code == 200:
        print("File updated successfully.")
    else:
        print("Failed to update file:", response.json())

if __name__ == "__main__":
    # Load the existing data.json content or define new content here
    new_content = json.dumps({"example": "new data"})  # Your new data as a JSON string
    # Encode the content in base64
    new_content_encoded = base64.b64encode(new_content.encode("utf-8")).decode("utf-8")
    
    # Example to update data.json
    update_file(REPO_NAME, FILE_PATH, new_content_encoded, message="Update data.json with new data")
