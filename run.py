"""
Punkt wejściowy (Entrypoint) uruchamiający aplikację.
Łączy i inicjalizuje wszystkie komponenty App Factory: ładuje zmienne środowiskowe, 
konfiguruje bazę danych, a następnie rejestruje podział routingu (Blueprints).
"""

from sklearn.metrics.pairwise import cosine_similarity
from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from app.ml.core_logic.movies.tmdb_client import fetch_movie_details
from app.ml.core_logic.games.igdb_client import fetch_game_details
from app.ml.core_logic.movies.movie_recommender import load_movies, recommend_movie
from app.ml.core_logic.games.game_recommender import load_games, recommend_game
from app.routes.auth import auth_bp, setup_auth
from app.db.models import db, User, Favorite
from functools import lru_cache
import numpy as np
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'twoj_sekretny_klucz_123')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///database.db')
db.init_app(app)

with app.app_context():
    db.create_all()

from app.routes.routes_main import main_bp
from app.routes.routes_api import api_bp
from app.routes.routes_content import content_bp

# Rejestracja Blueprints ze wszystkich podzielonych modułów
app.register_blueprint(main_bp)
app.register_blueprint(api_bp)
app.register_blueprint(content_bp)
app.register_blueprint(auth_bp)

if __name__ == "__main__":
    app.run(debug=True)
