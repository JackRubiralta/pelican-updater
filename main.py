import json
import requests
import base64

# Constants
GITHUB_TOKEN = 'your_github_token_here'
REPO_NAME = 'JackRubiralta/pelican-api'  # Repository name
FILE_PATH = 'data.json'  # Path to your JSON file within the GitHub repository
BRANCH = 'master'  # The branch where your file is located

# Prompt for article details including section choice
def prompt_for_article():
    print("Please enter the new article details:")
    section = input("Section (new/athletics): ").strip().lower()
    while section not in ["new", "athletics"]:
        print("Invalid section. Please choose 'new' or 'athletics'.")
        section = input("Section (new/athletics): ").strip().lower()

    title_text = input("Title Text: ")
    title_size = input("Title Size (big/small/medium): ").strip().lower()
    while title_size not in ["big", "small", "medium"]:
        print("Invalid size. Please choose 'big', 'small', or 'medium'.")
        title_size = input("Title Size (big/small/medium): ").strip().lower()

    summary_content = input("Summary Content: ")
    show_summary = input("Show Summary? (yes/no): ").strip().lower() == 'yes'
    author = input("Author: ")
    date = input("Date (YYYY-MM-DD): ")
    length = int(input("Length (in minutes): "))

    image_source = input("Image Source (leave blank for no image): ").strip()
    image_show = False
    if image_source:  # Only ask to show the image if there's an image source
        image_show = input("Show Image? (yes/no): ").strip().lower() == 'yes'
        image_caption = input("Image Caption (leave blank if none): ").strip()
        image_position = input("Image Position (bottom/side/generic, leave blank for 'bottom'): ").strip().lower() or "bottom"
    else:
        image_caption = ""
        image_position = "generic"

    new_article = {
        "section": section,
        "article": {
            "id": input("ID: "),
            "title": {
                "text": title_text,
                "size": title_size
            },
            "summary": {
                "content": summary_content,
                "show": show_summary
            },
            "image": {
                "source": image_source,
                "position": image_position,
                "caption": image_caption,
                "show": image_show
            },
            "date": date,
            "author": author,
            "length": length,
            "content": []
        }
    }

    return new_article


# Fetch and decode the current data.json content from GitHub
def fetch_current_data(repo_name, file_path):
    url = f"https://api.github.com/repos/{repo_name}/contents/{file_path}"
    headers = {'Authorization': f'token {GITHUB_TOKEN}'}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        file_info = response.json()
        encoded_content = file_info['content']
        sha = file_info['sha']
        decoded_content = base64.b64decode(encoded_content).decode('utf-8')
        return decoded_content, sha
    else:
        raise Exception("Failed to fetch current data.json")

# Update the file on GitHub
def update_file_on_github(repo_name, file_path, new_content, sha, message="Update data.json with a new article"):
    url = f"https://api.github.com/repos/{repo_name}/contents/{file_path}"
    headers = {
        'Authorization': f'token {GITHUB_TOKEN}',
        'Accept': 'application/vnd.github.v3+json'
    }
    data = {
        'message': message,
        'content': base64.b64encode(new_content.encode('utf-8')).decode('utf-8'),
        'branch': BRANCH,
        'sha': sha
    }
    response = requests.put(url, headers=headers, data=json.dumps(data))
    if response.status_code == 200:
        print("Article added successfully.")
    else:
        print("Failed to update article:", response.json())

def main():
    article_info = prompt_for_article()
    section = article_info['section']
    new_article = article_info['article']
    current_data, sha = fetch_current_data(REPO_NAME, FILE_PATH)
    data_json = json.loads(current_data)
    data_json[section].append(new_article)  # Append the article to the chosen section
    updated_content = json.dumps(data_json, indent=4)
    update_file_on_github(REPO_NAME, FILE_PATH, updated_content, sha)

if __name__ == "__main__":
    main()


# git push heroku master