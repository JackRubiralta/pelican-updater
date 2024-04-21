import json
import requests
import base64
import os
import random
import string
import re
from prompt_toolkit import prompt

# Constants
def get_github_token():
    """Attempts to retrieve the GitHub token from a file."""
    token_file_path = "github_token.txt"
    try:
        with open(token_file_path, "r") as file:
            token = file.read().strip()
            if token:
                return token
            else:
                raise FileNotFoundError
    except FileNotFoundError:
        return None
    
GITHUB_TOKEN = get_github_token()
if GITHUB_TOKEN is None:
    print("No GitHub token found. Please run 'python setup.py' to generate a token.")
else:
    print("GitHub Token found:", GITHUB_TOKEN)

REPO_NAME = 'JackRubiralta/pelican-api'
FILE_PATH = 'data/articles/issues.json'
IMAGE_DIR = 'data/articles/images'
BRANCH = 'master'

def generate_random_string(length=15):
    """Generate a random string of fixed length."""
    letters = string.ascii_letters
    return ''.join(random.choice(letters) for i in range(length))


def create_content():
    content_list = []
    images_info = []

    while True:
        content_type = prompt("\nAdd content - Type (header (h) / paragraph (p) / image (i) / list (l) / quote (q) / done (d)): ", default='').strip().lower()
        if content_type == 'd':
            break
        content = add_new_content(content_type)
        if content:
            if content['type'] == 'image':
                images_info.append(content['image_info'])
            content_list.append(content)
    return content_list, images_info

def edit_content(content_list):
    for i, content in enumerate(content_list):
        print(f"{i}: {content.get('text', content.get('caption', '[Image]'))}")
    while True:
        action = prompt("\nEdit content - Type (edit (e) / delete (del) / done (d)): ", default='').strip().lower()
        if action == 'd':
            break
        elif action in ['edit', 'e']:
            index = int(prompt("Enter index of content to edit: ", default=''))
            if 0 <= index < len(content_list):
                edit_item = content_list[index]
                if edit_item['type'] == 'image':
                    new_caption = prompt("Edit image caption: ", default=edit_item['caption'])
                    edit_item['caption'] = new_caption
                else:
                    new_text = prompt(f"Edit {edit_item['type']} text: ", default=edit_item['text'])
                    edit_item['text'] = new_text
        elif action in ['delete', 'del']:
            index = int(prompt("Enter index of content to delete: ", default=''))
            if 0 <= index < len(content_list):
                content_list.pop(index)
def prompt_for_content(existing_content=None):
    print("\nAdding new content items. Type 'done' to finish adding or editing.")
    content_list = existing_content if existing_content else []
    images_info = []  # Store images information here for later upload
    
    content_commands = {
        'header': 'h', 'paragraph': 'p', 'image': 'i',
        'list': 'l', 'quote': 'q', 'done': 'd', 'edit': 'e', 'delete': 'del'
    }
    display_commands = {v: k for k, v in content_commands.items()}
    
    while True:
        content_type = prompt("\nType of content to add (header (h) / paragraph (p) / image (i) / list (l) / quote (q) / edit (e) / delete (del) / done (d)): ", default='').strip().lower()
        while content_type not in content_commands.values():
            print("Invalid input. Please type a valid command.")
            content_type = prompt("\nType of content to add (header (h) / paragraph (p) / image (i) / list (l) / quote (q) / edit (e) / delete (del) / done (d)): ", default='').strip().lower()

        if content_type == 'd':
            break
        elif content_type == 'e':
            index = int(prompt("Enter index of content to edit (0-based index): ", default=''))
            edit_content(content_list, index, images_info)
        elif content_type == 'del':
            index = int(prompt("Enter index of content to delete (0-based index): ", default=''))
            if 0 <= index < len(content_list):
                content_list.pop(index)
        else:
            add_new_content(content_type, content_list, images_info)
    
    return content_list, images_info

def add_new_content(content_type):
    if content_type in ['h', 'header']:
        text = prompt("Enter header text: ", default='')
        return {"type": "header", "text": text}
    elif content_type in ['p', 'paragraph']:
        text = prompt("Enter paragraph text: ", default='')
        return {"type": "paragraph", "text": text}
    elif content_type in ['i', 'image']:
        image_file_path = prompt("Enter image file location: ", default='')
        while not os.path.isfile(image_file_path):
            print("Image file does not exist. Please check the path and try again.")
            image_file_path = prompt("Enter image file location: ", default='')
        image_caption = prompt("Enter image caption (optional): ", default='')
        random_filename = generate_random_string(15) + os.path.splitext(image_file_path)[-1]
        return {
            "type": "image",
            "source": f"/images/{random_filename}",
            "caption": image_caption,
            "image_info": (image_file_path, random_filename)
        }
    elif content_type in ['l', 'list']:
        items = []
        print("Enter list items, type 'done' to finish:")
        while True:
            item = prompt("List item: ", default='').strip()
            if item.lower() == 'done':
                break
            items.append(item)
        return {"type": "list", "items": items}
    elif content_type in ['q', 'quote']:
        text = prompt("Enter quote text: ", default='')
        return {"type": "quote", "text": text}

def create_article(data_json, issue, section):
    article_info = {
        "id": generate_random_string(10),
        "title": {"text": "", "size": ""},
        "summary": {"content": "", "show": False},
        "author": "",
        "date": "",
        "length": 0,
        "content": [],
        "image": {"source": "", "caption": "", "show": False, "position": ""}
    }
    article_info, images_info = prompt_for_article(article_info)
    return article_info, images_info

def edit_article(data_json, issue, section):
    print("Select the article to edit:")
    for idx, article in enumerate(data_json[issue][section]):
        print(f"{idx}: {article['title']['text']}")
    article_index = int(prompt("Enter the index of the article to edit: ", default=''))
    article_info = data_json[issue][section][article_index]

    # Call prompt_for_article with edit=True and handle the returned values
    article_info, images_info = prompt_for_article(article_info, edit=True)

    # After editing, return the updated article_info, images_info, and article_index
    return article_info, images_info, article_index
def prompt_for_article(article_info, edit=False):
    title_text = prompt("Title Text: ", default=article_info['title']['text'])
    article_info['title']['text'] = title_text
    title_size = prompt("Title Size (big (b) / medium (m) / small (s)): ", default=article_info['title']['size']).strip().lower()
    while title_size not in ["big", "b", "small", "s", "medium", "m"]:
        print("Invalid size. Please choose 'big', 'small', or 'medium' (or 'b', 's', 'm').")
        title_size = prompt("Title Size: ", default=article_info['title']['size']).strip().lower()
    article_info['title']['size'] = title_size if title_size in ["big", "medium", "small"] else {'b': 'big', 'm': 'medium', 's': 'small'}[title_size]

    show_summary = prompt("Show Summary? (yes (y) / no (n)): ", default='y' if article_info['summary']['show'] else 'n').strip().lower() in ['yes', 'y']
    article_info['summary']['show'] = show_summary
    if show_summary:
        summary_content = prompt("Summary Content: ", default=article_info['summary']['content'])
        article_info['summary']['content'] = summary_content

    author = prompt("Author: ", default=article_info['author'])
    article_info['author'] = author

    date = prompt("Date (YYYY-MM-DD): ", default=article_info['date'])
    date_regex = r"^\d{4}-\d{2}-\d{2}$"
    while not re.match(date_regex, date):
        print("Invalid date format. Please use YYYY-MM-DD.")
        date = prompt("Date (YYYY-MM-DD): ", default=article_info['date'])
    article_info['date'] = date

    length_input = prompt("Length (in minutes): ", default=str(article_info['length']))
    while not length_input.isdigit() or int(length_input) <= 0:
        print("Invalid length. Please enter a positive integer.")
        length_input = prompt("Length (in minutes): ", default=str(article_info['length']))
    article_info['length'] = int(length_input)

    main_image_file_path = prompt("Main Image File Location (optional, type 'skip' to skip or leave blank to keep current): ", default='')
    main_image_info = None
    while main_image_file_path.lower() != 'skip' and main_image_file_path:
        if os.path.isfile(main_image_file_path):
            random_filename = generate_random_string(15) + os.path.splitext(main_image_file_path)[-1]
            main_image_info = (main_image_file_path, random_filename)
            break
        else:
            print("Main image file does not exist. Please check the path and try again or type 'skip' to continue without a main image.")
            main_image_file_path = prompt("Main Image File Location (optional, type 'skip' to skip): ", default='')

    if main_image_info:
        article_info['image']['source'] = f"/images/{random_filename}"
        main_image_caption = prompt("Main Image Caption (optional): ", default=article_info['image']['caption'])
        article_info['image']['caption'] = main_image_caption
        show_image = prompt("Show Main Image? (yes/no or y/n): ", default='y' if article_info['image']['show'] else 'n').strip().lower() in ['yes', 'y']
        article_info['image']['show'] = show_image
        position_input = prompt("Main Image Position (bottom/side/top or b/s/t): ", default=article_info['image']['position']).strip().lower()
        article_info['image']['position'] = {'b': 'bottom', 's': 'side', 't': 'top'}.get(position_input, position_input)

    if edit:
        edit_content(article_info['content'])
    else:
        new_content, new_images_info = create_content()
        article_info['content'].extend(new_content)
        return article_info, new_images_info
    return article_info, []  # Return article_info

def update_file_on_github(new_content, sha):
    url = f"https://api.github.com/repos/{REPO_NAME}/contents/{FILE_PATH}"
    headers = {'Authorization': f'token {GITHUB_TOKEN}', 'Accept': 'application/vnd.github.v3+json'}
    data = {
        'message': "Update issues.json with a new article",
        'content': base64.b64encode(new_content.encode('utf-8')).decode('utf-8'),
        'branch': BRANCH,
        'sha': sha
    }
    response = requests.put(url, headers=headers, data=json.dumps(data))
    if response.status_code == 200:
        print("Issues updated successfully.")
    else:
        print("Failed to update issues. Response:", response.text)
        
def fetch_current_data():
    url = f"https://api.github.com/repos/{REPO_NAME}/contents/{FILE_PATH}?ref={BRANCH}"
    headers = {'Authorization': f'token {GITHUB_TOKEN}'}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        file_info = response.json()
        decoded_content = base64.b64decode(file_info['content']).decode('utf-8')
        return json.loads(decoded_content), file_info['sha']
    else:
        print("Failed to fetch issues.json. Response:", response.text)
        return None, None
def prompt_for_issue(data_json):
    print("Available issues:")
    for key in data_json.keys():
        print(f" - {key}")
    issue = input("Which issue would you like to update or edit (e.g., issue10): ").strip()
    while issue not in data_json:
        print("Invalid issue key. Please type one of the listed issue keys.")
        issue = input("Which issue would you like to update or edit (e.g., issue10): ").strip()
    return issue

def prompt_for_section(data_json, issue):
    print("Available sections in Issue:", issue)
    for key in data_json[issue].keys():
        print(f" - {key}")
    section = input("Which section would you like to add or edit the article in: ").strip()
    while section not in data_json[issue]:
        print("Invalid section. Please choose one of the listed sections.")
        section = input("Which section would you like to add or edit the article in: ").strip()
    return section
def update_article_with_image_urls(article_info, path_to_url):
    for content_item in article_info['content']:
        if content_item['type'] == 'image':
            if content_item['source'].replace('/images/', '') in path_to_url:
                content_item['source'] = path_to_url[content_item['source'].replace('/images/', '')]
    if 'source' in article_info['image'] and article_info['image']['source'] in path_to_url:
        article_info['image']['source'] = path_to_url[article_info['image']['source']]
    return article_info

def upload_image_to_github(image_path, random_filename):
    with open(image_path, "rb") as image_file:
        image_content = base64.b64encode(image_file.read()).decode('utf-8')
    url = f"https://api.github.com/repos/{REPO_NAME}/contents/{IMAGE_DIR}/{random_filename}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}", "Content-Type": "application/json"}
    data = {"message": f"Add image {random_filename}", "content": image_content, "branch": BRANCH}
    response = requests.put(url, headers=headers, json=data)
    if response.status_code in [200, 201]:
        print(f"Image {random_filename} uploaded successfully.")
        return f"https://raw.githubusercontent.com/{REPO_NAME}/{BRANCH}/{IMAGE_DIR}/{random_filename}"
    else:
        print(f"Failed to upload image {random_filename}. Response: {response.text}")
        return None
def upload_images(images_info):
    path_to_url = {}
    for image_path, random_filename in images_info:
        uploaded_url = upload_image_to_github(image_path, random_filename)
        if uploaded_url:
            path_to_url[f"{random_filename}"] = uploaded_url
    return path_to_url        
def main():
    if GITHUB_TOKEN is None:
        print("Exiting: No GitHub token found.")
        return
    
    data_json, sha = fetch_current_data()
    if data_json is None:
        print("Exiting: Failed to fetch data.")
        return

    issue = prompt_for_issue(data_json)
    section = prompt_for_section(data_json, issue)

    action_choice = prompt("Do you want to edit an existing article or create a new one? (edit/create): ", default='create').strip().lower()
    if action_choice == 'edit':
        article_info, images_info, article_index = edit_article(data_json, issue, section)
        data_json[issue][section][article_index] = article_info
    elif action_choice == 'create':
        print("Creating article for section:", section, "in issue:", issue)
        article_info, images_info = create_article(data_json, issue, section)
        data_json[issue][section].append(article_info)
    else:
        print("Invalid action. Please choose 'edit' or 'create'.")
        return  # You can also choose to recall main() or repeat the prompt depending on your user experience design.

    path_to_url = upload_images(images_info)
    article_info = update_article_with_image_urls(article_info, path_to_url)

    updated_content = json.dumps(data_json, indent=4)
    update_file_on_github(updated_content, sha)

if __name__ == "__main__":
    main()
