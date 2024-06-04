#!/bin/bash

# Name of the virtual environment directory
VENV_DIR=".venv"

# Check if virtual environment directory already exists
if [ -d "$VENV_DIR" ]; then
    echo "Virtual environment already exists. Activating it..."
else
    echo "Creating virtual environment..."
    python3 -m venv $VENV_DIR
fi

# Activate the virtual environment
source $VENV_DIR/bin/activate

# Check if requirements.txt file exists
if [ -f "requirements.txt" ]; then
    echo "Installing requirements from requirements.txt..."
    pip install -r requirements.txt
else
    echo "requirements.txt not found. Please make sure it exists in the current directory."
fi

echo "Setup complete. Virtual environment is ready and dependencies are installed."

echo "Running app"
python3 app.py