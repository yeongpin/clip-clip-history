@echo off
echo Building ClipClip History...

:: Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    exit /b 1
)

:: Check if NSIS is installed
makensis /VERSION >nul 2>&1
if errorlevel 1 (
    echo Error: NSIS is not installed or not in PATH
    echo Please install NSIS from https://nsis.sourceforge.io/Download
    exit /b 1
)

:: Check if virtual environment exists
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

:: Activate virtual environment
call venv\Scripts\activate

:: Install requirements
echo Installing requirements...
pip install -r requirements.txt
pip install pyinstaller python-dotenv

:: Clean previous builds
echo Cleaning previous builds...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

:: Build executable
echo Building executable...
pyinstaller build.spec

echo Build complete!
echo Installer can be found in the dist folder

:: Deactivate virtual environment
deactivate

pause 