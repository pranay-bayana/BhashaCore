"""Transactional email adapter. Only password reset delivery is supported."""
import os
from urllib.parse import quote
import httpx


def send_password_reset(email: str, token: str) -> bool:
    """Send through Resend when configured. Never log token or recipient."""
    if os.environ.get("EMAIL_PROVIDER", "").lower() != "resend":
        return False
    api_key, sender = os.environ.get("EMAIL_API_KEY"), os.environ.get("EMAIL_FROM")
    base_url = os.environ.get("APP_BASE_URL", "").rstrip("/")
    if not api_key or not sender or not base_url.startswith("https://"):
        return False
    reset_url = f"{base_url}/reset-password/{quote(token, safe='')}"
    response = httpx.post("https://api.resend.com/emails", timeout=10,
        headers={"Authorization": f"Bearer {api_key}"},
        json={"from": sender, "to": [email], "subject": "Reset your BhashaCore password",
              "text": f"Reset your password within one hour: {reset_url}"})
    return response.status_code in (200, 201)
