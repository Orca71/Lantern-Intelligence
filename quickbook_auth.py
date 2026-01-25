import urllib.parse



def generate_auth_url():
    params = {
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "response_type": "code",
        "scope": SCOPE,
        "state": "secureRandomState123"
    }
    return f"{AUTH_BASE_URL}?{urllib.parse.urlencode(params)}"

if __name__ == "__main__":
    url = generate_auth_url()
    print("\n🔗 Open this URL in your browser to authorize Lantern:\n")
    print(url)

