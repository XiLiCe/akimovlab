@echo off

:: Name of the virtual environment directory
set VENV_DIR=.venv

:: Check if virtual environment directory already exists
if exist %VENV_DIR% (
    echo Virtual environment already exists. Activating it...
) else (
    echo Creating virtual environment...
    python -m venv %VENV_DIR%
)

:: Activate the virtual environment
call %VENV_DIR%\Scripts\activate

:: Check if requirements.txt file exists
if exist requirements.txt (
    echo Installing requirements from requirements.txt...
    pip install -r requirements.txt
) else (
    echo requirements.txt not found. Please make sure it exists in the current directory.
)

echo Setup complete. Virtual environment is ready and dependencies are installed.


echo Running app
python app.py