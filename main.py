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

def prompt_for_content():
    print("\nAdding new content items. Type 'none' to finish adding.")
    content_list = []
    images_info = []  # Store images information here for later upload
    while True:
        content_type = input("\nType of content to add (paragraph (p) / image (i) / none (n)): ").strip().lower()
        while content_type not in ['paragraph', 'p', 'image', 'i', 'none', 'n']:
            print("Invalid input. Please type 'paragraph (p)', 'image (i)', or 'none (n)'.")
            content_type = input("\nType of content to add (paragraph (p) / image (i) / none (n)): ").strip().lower()
        
        if content_type in ['none', 'n']:
            break
        elif content_type in ['paragraph', 'p']:
            text = input("Enter paragraph text: ")
            content_list.append({"type": "paragraph", "text": text})
        elif content_type in ['image', 'i']:
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
    return content_list, images_info

def prompt_for_issue(data_json):
    print("Available issues:")
    for key in data_json.keys():
        print(f" - {key}")
    issue = input("Which issue would you like to update (e.g., issue10): ").strip()
    while issue not in data_json:
        print("Invalid issue key. Please type one of the listed issue keys.")
        issue = input("Which issue would you like to update (e.g., issue10): ").strip()
    return issue

def prompt_for_section(data_json, issue):
    print("Available sections:")
    for key in data_json[issue].keys():
        print(f" - {key}")
    section = input("Which section would you like to add the article to: ").strip()
    while section not in data_json[issue]:
        print("Invalid section. Please choose one of the listed sections.")
        section = input("Which section would you like to add the article to: ").strip()
    return section

def prompt_for_article():
    print("\nPlease enter the new article details.")
   

    title_text = input("Title Text: ")
    title_size = input("Title Size (big (b) / medium (m) / small (s)): ").strip().lower()
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

# Ask for summary content if the user wants to show the summary
    if show_summary:
        summary_content = input("Summary Content: ")
    else:
        summary_content = ""
    
   
    author = input("Author: ")
    while not author.strip():
        print("Author name cannot be empty.")
        author = input("Author: ")

    # Validate date input with regex
    date = input("Date (YYYY-MM-DD): ")
    date_regex = r"^\d{4}-\d{2}-\d{2}$"
    while not re.match(date_regex, date):
        print("Invalid date format. Please use YYYY-MM-DD.")
        date = input("Date (YYYY-MM-DD): ")

    # Validate length as a positive integer
    length_input = input("Length (in minutes): ")
    while not length_input.isdigit() or int(length_input) <= 0:
        print("Invalid length. Please enter a positive integer.")
        length_input = input("Length (in minutes): ")
    length = int(length_input)


    
    main_image_file_path = input("Main Image File Location (optional, type 'skip' to skip): ").strip()
    main_image_info = None

    # Loop until a valid path is provided or the user decides to skip
    while main_image_file_path.lower() != 'skip':
        if os.path.isfile(main_image_file_path):
            # Generate a random filename for the main image
            random_filename = generate_random_string(15) + os.path.splitext(main_image_file_path)[-1]
            main_image_info = (main_image_file_path, random_filename)
            break  # Exit the loop as we have a valid file
        else:
            print("Main image file does not exist. Please check the path and try again or type 'skip' to continue without a main image.")
            main_image_file_path = input("Main Image File Location (optional, type 'skip' to skip): ").strip()

    # Initialize main_image with default values
    main_image = {
        "source": "",
        "caption": "",
        "show": False,
        "position": ""
    }

    if main_image_info:
        main_image["source"] = f"/images/{main_image_info[1]}"
        main_image["caption"] = input("Main Image Caption (optional): ").strip()

        # Validate input for showing the main image
        show_input = ''
        while show_input not in ['yes', 'y', 'no', 'n']:
            show_input = input("Show Main Image? (yes/no or y/n): ").strip().lower()
            if show_input in ['yes', 'y']:
                main_image["show"] = True
            elif show_input in ['no', 'n']:
                main_image["show"] = False

        # Validate input for the position of the main image
        position_input = ''
        while position_input not in ['bottom', 'b', 'side', 's', 'top', 't']:
            position_input = input("Main Image Position (bottom/side/top or b/s/t): ").strip().lower()
            if position_input in ['bottom', 'b']:
                main_image["position"] = 'bottom'
            elif position_input in ['side', 's']:
                main_image["position"] = 'side'
            elif position_input in ['top', 't']:
                main_image["position"] = 'top'
            else:
                print("Invalid position. Please choose 'bottom', 'side', or 'top' (or 'b', 's', 't').")

    # If main_image_info is None, main_image will remain with its default values.

            
        
    content, images_info = prompt_for_content()
    if main_image_info:
        images_info.append(main_image_info)  # Add the main image for uploading


    article_info = {
        "id": generate_random_string(10),
        "title": {"text": title_text, "size": title_size},
        "summary": {"content": summary_content, "show": show_summary},
        "author": author,
        "date": date,
        "length": length,
        "content": content,
        "image": main_image
    }

    return article_info, images_info

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
            path_to_url[f"/images/{random_filename}"] = uploaded_url
    return path_to_url

def update_article_with_image_urls(article_info, path_to_url):
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

    print("Creating article for section:", section, "in issue:", issue)
    article_info, images_info = prompt_for_article()
    path_to_url = upload_images(images_info)
    article_info = update_article_with_image_urls(article_info, path_to_url)

    data_json[issue][section].append(article_info)
    updated_content = json.dumps(data_json, indent=4)
    update_file_on_github(updated_content, sha)

if __name__ == "__main__":
    main()
