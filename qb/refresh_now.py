import json
from tokens_storage import refresh_tokens

with open("tokens.json", "r") as f:
    tokens = json.load(f)

refresh_token = tokens["refresh_token"]

print("🔄 Refreshing tokens...")
refresh_tokens(refresh_token)
