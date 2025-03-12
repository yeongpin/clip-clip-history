#!/bin/bash

echo "Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed. Please install it first."
    exit 1
fi

echo "Cleaning up old environment..."
rm -rf venv

echo "Creating virtual environment..."
python3 -m venv venv

echo "Activating virtual environment..."
source venv/bin/activate || { echo "Error activating virtual environment"; exit 1; }

echo "Upgrading pip..."
pip install --upgrade pip

echo "Installing requirements..."
pip install -r requirements.txt || { echo "Failed to install requirements"; exit 1; }

# Set Python cache settings
export PYTHONPYCACHEPREFIX=venv/__pycache__
# export PYTHONDONTWRITEBYTECODE=1  # Uncomment to completely disable __pycache__

echo "Running application..."
python src/main.py

if [ $? -ne 0 ]; then
    echo "Application failed to run. Attempting to reinstall PyQt6..."
    pip uninstall -y PyQt6 PyQt6-Qt6 PyQt6-sip
    pip install PyQt6==6.4.2
    echo "Running application again..."
    python src/main.py
fi

echo "Done!"
