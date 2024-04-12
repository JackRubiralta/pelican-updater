#!/bin/bash
clear

# Checking for Homebrew and installing it if it's not present
if ! command -v brew &> /dev/null; then
    echo "Homebrew not found. Installing Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    # Add Homebrew to PATH if it's not already added
    echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
    eval "$(/opt/homebrew/bin/brew shellenv)"
fi

echo "Homebrew installed."

# Checking for Python and installing it if it's not present
if ! command -v python3 &> /dev/null; then
    echo "Python 3 not found. Installing Python 3..."
    brew install python
else
    echo "Python 3 is already installed."
fi

echo
echo "Installing required pip packages..."
pip3 install -r requirements.txt || python3 -m pip install -r requirements.txt

echo
if [ -f "github_token.txt" ]; then
    echo "GitHub token found."
else
    echo "GitHub token file not found."
    echo "Opening GitHub token creation page..."
    open https://github.com/settings/tokens
    echo "Please select the following scopes for the GitHub token:"
    echo "- repo: Full control of private repositories"
    echo "- admin:repo_hook: Full control of repository hooks"
    echo "- user: Update all user data"
    echo "Enter your GitHub token:"
    read GITHUB_TOKEN
    echo $GITHUB_TOKEN > github_token.txt
    echo "GitHub token saved to github_token.txt."
fi

echo
echo "Setup complete. Please restart your terminal for all changes to take effect."
read -p "Press any key to continue... " -n1 -s
echo
