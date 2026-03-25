"""
Moduł odpowiedzialny za autoryzację i sesje użytkowników.
Obejmuje proces logowania w standardzie OAuth 2.0 (Google), callback, 
oraz zarządza danymi tymczasowymi autoryzacji sesji.
"""

import os
from flask import Blueprint, url_for, redirect, session, render_template
from authlib.integrations.flask_client import OAuth
from dotenv import load_dotenv
load_dotenv()

# Tworzymy Blueprint, żeby łatwo było podpiąć to pod main.py
auth_bp = Blueprint('auth', __name__)

oauth = OAuth()


def setup_auth(app):
    """
    Konfiguruje mechanizm OAuth 2.0 dla aplikacji flask.

    1. Ustawia Secret Key niezbędny do bezpiecznego szyfrowania sesji.
    2. Rejestruje Google jako dostawcę tożsamości.
    3. Pobiera konfigurację OpenID (adresy URL do logowania/tokenów) z serwerów Google
    """
    app.secret_key = os.getenv("SECRET_KEY")
    oauth.init_app(app)

    # Konfiguracja Google
    oauth.register(
        name='google',
        client_id=os.getenv("GOOGLE_CLIENT_ID"),
        # <--- POPRAWIONE z client_server
        client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
        client_kwargs={
            'scope': 'openid email profile'
        }
    )


@auth_bp.route('/login')
def login():
    """
    Inicjuje porces logowania.
    Generuje uniklany link i przekierowuje użytkownika na stronę logowania Google.
    """
    # Przekierowanie do Google
    redirect_uri = url_for('auth.callback', _external=True)
    return oauth.google.authorize_redirect(redirect_uri)


@auth_bp.route('/callback')
def callback():
    """
    Punkt zwrotny, do którego Google odsyła użytkownika po udanym logowaniu.

    Proces:
    1. Wymienia tymczsowy kod od Google na stały Access Token.
    2. Pobiera dane o użytkoniku (userinfo).
    3. Czyści adres email (małe litery, brak spacji) i zapisuje profil w sesji.
    """
    token = oauth.google.authorize_access_token()
    user_info = token.get('userinfo')

    if user_info:
        # Normalizujemy email od razu
        clean_email = user_info.get("email", "").strip().lower()
        session['user'] = {
            "name": user_info.get("name"),
            "email": clean_email,
            "picture": user_info.get("picture"),
        }
        print(f"Zalogowano użytkownika: {session['user']}")

    return redirect('/')


@auth_bp.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')


