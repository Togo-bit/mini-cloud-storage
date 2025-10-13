from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import pandas as pd
import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import firebase_admin
from firebase_admin import credentials as fb_credentials, auth

# ------------------------------------
# Flask Configuration
# ------------------------------------
app = Flask(__name__)
app.secret_key = "your_secret_key_here"  # for Flask session handling

# ------------------------------------
# Google Sheets Configuration
# ------------------------------------
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]
google_creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(google_creds)
sheet = client.open("Form_Data").sheet1  # Replace with your Google Sheet name

# ------------------------------------
# Firebase Configuration (Google Login)
# ------------------------------------
firebase_cred = fb_credentials.Certificate("firebase_credentials.json")  # Your Firebase Service Account JSON
firebase_admin.initialize_app(firebase_cred)

# ------------------------------------
# Routes
# ------------------------------------

# 1️⃣ Landing Page or Form (based on session)
@app.route('/')
def index():
    if 'user' not in session:
        return render_template('landing.html')  # shows Google Sign-In
    return render_template('form.html', user=session['user'])  # shows form after login


# 2️⃣ Handle Google Sign-In Token
@app.route('/sessionLogin', methods=['POST'])
def session_login():
    try:
        id_token = request.json.get('idToken')
        decoded_token = auth.verify_id_token(id_token)
        session['user'] = {
            'email': decoded_token.get('email'),
            'name': decoded_token.get('name')
        }
        return jsonify({'message': 'Login successful'})
    except Exception as e:
        return jsonify({'message': str(e)}), 400


# 3️⃣ Logout
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


# 4️⃣ Handle Form Submission
@app.route('/submit', methods=['POST'])
def submit():
    try:
        # Only allow if user is logged in
        if 'user' not in session:
            return jsonify({'message': 'Unauthorized'}), 403

        # Get form data
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']

        # Append to Google Sheet
        sheet.append_row([name, email, message])

        return render_template('success.html', user=session['user'])
    except Exception as e:
        return jsonify({'message': str(e)}), 500


# ------------------------------------
# Run Flask
# ------------------------------------
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
