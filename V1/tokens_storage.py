import requests
import json
from requests.auth import HTTPBasicAuth


def save_tokens(tokens: dict):
    """Save tokens (including realmId if present)."""
    with open("tokens.json", "w") as f:
        json.dump(tokens, f, indent=4)
    print("💾 Tokens saved → tokens.json")


def get_tokens(auth_code: str):
    """Exchange authorization code for access + refresh tokens."""

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    payload = {
        "grant_type": "authorization_code",
        "code": auth_code,
        "redirect_uri": REDIRECT_URI
    }

    response = requests.post(
        TOKEN_URL,
        data=payload,
        headers=headers,
        auth=HTTPBasicAuth(CLIENT_ID, CLIENT_SECRET)
    )

    if response.status_code != 200:
        raise Exception(f"❌ Failed to get tokens: {response.text}")

    tokens = response.json()
    save_tokens(tokens)
    return tokens


def refresh_tokens(refresh_token: str):
    """Use refresh token to obtain new access token."""

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    payload = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token
    }

    response = requests.post(
        TOKEN_URL,
        data=payload,
        headers=headers,
        auth=HTTPBasicAuth(CLIENT_ID, CLIENT_SECRET)
    )

    if response.status_code != 200:
        raise Exception(f"❌ Failed to refresh tokens: {response.text}")

    tokens = response.json()
    save_tokens(tokens)
    print("♻️ Tokens refreshed successfully.")
    return tokens

