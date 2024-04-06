import json
import requests
import base64
import os
import random
import string

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
    
REPO_NAME = 'JackRubiralta/pelican-api'
FILE_PATH = 'data.json'
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
        if content_type == 'none' or content_type == 'n':
            break
        elif content_type == 'paragraph' or content_type == 'p':
            text = input("Enter paragraph text: ")
            content_list.append({"type": "paragraph", "text": text})
        elif content_type == 'image' or content_type == 'i':
            image_file_path = input("Enter image file location: ").strip()
            if os.path.isfile(image_file_path):
                image_caption = input("Enter image caption (optional): ").strip()
                random_filename = generate_random_string(15) + os.path.splitext(image_file_path)[-1]
                images_info.append((image_file_path, random_filename))
                content_list.append({"type": "image", "source": f"/images/{random_filename}", "caption": image_caption})
            else:
                print("Image file does not exist. Please check the path and try again.")
        else:
            print("Invalid input. Please type 'paragraph (p)', 'image (i)', or 'none (n)'.")
    return content_list, images_info

def prompt_for_article():
    print("\nPlease enter the new article details.")
    section = input("Section (news/athletics): ").strip().lower()
    while section not in ["news", "athletics"]:
        print("Invalid section. Please choose 'news' or 'athletics'.")
        section = input("Section: ").strip().lower()

    title_text = input("Title Text: ")
    title_size = input("Title Size (big/small/medium): ").strip().lower()
    while title_size not in ["big", "small", "medium"]:
        print("Invalid size. Please choose 'big', 'small', or 'medium'.")
        title_size = input("Title Size: ").strip().lower()

    summary_content = input("Summary Content: ")
    show_summary = input("Show Summary? (yes/no): ").strip().lower() == 'yes'
    author = input("Author: ")
    date = input("Date (YYYY-MM-DD): ")
    length = int(input("Length (in minutes): "))

    main_image_file_path = input("Main Image File Location (optional): ").strip()
    main_image_info = None
    if main_image_file_path and os.path.isfile(main_image_file_path):
        random_filename = generate_random_string(15) + os.path.splitext(main_image_file_path)[-1]
        main_image_info = (main_image_file_path, random_filename)
    else:
        print("Main image file does not exist. Continuing without a main image.")

    content, images_info = prompt_for_content()
    if main_image_info:
        images_info.append(main_image_info)  # Add the main image for uploading

    article_info = {
        "section": section,
        "article": {
            "id": generate_random_string(10),
            "title": {"text": title_text, "size": title_size},
            "summary": {"content": summary_content, "show": show_summary},
            "author": author,
            "date": date,
            "length": length,
            "content": content,
        }
    }

    if main_image_info:
        article_info["article"]["image"] = {
            "source": f"/images/{main_image_info[1]}",
            "caption": input("Main Image Caption (optional): ").strip(),
            "show": input("Show Main Image? (yes/no): ").strip().lower() == 'yes',
            "position": input("Main Image Position (bottom/side/generic, default 'bottom'): ").strip().lower() or "bottom"
        }

    return article_info, images_info

def upload_image_to_github(image_path, random_filename):
    with open(image_path, "rb") as image_file:
        image_content = base64.b64encode(image_file.read()).decode('utf-8')
    url = f"https://api.github.com/repos/{REPO_NAME}/contents/images/{random_filename}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}", "Content-Type": "application/json"}
    data = {"message": f"Add image {random_filename}", "content": image_content, "branch": BRANCH}
    response = requests.put(url, headers=headers, json=data)
    if response.status_code in [200, 201]:
        print(f"Image {random_filename} uploaded successfully.")
        return f"https://raw.githubusercontent.com/{REPO_NAME}/{BRANCH}/images/{random_filename}"
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
    for content_item in article_info["article"]["content"]:
        if content_item["type"] == "image" and content_item["source"] in path_to_url:
            content_item["source"] = path_to_url[content_item["source"]]
    if "image" in article_info["article"] and article_info["article"]["image"]["source"] in path_to_url:
        article_info["article"]["image"]["source"] = path_to_url[article_info["article"]["image"]["source"]]
    return article_info

def fetch_current_data():
    url = f"https://api.github.com/repos/{REPO_NAME}/contents/{FILE_PATH}?ref={BRANCH}"
    headers = {'Authorization': f'token {GITHUB_TOKEN}'}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        file_info = response.json()
        decoded_content = base64.b64decode(file_info['content']).decode('utf-8')
        return decoded_content, file_info['sha']
    else:
        print("Failed to fetch current data.json. Response:", response.text)
        return None, None

def update_file_on_github(new_content, sha):
    url = f"https://api.github.com/repos/{REPO_NAME}/contents/{FILE_PATH}"
    headers = {'Authorization': f'token {GITHUB_TOKEN}', 'Accept': 'application/vnd.github.v3+json'}
    data = {
        'message': "Update data.json with a new article",
        'content': base64.b64encode(new_content.encode('utf-8')).decode('utf-8'),
        'branch': BRANCH,
        'sha': sha
    }
    response = requests.put(url, headers=headers, data=json.dumps(data))
    if response.status_code == 200:
        print("Article added successfully.")
    else:
        print("Failed to update article. Response:", response.json())

def main():
    
    GITHUB_TOKEN = get_github_token()
    
    if GITHUB_TOKEN is None:
        print("No GitHub token found. Please run 'python setup.py' to generate a token.")
        return

    # Your main script logic here
    print("GitHub Token found:", GITHUB_TOKEN)
    
    print("Creating article!")
    article_info, images_info = prompt_for_article()
    path_to_url = upload_images(images_info)
    article_info = update_article_with_image_urls(article_info, path_to_url)

    current_data, sha = fetch_current_data()
    if current_data is not None:
        data_json = json.loads(current_data)
        section = article_info['section']
        data_json[section].append(article_info['article'])
        updated_content = json.dumps(data_json, indent=4)
        update_file_on_github(updated_content, sha)

if __name__ == "__main__":
    main()
