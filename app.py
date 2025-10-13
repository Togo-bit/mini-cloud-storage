# app.py
import os
import json
from flask import Flask, render_template, request, session, redirect, url_for
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import firebase_admin
from firebase_admin import credentials as fb_creds, auth as fb_auth

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "change_this_in_production")

# ---------- Google Sheets / service account ----------
# Load service account from environment variable (Render)
google_creds_json = os.getenv("GOOGLE_CREDENTIALS")
creds_dict = json.loads(google_creds_json)
# gspread auth
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
gcreds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
gclient = gspread.authorize(gcreds)
sheet = gclient.open("form_responses").sheet1

# ---------- Initialize firebase_admin using same service account ----------
# (firebase_admin uses a service account to verify ID tokens)
if not firebase_admin._apps:
    fb_cred = fb_creds.Certificate(creds_dict)
    firebase_admin.initialize_app(fb_cred)

# ---------- Routes ----------
@app.route('/')
def index():
    # If user not logged in, show a landing page with sign-in option
    if 'user' not in session:
        return render_template('landing.html')  # contains "Sign in with Google" button
    return render_template('form.html', user=session['user'])

@app.route('/sessionLogin', methods=['POST'])
def session_login():
    # Frontend posts ID token in JSON body: { "idToken": "<token>" }
    id_token = request.json.get('idToken')
    try:
        decoded_token = fb_auth.verify_id_token(id_token)
        # decoded_token contains uid, email, name, etc.
        session['user'] = {
            'uid': decoded_token.get('uid'),
            'email': decoded_token.get('email'),
            'name': decoded_token.get('name')
        }
        return {"status": "success"}, 200
    except Exception as e:
        return {"status": "error", "message": str(e)}, 401

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))

@app.route('/submit', methods=['POST'])
def submit():
    if 'user' not in session:
        return redirect(url_for('index'))

    name = request.form['name']
    email = request.form['email']
    feedback = request.form['feedback']

    sheet.append_row([name, email, feedback])
    return "✅ Form submitted successfully and saved to Google Sheets!"

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
