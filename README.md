# Project Title

Brief project description goes here.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites

What things you need to install the software and how to install them:

- **Python**: The project is developed with Python. You will need Python installed on your system to run the script.
- **GitHub Account**: The script interacts with GitHub, requiring a GitHub account and a personal access token for authentication.

### Installing Python

Follow these steps to install Python on your system:

#### Windows:

1. Download the latest Python installer from the [official Python website](https://www.python.org/downloads/windows/).
2. Run the installer, ensuring that you check the option to **Add Python to PATH** during installation.
3. Once installed, open Command Prompt and type `python --version` to verify the installation.

#### macOS:

1. Python comes pre-installed on macOS. You can verify the installation by opening Terminal and typing `python3 --version`.
2. If you need a newer version, you can download it from the [official Python website](https://www.python.org/downloads/macos/) or use a package manager like Homebrew.
```sh
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
brew install python
```


#### Linux:

1. Most Linux distributions come with Python pre-installed. You can verify the installation by opening a terminal and typing `python3 --version`.
2. If Python is not installed, you can install it using your distribution's package manager. For example, on Ubuntu, you can install Python by running `sudo apt-get install python3`.

### Creating a GitHub Account

If you do not already have a GitHub account, go to [GitHub's website](https://github.com/) and sign up for a new account.

### Obtaining a GitHub Personal Access Token

1. Once logged into GitHub, navigate to [Personal Access Tokens settings](https://github.com/settings/tokens).
2. Click on **Generate new token**.
3. Give your token a descriptive name in the **Note** field.
4. Select the scopes or permissions you'd like to grant this token. To use the script, you must select **repo** to allow access to private repositories.
5. Click **Generate token** at the bottom.
6. **Important**: Make sure you copy your new personal access token now. You won’t be able to see it again!

### Running the Script

1. Clone the repository or download the script to your local machine.
2. Open a terminal or command prompt in the script's directory.
3. Before running the script, replace `'YOUR_GITHUB_TOKEN_HERE'` in the script with the personal access token you generated.
4. Run the script by typing `python script_name.py`, replacing `script_name.py` with the actual name of the script.
5. Follow the prompts provided by the script to input your article and images information.
