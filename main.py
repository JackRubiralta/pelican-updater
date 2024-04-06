import json
import requests
import base64
import os
import random
import string

# Constants
GITHUB_TOKEN = 'your_github_token_here'
REPO_NAME = 'JackRubiralta/pelican-api'  # Repository name
FILE_PATH = 'data.json'  # Path to your JSON file within the GitHub repository
BRANCH = 'master'  # The branch where your file is located
def generate_random_string(length=15):
    """Generate a random string of fixed length."""
    letters = string.ascii_letters  # Combination of lowercase and uppercase
    return ''.join(random.choice(letters) for i in range(length))

# Prompt for article details including section choice
import os

def upload_image_to_github(image_path, branch='master'):
    # Generate a unique filename using a random string + original file extension
    _, ext = os.path.splitext(image_path)  # Extract the extension from the input file path
    random_filename = generate_random_string(15) + ext  # Append extension to the random string
    
    # Encode the image in base64
    with open(image_path, "rb") as image_file:
        image_content = base64.b64encode(image_file.read()).decode('utf-8')

    # Define the GitHub API URL for the target path
    url = f"https://api.github.com/repos/{REPO_NAME}/contents/images/{random_filename}"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "message": f"Add image {random_filename}",
        "content": image_content,
        "branch": branch
    }

    # Make the request to upload the image
    response = requests.put(url, headers=headers, json=data)
    if response.status_code in [200, 201]:
        print(f"Image {random_filename} uploaded successfully.")
        # Return the GitHub URL for the uploaded image
        return f"/images/{random_filename}"
    else:
        print(f"Failed to upload image {random_filename}. Response: {response.text}")
        return None


def prompt_for_content():
    content_list = []  # Initialize an empty list to hold content items

    while True:
        content_type = input("Type of content to add (paragraph/image/none to finish): ").strip().lower()

        if content_type == 'none':
            break  # Exit the loop if the user is done adding content
        elif content_type == 'paragraph':
            text = input("Enter paragraph text: ")
            content_list.append({
                "type": "paragraph",
                "text": text
            })
        elif content_type == 'image':
            image_file_path = input("Enter image file location (relative path): ").strip()
            if image_file_path:
                uploaded_image_source = upload_image_to_github(image_file_path, BRANCH)
                if uploaded_image_source:
                    image_caption = input("Enter image caption (leave blank if none): ").strip()
                    content_list.append({
                        "type": "image",
                        "source": uploaded_image_source,
                        "caption": image_caption
                    })
                else:
                    print("Failed to upload image. Skipping this content item.")
            else:
                print("No image file location provided. Skipping this content item.")
        else:
            print("Invalid content type. Please enter 'paragraph', 'image', or 'none'.")

    return content_list

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

    # Ask for the local image file location
    image_file_path = input("Main Image File Location (leave blank for no image): ").strip()
    image_source = ""  # Initialize image source as empty
    if image_file_path:
        uploaded_image_source = upload_image_to_github(image_file_path, BRANCH)
        if uploaded_image_source:
            image_source = uploaded_image_source
            
            # Use a while loop to ensure a valid response for "Show Image?"
            image_show_input = input("Show Image? (yes/no): ").strip().lower()
            while image_show_input not in ["yes", "no"]:
                print("Invalid input. Please type 'yes' or 'no'.")
                image_show_input = input("Show Image? (yes/no): ").strip().lower()
            image_show = image_show_input == 'yes'
            
            image_caption = input("Image Caption (leave blank if none): ").strip()

            # Use a while loop to ensure a valid response for "Image Position"
            valid_positions = ["bottom", "side", "top"]
            image_position = input("Image Position (bottom/side/generic, leave blank for 'bottom'): ").strip().lower()
            while image_position not in valid_positions and image_position != "":
                print(f"Invalid position. Please choose one of the following: {', '.join(valid_positions)}.")
                image_position = input("Image Position (bottom/side/generic, leave blank for 'bottom'): ").strip().lower()
            image_position = image_position if image_position in valid_positions else "bottom"
    else:
        image_show = False
        image_caption = ""
        image_position = ""

    content = prompt_for_content()
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
                "source": image_source,  # Use the URL or path where the image is accessible
                "position": image_position,
                "caption": image_caption,
                "show": image_show
            },
            "date": date,
            "author": author,
            "length": length,
            "content": content,
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