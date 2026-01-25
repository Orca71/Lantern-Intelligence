import requests
import base64
import json



def exchange_code_for_tokens(auth_code: str):
    basic_auth = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()

    headers = {
        "Accept": "application/json",
        "Authorization": f"Basic {basic_auth}",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    data = {
        "grant_type": "authorization_code",
        "code": auth_code,
        "redirect_uri": REDIRECT_URI
    }

    response = requests.post(TOKEN_URL, headers=headers, data=data)

    if response.status_code != 200:
        print("❌ Error exchanging code:", response.text)
        return None

    tokens = response.json()

    # SAVE tokens.json
    with open("tokens.json", "w") as f:
        json.dump(tokens, f, indent=4)

    print("✅ Tokens saved to tokens.json")
    print(tokens)
    return tokens


if __name__ == "__main__":
    auth_code = input("Paste the authorization code: ")
    exchange_code_for_tokens(auth_code)

