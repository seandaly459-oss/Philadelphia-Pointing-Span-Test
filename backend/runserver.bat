@echo off
REM Activate virtual environment and run server
call venv\Scripts\activate.bat
python manage.py runserver
