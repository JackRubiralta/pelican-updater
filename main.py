import json
import requests
import base64
import os
import random
import string
import re

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
        content_type = input("\nType of content to add (header (h) / paragraph (p) / image (i) / list (l) / quote (q) / edit (e) / delete (del) / done (d)): ").strip().lower()
        while content_type not in content_commands.values():
            print("Invalid input. Please type a valid command.")
            content_type = input("\nType of content to add (header (h) / paragraph (p) / image (i) / list (l) / quote (q) / edit (e) / delete (del) / done (d)): ").strip().lower()

        if content_type == 'd':
            break
        elif content_type == 'e':
            index = int(input("Enter index of content to edit (0-based index): "))
            edit_content(content_list, index, images_info)
        elif content_type == 'del':
            index = int(input("Enter index of content to delete (0-based index): "))
            if 0 <= index < len(content_list):
                content_list.pop(index)
        else:
            add_new_content(content_type, content_list, images_info)
    
    return content_list, images_info

def edit_content(content_list, index, images_info):
    if 0 <= index < len(content_list):
        content_item = content_list[index]
        print(f"Editing content: {content_item}")
        if content_item['type'] == 'image':
            # Special handling for images to possibly update the file
            image_file_path = input("Enter new image file location (leave blank to keep current): ").strip()
            if image_file_path and os.path.isfile(image_file_path):
                random_filename = generate_random_string(15) + os.path.splitext(image_file_path)[-1]
                images_info.append((image_file_path, random_filename))
                content_item['source'] = f"/images/{random_filename}"
            image_caption = input("Enter new image caption (leave blank to keep current): ").strip()
            if image_caption:
                content_item['caption'] = image_caption
        else:
            new_text = input(f"Enter new text for {content_item['type']} (leave blank to keep current): ").strip()
            if new_text:
                content_item['text'] = new_text

def add_new_content(content_type, content_list, images_info):
    if content_type in ['h', 'header']:
        text = input("Enter header text: ")
        content_list.append({"type": "header", "text": text})
    elif content_type in ['p', 'paragraph']:
        text = input("Enter paragraph text: ")
        content_list.append({"type": "paragraph", "text": text})
    elif content_type in ['i', 'image']:
        while True:
            image_file_path = input("Enter image file location: ").strip()
            if os.path.isfile(image_file_path):
                break
            else:
                print("Image file does not exist. Please check the path and try again.")
        image_caption = input("Enter image caption (optional): ").strip()
        random_filename = generate_random_string(15) + os.path.splitext(image_file_path)[-1]
        images_info.append((image_file_path, random_filename))
        content_list.append({"type": "image", "source": f"/images/{random_filename}", "caption": image_caption})
    elif content_type in ['l', 'list']:
        items = []
        print("Enter list items, type 'done' to finish:")
        while True:
            item = input("List item: ").strip()
            if item.lower() == 'done':
                break
            items.append(item)
        if items:
            content_list.append({"type": "list", "items": items})
    elif content_type in ['q', 'quote']:
        text = input("Enter quote text: ")
        content_list.append({"type": "quote", "text": text})

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

def prompt_for_article(data_json=None, issue=None, section=None, edit=False):
    print("\nPlease enter the new article details or edit an existing one.")
   
    if edit:
        print("Select the article to edit:")
        for idx, article in enumerate(data_json[issue][section]):
            print(f"{idx}: {article['title']['text']}")
        article_index = int(input("Enter the index of the article to edit: "))
        article_info = data_json[issue][section][article_index]
    else:
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
    title_text = input(f"Title Text ({'Enter new title' if edit else 'Current title: ' + article_info['title']['text']}): ")
    if title_text:
        article_info['title']['text'] = title_text
    title_size = input(f"Title Size (big (b) / medium (m) / small (s)) ({'Enter new size' if edit else 'Current size: ' + article_info['title']['size']}): ").strip().lower()
    # Keep asking until a valid input is provided
    while title_size not in ["big", "b", "small", "s", "medium", "m"]:
        print("Invalid size. Please choose 'big', 'small', or 'medium' (or 'b', 's', 'm').")
        title_size = input("Title Size: ").strip().lower()

    # Map the abbreviations to their full form
    if title_size == 'b':
        title_size = 'big'
    elif title_size == 'm':
        title_size = 'medium'
    elif title_size == 's':
        title_size = 'small'
    article_info['title']['size'] = title_size

    show_summary = None
    # Ask the user until a valid input is provided
    while show_summary is None:
        user_input = input("Show Summary? (yes (y) / no (n)): ").strip().lower()
        if user_input in ['yes', 'y']:
            show_summary = True
        elif user_input in ['no', 'n']:
            show_summary = False
        else:
            print("Invalid input. Please answer 'yes' or 'no' ('y' or 'n').")
    article_info['summary']['show'] = show_summary

    # Ask for summary content if the user wants to show the summary
    if show_summary:
        summary_content = input("Summary Content: ")
        article_info['summary']['content'] = summary_content
    
    author = input(f"Author: ({'Enter new author' if edit else 'Current author: ' + article_info['author']}): ")
    if author:
        article_info['author'] = author

    # Validate date input with regex
    date = input(f"Date (YYYY-MM-DD): ({'Enter new date' if edit else 'Current date: ' + article_info['date']}): ")
    date_regex = r"^\d{4}-\d{2}-\d{2}$"
    while not re.match(date_regex, date):
        print("Invalid date format. Please use YYYY-MM-DD.")
        date = input("Date (YYYY-MM-DD): ")
    article_info['date'] = date

    # Validate length as a positive integer
    length_input = input(f"Length (in minutes): ({'Enter new length' if edit else 'Current length: ' + str(article_info['length'])}): ")
    while not length_input.isdigit() or int(length_input) <= 0:
        print("Invalid length. Please enter a positive integer.")
        length_input = input("Length (in minutes): ")
    article_info['length'] = int(length_input)

    main_image_file_path = input("Main Image File Location (optional, type 'skip' to skip or leave blank to keep current): ").strip()
    main_image_info = None

    # Loop until a valid path is provided or the user decides to skip
    while main_image_file_path.lower() != 'skip' and main_image_file_path:
        if os.path.isfile(main_image_file_path):
            # Generate a random filename for the main image
            random_filename = generate_random_string(15) + os.path.splitext(main_image_file_path)[-1]
            main_image_info = (main_image_file_path, random_filename)
            break  # Exit the loop as we have a valid file
        else:
            print("Main image file does not exist. Please check the path and try again or type 'skip' to continue without a main image.")
            main_image_file_path = input("Main Image File Location (optional, type 'skip' to skip): ").strip()

    if main_image_info:
        article_info['image']['source'] = f"/images/{random_filename}"
        main_image_caption = input("Main Image Caption (optional): ").strip()
        if main_image_caption:
            article_info['image']['caption'] = main_image_caption

        # Validate input for showing the main image
        show_input = ''
        while show_input not in ['yes', 'y', 'no', 'n']:
            show_input = input("Show Main Image? (yes/no or y/n): ").strip().lower()
            if show_input in ['yes', 'y']:
                article_info['image']['show'] = True
            elif show_input in ['no', 'n']:
                article_info['image']['show'] = False

        # Validate input for the position of the main image
        position_input = ''
        while position_input not in ['bottom', 'b', 'side', 's', 'top', 't']:
            position_input = input("Main Image Position (bottom/side/top or b/s/t): ").strip().lower()
            if position_input in ['bottom', 'b']:
                article_info['image']['position'] = 'bottom'
            elif position_input in ['side', 's']:
                article_info['image']['position'] = 'side'
            elif position_input in ['top', 't']:
                article_info['image']['position'] = 'top'
            else:
                print("Invalid position. Please choose 'bottom', 'side', or 'top' (or 'b', 's', 't').")

    existing_content = article_info['content'] if edit else None
    content, images_info = prompt_for_content(existing_content)
    if main_image_info:
        images_info.append(main_image_info)  # Add the main image for uploading
    article_info['content'] = content

    return article_info, images_info, edit, article_index if edit else None

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

def update_article_with_image_urls(article_info, path_to_url):
    for content_item in article_info['content']:
        if content_item['type'] == 'image':
            if content_item['source'].replace('/images/', '') in path_to_url:
                content_item['source'] = path_to_url[content_item['source'].replace('/images/', '')]
    if 'source' in article_info['image'] and article_info['image']['source'] in path_to_url:
        article_info['image']['source'] = path_to_url[article_info['image']['source']]
    return article_info

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

    edit_article = input("Do you want to edit an existing article? (yes/no): ").strip().lower() == 'yes'
    if edit_article:
        article_info, images_info, edit, article_index = prompt_for_article(data_json, issue, section, edit=True)
        data_json[issue][section][article_index] = article_info
    else:
        print("Creating article for section:", section, "in issue:", issue)
        article_info, images_info, edit, _ = prompt_for_article()
        data_json[issue][section].append(article_info)

    path_to_url = upload_images(images_info)
    article_info = update_article_with_image_urls(article_info, path_to_url)

    updated_content = json.dumps(data_json, indent=4)
    update_file_on_github(updated_content, sha)

if __name__ == "__main__":
    main()
