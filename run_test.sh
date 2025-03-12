#!/bin/bash
echo "Cleaning up old environment..."
rm -rf venv

echo "Creating virtual environment..."
python3 -m venv venv

echo "Activating virtual environment..."
source venv/bin/activate

echo "Installing requirements..."
pip install --upgrade pip
pip install -r requirements.txt

echo "Running application..."
python src/main.py

if [ $? -ne 0 ]; then
    echo "Application failed to run. Trying alternative installation..."
    pip uninstall -y PyQt6 PyQt6-Qt6 PyQt6-sip
    pip install PyQt6==6.4.2
    echo "Running application again..."
    python src/main.py
fi

echo "Done!" 