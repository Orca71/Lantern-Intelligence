import urllib.parse

CLIENT_ID = "ABRgRvGV49OOIiERh6ICf4yvyvBRIRCVgodNO3iFbRHP4Ih393"
CLIENT_SECRET = "gqovUeRkP9x0X1iAN4VeF7xQPqn31I8OxlNCbv7Z"
REDIRECT_URI = "http://localhost:9000/callback"
TOKEN_URL = "https://oauth.platform.intuit.com/oauth2/v1/tokens/bearer"
SCOPE = "com.intuit.quickbooks.accounting openid profile email"
AUTH_BASE_URL = "https://appcenter.intuit.com/connect/oauth2"

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
