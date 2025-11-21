from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from pydantic import BaseModel
from database.config import config




class Settings(BaseModel):
    MAIL_USERNAME: str = "kayley62@ethereal.email"
    MAIL_PASSWORD: str = "QGDDaVcPcNYrkpx9Xy"
    MAIL_FROM: str = "your_email@gmail.com"
    MAIL_PORT: int = 587
    MAIL_SERVER: str = "smtp.ethereal.email"
    MAIL_FROM_NAME: str = "File Finder App"
    MAIL_STARTTLS: bool = True
    MAIL_SSL_TLS: bool = False
    USE_CREDENTIALS: bool = True


settings = Settings()

conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_FROM_NAME=settings.MAIL_FROM_NAME,
    MAIL_STARTTLS=settings.MAIL_STARTTLS,
    MAIL_SSL_TLS=settings.MAIL_SSL_TLS,
    USE_CREDENTIALS=settings.USE_CREDENTIALS,
)


fm = FastMail(conf)


# import os, smtplib
# from email.message import EmailMessage

# SMTP_HOST = os.getenv("SMTP_HOST") or os.getenv("SMTP_SERVER")  # works with either
# SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
# SMTP_USER = os.getenv("SMTP_USER") or os.getenv("SMTP_USERNAME")
# SMTP_PASS = os.getenv("SMTP_PASS") or os.getenv("SMTP_PASSWORD")
# FROM_EMAIL = os.getenv("FROM_EMAIL", SMTP_USER or "no-reply@example.com")


# def send_verification_email(to_email: str, subject: str, body: str):
#     msg = EmailMessage()
#     msg["From"] = FROM_EMAIL
#     msg["To"] = to_email
#     msg["Subject"] = subject
#     msg.set_content(body)

#     with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=10) as smtp:
#         smtp.starttls()
#         if SMTP_USER and SMTP_PASS:
#             smtp.login(SMTP_USER, SMTP_PASS)
#         smtp.send_message(msg)


# def send_password_reset_email(to_email: str, code: str):
#     subject = "Your Password Reset Code"
#     body = f"Your password reset code is: {code}\nIt expires in 15 minutes."
#     msg = EmailMessage()
#     msg["From"] = FROM_EMAIL
#     msg["To"] = to_email
#     msg["Subject"] = subject
#     msg.set_content(body)

#     with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=10) as smtp:
#         smtp.starttls()
#         if SMTP_USER and SMTP_PASS:
#             smtp.login(SMTP_USER, SMTP_PASS)
#         smtp.send_message(msg)