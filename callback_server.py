from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
import urllib.parse
import uvicorn

CLIENT_ID = "ABRgRvGV49OOIiERh6ICf4yvyvBRIRCVgodNO3iFbRHP4Ih393"
REDIRECT_URI = "http://localhost:9000/callback"
SCOPES = "com.intuit.quickbooks.accounting openid profile email"
AUTH_URL = "https://appcenter.intuit.com/connect/oauth2"

app = FastAPI()

@app.get("/auth")
async def auth():
    params = {
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "response_type": "code",
        "scope": SCOPES,
        "state": "secureRandomState123"
    }
    url = AUTH_URL + "?" + urllib.parse.urlencode(params)
    return RedirectResponse(url=url)

@app.get("/callback")
async def callback(request: Request):
    code = request.query_params.get("code")
    state = request.query_params.get("state")
    return {"Authorization code": code, "State": state}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
