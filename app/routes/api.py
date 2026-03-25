"""
Moduł API odpowiedzialny za asynchroniczne żądania (JSON) z frontendu.
Gromadzi w sobie endpointy do rekomendacji filmów/gier w oparciu o silnik ML (funkcje np. quiz_recommend)
często wywoływane przez AJAX bez odświeżania strony.
"""

from flask import Blueprint, request, jsonify, session, redirect, url_for
from app.ml.core_logic.movies.movie_recommender import recommend_movie
from app.ml.core_logic.games.game_recommender import recommend_game
from sklearn.metrics.pairwise import cosine_similarity
from app.ml.engine import (movies, movie_sim, movie_vectorizer, 
                   games, game_sim, game_model, GAME_EMBEDDINGS,
                   fetch_movie_details_cached, fetch_game_details_cached)
from app.db.models import db, User, Favorite

api_bp = Blueprint('api_bp', __name__)

@api_bp.route("/recommend_movie", methods=["GET"])
def recommend_movie_endpoint():
    title = request.args.get("title", "").strip()
    if not title:
        return jsonify({"error": "Brak tytułu"}), 400
    base, recs = recommend_movie(movies, movie_sim, title)
    if base is None:
        return jsonify({"error": "Nie znaleziono"}), 404
    base_details = fetch_movie_details_cached(base)
    rec_items = []
    for t in recs:
        details = fetch_movie_details_cached(t)
        if details and details.get("Poster"):
            rec_items.append({"title": t, "poster": details.get("Poster")})
    return jsonify({"base_movie": base, "base_poster": base_details.get("Poster") if base_details else None, "recommendations": rec_items})


@api_bp.route("/recommend_game", methods=["GET"])
def recommend_game_endpoint():
    title = request.args.get("title", "").strip()
    if not title:
        return jsonify({"error": "Brak tytułu"}), 400
    base, recs = recommend_game(games, game_sim, title)
    if base is None:
        return jsonify({"error": "Nie znaleziono"}), 404
    base_details = fetch_game_details_cached(base)
    rec_items = []
    for t in recs:
        d = fetch_game_details_cached(t)
        if d and d.get("Poster"):
            rec_items.append({"title": t, "poster": d.get(
                "Poster"), "summary": d.get("summary", "")})
    return jsonify({"base_game": base, "base_poster": base_details.get("Poster") if base_details else None, "recommendations": rec_items})


@api_bp.route("/add_favorite", methods=["POST"])
def add_favorite():
    user_data = session.get('user')
    if not user_data:
        return jsonify({"error": "Musisz się zalogować"}), 401
    email = user_data['email'].strip().lower()
    data = request.json
    user_record = User.query.filter_by(
        email=email).first() or User(email=email)
    if not user_record.id:
        db.session.add(user_record)
        db.session.commit()

    # Optymalizacja: Frontend podaje kategorię, eliminacja .values
    cat = data.get('category')
    
    if not cat:
         # Fallback jakby nie przesłali
         if data['title'] in games['title'].values:
             cat = 'game'
         elif data['title'] in movies['title'].values:
             cat = 'movie'

    if not Favorite.query.filter_by(user_id=user_record.id, title=data['title'], category=cat).first():
        db.session.add(Favorite(user_id=user_record.id, user_email=email,
                       title=data['title'], category=cat, poster=data.get('poster')))
        db.session.commit()
    return jsonify({"message": "success"}), 201


@api_bp.route('/api/quiz_recommend', methods=['POST'])
def quiz_recommend_api():
    data = request.get_json()
    cat = data.get('category', 'movie')
    
    keywords_string = data.get('keywords', '')
    top_n = 5
    
    if cat == 'game':
        query_vec = game_model.encode([keywords_string])
        similarities = cosine_similarity(query_vec, GAME_EMBEDDINGS).flatten()
        df = games
    else:
         query_vec = movie_vectorizer.transform([keywords_string])
         all_vectors = movie_vectorizer.transform(movies['combined'])
         similarities = cosine_similarity(query_vec, all_vectors).flatten()
         df = movies
         
    best_indices = similarities.argsort()[-top_n:][::-1]
    recs = df.iloc[best_indices]['title'].tolist()
    
    return jsonify(recs)
