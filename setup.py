import os

# Instructions for the user
instructions = """
To run this script, you need a GitHub account and a personal access token.
1. If you don't have a GitHub account, please create one at: https://github.com/signup
2. Once you have your GitHub account, create a personal access token by following these steps:
    a. Go to https://github.com/settings/tokens
    b. Click on "Generate new token".
    c. Give your token a descriptive name in the "Note" field.
    d. Select the scopes or permissions you'd like to grant this token. For basic repository operations, select "repo".
    e. Click "Generate token" at the bottom.
    f. Copy the generated token. This is the only time you'll see it, so make sure to save it somewhere safe.
"""

def store_github_token(token):
    """Stores the GitHub token in a local file."""
    filename = "github_token.txt"
    with open(filename, "w") as file:
        file.write(token)
    print(f"Token stored successfully in {filename}")

def main():
    print(instructions)
    token = input("Please enter your GitHub personal access token: ")
    store_github_token(token)
    print("Setup complete. You can now run your script.")

if __name__ == "__main__":
    main()
