import json
import os

USER_FILE = 'users.json'


def load_user():
    """Loads all registered users."""
    if os.path.exists(USER_FILE):
        with open(USER_FILE, "r") as f:
            return json.load(f)
    return {}


def save_users(users):
    """Save all user data."""
    with open(USER_FILE, "w") as f:
        json.dump(users, f, indent=4)
