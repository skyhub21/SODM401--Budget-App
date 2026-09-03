import os
from dotenv import load_dotenv
load_dotenv()

from flask import Flask, render_template, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from models import db
from services.gmail_service import GmailService
from authlib.integrations.flask_client import OAuth

# Initialize extensions
oauth = OAuth() 

def create_app():
    app = Flask(__name__)

    # Configuration
    app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY')
    app.config['SESSION_TYPE'] = 'filesystem'

    # DB Config
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("SQLITE_DATABASE_URL")
    #app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Email Configurations
    app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
    app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'True').lower() == 'true'
    app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
    app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER', os.getenv('MAIL_USERNAME'))
    app.config['MAIL_TIMEOUT'] = int(os.getenv('MAIL_TIMEOUT', 30))

    # Microsoft OAuth Configuration
    app.config['OAUTH2_CLIENT_ID'] = os.getenv('MICROSOFT_CLIENT_ID')
    app.config['OAUTH2_CLIENT_SECRET'] = os.getenv('MICROSOFT_CLIENT_SECRET')

    db.init_app(app)
    oauth.init_app(app)
    
    # Register Microsoft OAuth client
    oauth.register(
    name='microsoft',
    client_id=os.getenv('AZURE_CLIENT_ID'),
    client_secret=os.getenv('AZURE_CLIENT_SECRET'),
    authorize_url='https://login.microsoftonline.com/common/oauth2/v2.0/authorize',
    access_token_url='https://login.microsoftonline.com/common/oauth2/v2.0/token',
    api_base_url='https://graph.microsoft.com/v1.0/',
    jwks_uri='https://login.microsoftonline.com/common/discovery/v2.0/keys',
    client_kwargs={
        'scope': 'openid profile email User.Read',
        'prompt': 'select_account'
    }
    )
    
    app.gmail_service = GmailService(app)
    
    return app

app = create_app()

# Create database tables
with app.app_context():
    db.create_all()


@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    # Starts the local development server
    app.run(debug=True)
'''
if __name__ == '__main__':
    app.run(debug=True, ssl_context=('cert.pem', 'key.pem'), host='127.0.0.1', port=5000)
'''