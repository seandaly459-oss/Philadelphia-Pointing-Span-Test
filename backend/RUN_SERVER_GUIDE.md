# PPST Backend - Run Server Guide

## For Git Bash Users

When running the server in Git Bash, you **must** activate the virtual environment first.

### Quick Start (Copy-Paste Ready for Git Bash):

```bash
cd backend
source venv/Scripts/activate
python manage.py runserver
```

### Alternative - Use the helper script:

```bash
cd backend
bash runserver.sh
```

## For PowerShell Users:

```powershell
cd backend
venv\Scripts\Activate.ps1
python manage.py runserver
```

### Alternative - Use the batch script:

```cmd
cd backend
runserver.bat
```

## Troubleshooting

If you get "ModuleNotFoundError: No module named 'rest_framework'":

1. **Make sure you've activated the venv**:
   - Git Bash: `source venv/Scripts/activate`
   - PowerShell: `venv\Scripts\Activate.ps1`

2. **If activation didn't work**, reinstall packages:
   - Git Bash: `./venv/Scripts/pip install -r requirements-dev.txt`
   - PowerShell: `venv\Scripts\pip.exe install -r requirements-dev.txt`

3. **Check which Python is being used**:
   - Git Bash: `which python`
   - PowerShell: `Get-Command python`
   - Should show path to `backend/venv`

## Notes

- Use `requirements-dev.txt` for development (SQLite, no psycopg2)
- Use `requirements.txt` for production (with psycopg2)
