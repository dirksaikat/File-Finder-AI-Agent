import os, smtplib
from email.message import EmailMessage

SMTP_HOST = os.getenv("SMTP_HOST") or os.getenv("SMTP_SERVER")  # works with either
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER") or os.getenv("SMTP_USERNAME")
SMTP_PASS = os.getenv("SMTP_PASS") or os.getenv("SMTP_PASSWORD")
FROM_EMAIL = os.getenv("FROM_EMAIL", SMTP_USER or "no-reply@example.com")


def send_verification_email(to_email: str, subject: str, body: str):
    msg = EmailMessage()
    msg["From"] = FROM_EMAIL
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.set_content(body)

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=10) as smtp:
        smtp.starttls()
        if SMTP_USER and SMTP_PASS:
            smtp.login(SMTP_USER, SMTP_PASS)
        smtp.send_message(msg)


def send_password_reset_email(to_email: str, code: str):
    subject = "Your Password Reset Code"
    body = f"Your password reset code is: {code}\nIt expires in 15 minutes."
    msg = EmailMessage()
    msg["From"] = FROM_EMAIL
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.set_content(body)

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=10) as smtp:
        smtp.starttls()
        if SMTP_USER and SMTP_PASS:
            smtp.login(SMTP_USER, SMTP_PASS)
        smtp.send_message(msg)