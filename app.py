from flask import Flask, render_template, request
import gspread
from oauth2client.service_account import ServiceAccountCredentials

app = Flask(__name__)

# Connect to Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
import json, os
from oauth2client.service_account import ServiceAccountCredentials

# Load credentials from environment variable instead of file
google_creds_json = os.getenv("GOOGLE_CREDENTIALS")
creds_dict = json.loads(google_creds_json)
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)

client = gspread.authorize(creds)
sheet = client.open("form_responses").sheet1  # replace with your sheet name

@app.route('/', methods=['GET', 'POST'])
def form():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        feedback = request.form['feedback']

        # Append the data to Google Sheet
        sheet.append_row([name, email, feedback])
        return "✅ Form submitted successfully and saved to Google Sheets!"
    return render_template('form.html')

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # use Render’s port or default 5000
    app.run(host='0.0.0.0', port=port)

