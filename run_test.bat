@echo off
echo Checking virtual environment...
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Installing requirements...
pip install -r requirements.txt

:: set Python not to generate __pycache__ or put it in venv
set PYTHONPYCACHEPREFIX=venv/__pycache__
:: or disable __pycache__
:: set PYTHONDONTWRITEBYTECODE=1

echo Running application...
python src\main.py
if errorlevel 1 (
    echo Application terminated with error code %errorlevel%
)

echo Done!
pause 