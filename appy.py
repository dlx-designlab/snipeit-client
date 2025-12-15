from flask import Flask, redirect, request, session, url_for
import requests
import os

app = Flask(__name__)
# In a production app, use a secure and consistent secret key!
# app.secret_key = ""
app.secret_key = os.urandom(24)


# === Snipe-IT OAuth config ===
SNIPEIT_BASE_URL = "https://dlx-it-manager-g2hcc6gxe4hmdecs.japanwest-01.azurewebsites.net/"
CLIENT_ID = "00000000000000000000000000000000"
CLIENT_SECRET = "????"
REDIRECT_URI = "https://silver-waddle-v6pvjg57v9xcpg79-5000.app.github.dev/callback"  # must match Snipe-IT exactly

# === Routes ===

@app.route("/")
def index():
    if "access_token" in session:
        return """
            <h2>Logged in</h2>
            <a href="/me">View my Snipe-IT profile</a><br>
            <a href="/logout">Logout</a>
        """
    return '<a href="/login">Login with Snipe-IT</a>'


@app.route("/login")
def login():
    auth_url = (
        f"{SNIPEIT_BASE_URL}/oauth/authorize"
        f"?client_id={CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URI}"
        f"&response_type=code"
    )
    return redirect(auth_url)


@app.route("/callback")
def callback():
    if "code" not in request.args:
        return "Error: no code returned", 400

    code = request.args.get("code")

    token_url = f"{SNIPEIT_BASE_URL}/oauth/token"

    data = {
        "grant_type": "authorization_code",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "redirect_uri": REDIRECT_URI,
        "code": code
    }

    r = requests.post(token_url, data=data)
    if r.status_code != 200:
        return f"Token error: {r.text}", 400

    token_data = r.json()
    session["access_token"] = token_data["access_token"]

    return redirect(url_for("index"))


@app.route("/me")
def me():
    if "access_token" not in session:
        return redirect(url_for("login"))

    headers = {
        "Authorization": f"Bearer {session['access_token']}",
        "Accept": "application/json"
    }

    r = requests.get(
        f"{SNIPEIT_BASE_URL}/api/v1/users/me",
        headers=headers
    )

    return r.json()


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
