#!/bin/bash

echo "Building ClipClip History..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    exit 1
fi

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install requirements
echo "Installing requirements..."
pip install -r requirements.txt
pip install pyinstaller python-dotenv

# Clean previous builds
echo "Cleaning previous builds..."
rm -rf build dist

# Build executable
echo "Building executable..."
pyinstaller build.spec

echo "Build complete!"
echo "Executable can be found in the dist folder"

# Deactivate virtual environment
deactivate 