#!/bin/bash

# Enable real email sending for PPST development
# Works on macOS, Linux, and Windows (Git Bash)

echo "============================================"
echo "PPST Email Configuration Setup"
echo "============================================"
echo ""

# Default values for Gmail
DEFAULT_EMAIL_BACKEND="django.core.mail.backends.smtp.EmailBackend"
DEFAULT_EMAIL_HOST="smtp.gmail.com"
DEFAULT_EMAIL_PORT="587"
DEFAULT_EMAIL_USE_TLS="True"
DEFAULT_EMAIL_USE_SSL="False"

# Prompt user for credentials
echo "Configure SMTP credentials for email sending."
echo ""

read -p "Email backend (default: django.core.mail.backends.smtp.EmailBackend): " EMAIL_BACKEND
EMAIL_BACKEND=${EMAIL_BACKEND:-$DEFAULT_EMAIL_BACKEND}

read -p "SMTP host (default: smtp.gmail.com): " EMAIL_HOST
EMAIL_HOST=${EMAIL_HOST:-$DEFAULT_EMAIL_HOST}

read -p "SMTP port (default: 587): " EMAIL_PORT
EMAIL_PORT=${EMAIL_PORT:-$DEFAULT_EMAIL_PORT}

read -p "Use TLS? (default: True) [True/False]: " EMAIL_USE_TLS
EMAIL_USE_TLS=${EMAIL_USE_TLS:-$DEFAULT_EMAIL_USE_TLS}

read -p "Use SSL? (default: False) [True/False]: " EMAIL_USE_SSL
EMAIL_USE_SSL=${EMAIL_USE_SSL:-$DEFAULT_EMAIL_USE_SSL}

read -p "Email address (your login): " EMAIL_HOST_USER
while [ -z "$EMAIL_HOST_USER" ]; do
    echo "Email address cannot be empty."
    read -p "Email address (your login): " EMAIL_HOST_USER
done

read -sp "App password (will not be displayed): " EMAIL_HOST_PASSWORD
echo ""
while [ -z "$EMAIL_HOST_PASSWORD" ]; do
    echo "App password cannot be empty."
    read -sp "App password (will not be displayed): " EMAIL_HOST_PASSWORD
    echo ""
done

read -p "From email display (default: PPST <$EMAIL_HOST_USER>): " DEFAULT_FROM_EMAIL
DEFAULT_FROM_EMAIL=${DEFAULT_FROM_EMAIL:-"PPST <$EMAIL_HOST_USER>"}

echo ""
echo "============================================"
echo "Setting environment variables..."
echo "============================================"
echo ""

# Export environment variables
export EMAIL_BACKEND="$EMAIL_BACKEND"
export EMAIL_HOST="$EMAIL_HOST"
export EMAIL_PORT="$EMAIL_PORT"
export EMAIL_USE_TLS="$EMAIL_USE_TLS"
export EMAIL_USE_SSL="$EMAIL_USE_SSL"
export EMAIL_HOST_USER="$EMAIL_HOST_USER"
export EMAIL_HOST_PASSWORD="$EMAIL_HOST_PASSWORD"
export DEFAULT_FROM_EMAIL="$DEFAULT_FROM_EMAIL"

echo "✓ EMAIL_BACKEND=$EMAIL_BACKEND"
echo "✓ EMAIL_HOST=$EMAIL_HOST"
echo "✓ EMAIL_PORT=$EMAIL_PORT"
echo "✓ EMAIL_USE_TLS=$EMAIL_USE_TLS"
echo "✓ EMAIL_USE_SSL=$EMAIL_USE_SSL"
echo "✓ EMAIL_HOST_USER=$EMAIL_HOST_USER"
echo "✓ DEFAULT_FROM_EMAIL=$DEFAULT_FROM_EMAIL"
echo ""
echo "Environment variables are set in this shell session."
echo ""
echo "You can now run:"
echo "  python manage.py runserver"
echo ""
echo "To make these persistent across terminal sessions, add to ~/.bashrc or ~/.zshrc:"
echo ""
echo "export EMAIL_BACKEND='$EMAIL_BACKEND'"
echo "export EMAIL_HOST='$EMAIL_HOST'"
echo "export EMAIL_PORT='$EMAIL_PORT'"
echo "export EMAIL_USE_TLS='$EMAIL_USE_TLS'"
echo "export EMAIL_USE_SSL='$EMAIL_USE_SSL'"
echo "export EMAIL_HOST_USER='$EMAIL_HOST_USER'"
echo "export EMAIL_HOST_PASSWORD='$EMAIL_HOST_PASSWORD'"
echo "export DEFAULT_FROM_EMAIL='$DEFAULT_FROM_EMAIL'"
echo ""
