# Email Configuration Guide for PPST Development

## Why Emails Aren't Arriving

In development mode (DEBUG=True), Django uses the console email backend by default, which prints emails to the terminal instead of sending them. This is for safety during development.

## To Enable Real Email Sending

### Option 1: Gmail SMTP (Easiest)

1. **Enable 2-Factor Authentication** on your Gmail account if not already enabled.

2. **Generate an App Password**:
   - Go to https://myaccount.google.com/security
   - Click "2-Step Verification" > "App passwords"
   - Select "Mail" and "Other (custom name)"
   - Enter "PPST Development" as the name
   - Copy the 16-character password

3. **Run the Setup Script**:

   **On macOS, Linux, or Windows (Git Bash)**:
   ```bash
   chmod +x backend/enable_email.sh
   source backend/enable_email.sh
   # Answer the prompts with your Gmail credentials
   ```

   **On Windows (Command Prompt or PowerShell)**:
   ```cmd
   cd backend
   .\enable_email.bat
   ```

   On Windows, the script can save credentials to `backend/.env`, which is recommended.
   Django loads `backend/.env` automatically via `load_dotenv`, so email config works across new terminal sessions.

4. **Run with Email Enabled**:
   ```bash
   python manage.py runserver
   ```

   The environment variables from the setup script will remain active in your current terminal session.

### Option 2: Other SMTP Providers

For production or other providers (SendGrid, Mailgun, etc.), set these variables:

```
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=your-smtp-host
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-username
EMAIL_HOST_PASSWORD=your-password
```

### Option 3: Console Testing (Current Default)

Emails will print to the Django console/terminal. Check the output when creating tests.

## Testing Email Sending

After configuration, create a test through the dashboard and check:
1. Browser network tab for success response
2. Terminal output for any errors
3. Your email inbox (may take 1-2 minutes)

## Troubleshooting

- **Emails in Spam**: Check spam/junk folder
- **Authentication Errors (535 BadCredentials)**:
   - Use a Gmail **App Password** (16 characters), not your normal Gmail password
   - Ensure `EMAIL_HOST_USER` is the full Gmail address
   - If you changed password recently, generate a new App Password and update `backend/.env`
   - Confirm no extra spaces or quotes were pasted into credentials
- **Connection Errors**: Check firewall/antivirus blocking SMTP
- **Still not working**: Temporarily set DEBUG=False to force SMTP backend