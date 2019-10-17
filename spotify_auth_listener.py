from flask import Flask, escape, request, make_response, redirect
import requests
import os
import random
import base64

client_id = os.environ.get('SPOTIFY_CLIENT_ID')
client_secret = os.environ.get('SPOTIFY_CLIENT_SECRET')
redirect_uri = 'http://localhost:3000/callback'

def generate_random_string(length):
    text = ''
    possible = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
    
    for i in range(length):
        text += random.choice(possible)
    
    return text

state_key = 'spotify_auth_state'
scope = 'user-read-private user-read-email user-top-read'

def get_auth_url(state):
    params = {
        'response_type': 'code',
        'client_id': client_id,
        'scope': scope,
        'redirect_uri': redirect_uri,
        'state': state    }

    url = 'https://accounts.spotify.com/authorize' 
    request = requests.Request('GET', url, params=params).prepare()
    auth_url = request.url
    return auth_url

app = Flask(__name__)

@app.route('/')
def hello():
    name = request.args.get("name", "World")
    return f'Hello, {escape(name)}!'

@app.route('/spotify')
def spotify():
    state = request.args.get('id')
    redirect_url = get_auth_url(state)
    
    resp = make_response(redirect(redirect_url))
    resp.set_cookie('stateKey', state)
    return resp

@app.route('/callback')
def callback():
    code = request.args.get('code')
    state = request.args.get('state')
    stored_state = request.cookies.get('stateKey')
    
    if code is None:
        return "ERROR: Missing authorization code"
    if state is None:
        return "ERROR: Missing state"
    if not state == stored_state:
        return f"ERROR: State mismatch"
    
    resp = make_response("You can now close this page")
    # resp.delete_cookie('stateKey')

    params = {
        'code': code,
        'redirect_uri': redirect_uri,
        'grant_type': 'authorization_code'
    }
    
    encodedBytes = base64.b64encode(f"{client_id}:{client_secret}".encode("utf-8"))
    headers = {
        'Authorization': 'Basic ' + str(encodedBytes, "utf-8")
    }

    response = requests.post('https://accounts.spotify.com/api/token', data=params, headers=headers)
    
    data = response.json()
    
    

    return resp

if __name__ == "__main__":
    app.run(host='0.0.0.0')
