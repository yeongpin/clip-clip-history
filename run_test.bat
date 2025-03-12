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

:: 設置 Python 不生成 __pycache__ 或將其放在 venv 中
set PYTHONPYCACHEPREFIX=venv/__pycache__
:: 或者完全禁用 __pycache__
:: set PYTHONDONTWRITEBYTECODE=1

echo Running application...
python src\main.py
if errorlevel 1 (
    echo Application terminated with error code %errorlevel%
)

echo Done!
pause 