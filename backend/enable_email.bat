@echo off

echo ============================================
echo PPST Email Configuration Setup (Windows)
echo ============================================
echo.

set "DEFAULT_EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend"
set "DEFAULT_EMAIL_HOST=smtp.gmail.com"
set "DEFAULT_EMAIL_PORT=587"
set "DEFAULT_EMAIL_USE_TLS=True"
set "DEFAULT_EMAIL_USE_SSL=False"

echo Configure SMTP credentials for email sending.
echo For Gmail, use a 16-character App Password (not your normal Gmail password).
echo.

set /p EMAIL_BACKEND=Email backend [django.core.mail.backends.smtp.EmailBackend]: 
if "%EMAIL_BACKEND%"=="" set "EMAIL_BACKEND=%DEFAULT_EMAIL_BACKEND%"

set /p EMAIL_HOST=SMTP host [smtp.gmail.com]: 
if "%EMAIL_HOST%"=="" set "EMAIL_HOST=%DEFAULT_EMAIL_HOST%"

set /p EMAIL_PORT=SMTP port [587]: 
if "%EMAIL_PORT%"=="" set "EMAIL_PORT=%DEFAULT_EMAIL_PORT%"

set /p EMAIL_USE_TLS=Use TLS? [True/False, default=True]: 
if "%EMAIL_USE_TLS%"=="" set "EMAIL_USE_TLS=%DEFAULT_EMAIL_USE_TLS%"

set /p EMAIL_USE_SSL=Use SSL? [True/False, default=False]: 
if "%EMAIL_USE_SSL%"=="" set "EMAIL_USE_SSL=%DEFAULT_EMAIL_USE_SSL%"

:prompt_user
set /p EMAIL_HOST_USER=Email address (SMTP login): 
if "%EMAIL_HOST_USER%"=="" (
	echo Email address cannot be empty.
	goto prompt_user
)

:prompt_pass
set /p EMAIL_HOST_PASSWORD=App password: 
if "%EMAIL_HOST_PASSWORD%"=="" (
	echo App password cannot be empty.
	goto prompt_pass
)

set /p DEFAULT_FROM_EMAIL=From email display [PPST ^<%EMAIL_HOST_USER%^>]: 
if "%DEFAULT_FROM_EMAIL%"=="" set "DEFAULT_FROM_EMAIL=PPST <%EMAIL_HOST_USER%>"

echo.
set /p SAVE_TO_ENV=Also save to backend/.env for future sessions? [Y/n]: 
if "%SAVE_TO_ENV%"=="" set "SAVE_TO_ENV=Y"

echo.
echo Applying environment variables for this session...

set "EMAIL_BACKEND=%EMAIL_BACKEND%"
set "EMAIL_HOST=%EMAIL_HOST%"
set "EMAIL_PORT=%EMAIL_PORT%"
set "EMAIL_USE_TLS=%EMAIL_USE_TLS%"
set "EMAIL_USE_SSL=%EMAIL_USE_SSL%"
set "EMAIL_HOST_USER=%EMAIL_HOST_USER%"
set "EMAIL_HOST_PASSWORD=%EMAIL_HOST_PASSWORD%"
set "DEFAULT_FROM_EMAIL=%DEFAULT_FROM_EMAIL%"

if /I "%SAVE_TO_ENV%"=="Y" (
	> .env (
		echo EMAIL_BACKEND=%EMAIL_BACKEND%
		echo EMAIL_HOST=%EMAIL_HOST%
		echo EMAIL_PORT=%EMAIL_PORT%
		echo EMAIL_USE_TLS=%EMAIL_USE_TLS%
		echo EMAIL_USE_SSL=%EMAIL_USE_SSL%
		echo EMAIL_HOST_USER=%EMAIL_HOST_USER%
		echo EMAIL_HOST_PASSWORD=%EMAIL_HOST_PASSWORD%
		echo DEFAULT_FROM_EMAIL=%DEFAULT_FROM_EMAIL%
		echo ALLOW_CONSOLE_EMAIL_FALLBACK=False
	)
	echo Saved settings to backend/.env
)

echo.
echo Active values:
echo   EMAIL_BACKEND=%EMAIL_BACKEND%
echo   EMAIL_HOST=%EMAIL_HOST%
echo   EMAIL_PORT=%EMAIL_PORT%
echo   EMAIL_USE_TLS=%EMAIL_USE_TLS%
echo   EMAIL_USE_SSL=%EMAIL_USE_SSL%
echo   EMAIL_HOST_USER=%EMAIL_HOST_USER%
echo   DEFAULT_FROM_EMAIL=%DEFAULT_FROM_EMAIL%
echo.
echo Next step: run "python manage.py runserver" in this same terminal.