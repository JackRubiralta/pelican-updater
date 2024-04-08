@echo off
cls
echo Checking for Python installation...
python --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo Python is not installed.
    echo Downloading Python installer...
    PowerShell -Command "& { Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.12.2/python-3.12.2-amd64.exe' -OutFile 'python-3.12.2-amd64.exe' }"
    echo Starting Python installation...
    echo Please follow the installation prompts and ensure you add Python to the PATH.
    start /wait python-3.12.2-amd64.exe /quiet InstallAllUsers=1 PrependPath=1
    echo Python installation process has been initiated. Please verify the installation once completed.
) ELSE (
    echo Python is installed.
)

echo.
echo Installing required pip packages...
python -m pip install -r requirements.txt

echo.
IF EXIST github_token.txt (
    echo GitHub token found.
) ELSE (
    echo GitHub token file not found. Opening GitHub token creation page...
    start https://github.com/settings/tokens
    echo Please create a file named github_token.txt in the script's directory and paste your GitHub token inside.
)

:end
echo.
echo Setup complete.
pause
