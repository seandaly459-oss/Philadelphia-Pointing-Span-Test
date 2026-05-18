"""Email validation and sending utilities for PPST."""

import re
import socket
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string


EMAIL_REGEX = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")


def is_valid_email_format(email: str) -> bool:
    """Return True if the email address is syntactically valid."""
    if not email:
        return False
    return EMAIL_REGEX.match(email) is not None


def domain_is_deliverable(email: str) -> bool:
    """Check that the email domain resolves to an address or MX record."""
    try:
        domain = email.split('@', 1)[1]
        # First try DNS MX records when dnspython is available.
        try:
            import dns.resolver
            answers = dns.resolver.resolve(domain, 'MX')
            return bool(answers)
        except Exception:
            # Fallback to basic domain resolution.
            socket.getaddrinfo(domain, None)
            return True
    except (IndexError, socket.gaierror, socket.error):
        return False


def validate_patient_email(email: str) -> tuple[bool, str]:
    """Validate a patient email for format and simple deliverability."""
    if not email:
        return False, 'Email address is required.'

    email = email.strip().lower()
    if not is_valid_email_format(email):
        return False, 'Invalid email format.'

    if not domain_is_deliverable(email):
        return False, 'Email domain is not reachable or does not appear to receive mail.'

    return True, ''


def send_test_link_email(patient_email: str, test_url: str, doctor_username: str) -> tuple[bool, str]:
    """Send a templated PPST invitation email to the patient."""
    if (
        settings.EMAIL_BACKEND == 'django.core.mail.backends.console.EmailBackend'
        and not getattr(settings, 'ALLOW_CONSOLE_EMAIL_FALLBACK', False)
    ):
        return False, (
            'Email backend is configured for console output. '
            'Set SMTP credentials in backend/.env (EMAIL_HOST_USER and EMAIL_HOST_PASSWORD) '
            'or set EMAIL_BACKEND to django.core.mail.backends.smtp.EmailBackend.'
        )

    subject = 'PPST Test Invitation'
    context = {
        'patient_email': patient_email,
        'doctor_username': doctor_username,
        'test_url': test_url,
        'test_name': 'Philadelphia Pointing Span Test',
    }
    html_message = render_to_string('portal/emails/test_link_email.html', context)
    text_message = render_to_string('portal/emails/test_link_email.txt', context)

    try:
        send_mail(
            subject=subject,
            message=text_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[patient_email],
            html_message=html_message,
            fail_silently=False,
        )
        return True, 'Email sent successfully.'
    except Exception as exc:
        return False, str(exc)
