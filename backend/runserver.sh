#!/bin/bash
# Activate virtual environment and run server for Git Bash
set -e

if [ ! -f "venv/Scripts/activate" ]; then
    echo "Error: Virtual environment not found at venv/Scripts/activate"
    echo "Please run this script from the backend directory with: bash runserver.sh"
    exit 1
fi

echo "Activating virtual environment..."
source venv/Scripts/activate

echo "Starting Django development server..."
python manage.py runserver
