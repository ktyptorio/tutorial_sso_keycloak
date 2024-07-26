from flask import Flask, redirect, url_for, request, session
from keycloak import KeycloakOpenID
from keycloak.exceptions import KeycloakError
import requests
import json
from dotenv import load_dotenv
import os

load_dotenv()  # Baca environment variables dari .env file

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY')
hostname = os.getenv('HOSTNAME')

# Konfigurasi Keycloak
KEYCLOAK_SERVER_URL = f'https://{hostname}:8443/'
KEYCLOAK_REALM_NAME = 'flask-app'
KEYCLOAK_CLIENT_ID = os.getenv('KEYCLOAK_CLIENT_ID')
KEYCLOAK_CLIENT_SECRET = os.getenv('KEYCLOAK_CLIENT_SECRET')
KEYCLOAK_REDIRECT_URI = f'http://{hostname}:5000/callback'
KEYCLOAK_SCOPES = "openid profile email"

keycloak_openid = KeycloakOpenID(
    server_url=KEYCLOAK_SERVER_URL,
    client_id=KEYCLOAK_CLIENT_ID,
    realm_name=KEYCLOAK_REALM_NAME,
    client_secret_key=KEYCLOAK_CLIENT_SECRET,
    verify=False
)

@app.route('/')
def index():
    return 'Welcome to the Flask app! <a href="/login">Login</a>'

@app.route('/login')
def login():
    return redirect(keycloak_openid.auth_url(redirect_uri=KEYCLOAK_REDIRECT_URI, scope=KEYCLOAK_SCOPES))

@app.route('/callback')
def callback():
    code = request.args.get('code')
    token_url = f"{KEYCLOAK_SERVER_URL}realms/{KEYCLOAK_REALM_NAME}/protocol/openid-connect/token"
    
    data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': KEYCLOAK_REDIRECT_URI,
        'client_id': KEYCLOAK_CLIENT_ID,
        'client_secret': KEYCLOAK_CLIENT_SECRET,
    }
    
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    
    response = requests.post(token_url, data=data, headers=headers, verify=False)
    
    if response.status_code == 200:
        token = response.json()
        access_token = token['access_token']
        refresh_token = token['refresh_token']
        
        userinfo_url = f"{KEYCLOAK_SERVER_URL}realms/{KEYCLOAK_REALM_NAME}/protocol/openid-connect/userinfo"
        userinfo_response = requests.get(userinfo_url, headers={'Authorization': f"Bearer {access_token}"}, verify=False)
        
        if userinfo_response.status_code == 200:
            userinfo = userinfo_response.json()
            session['user'] = userinfo
            session['refresh_token'] = refresh_token
            return redirect(url_for('profile'))
        else:
            return f"Failed to get user info: {userinfo_response.content}"
    else:
        return f"Failed to get token: {response.content}"

@app.route('/profile')
def profile():
    if 'user' not in session:
        return redirect(url_for('index'))
    user = session['user']
    return f'Logged in as: {user["preferred_username"]}<br><a href="/logout">Logout</a>'

@app.route('/logout')
def logout():
    refresh_token = session.get('refresh_token')
    if refresh_token:
        logout_url = f"{KEYCLOAK_SERVER_URL}realms/{KEYCLOAK_REALM_NAME}/protocol/openid-connect/logout"
        data = {
            'client_id': KEYCLOAK_CLIENT_ID,
            'client_secret': KEYCLOAK_CLIENT_SECRET,
            'refresh_token': refresh_token,
            'redirect_uri': f'http://{hostname}:5000/'
        }
        response = requests.post(logout_url, data=data, headers={'Content-Type': 'application/x-www-form-urlencoded'}, verify=False)
        session.clear()
        return redirect(f'http://{hostname}:5000/')
    else:
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.config.update(
        SESSION_COOKIE_SECURE=True,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE='Lax',
    )
    app.run(debug=True, ssl_context=('/app/server.crt.pem', '/app/server.key.pem'))
