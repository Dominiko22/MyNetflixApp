"""
Router obsługujący renderowanie specyficznych podstron w obrębie wyszukiwania katalogowego (Views).
Dostarcza treść HTML szczegółów o pojedynczym filmie, pojedynczej grze, 
złączonymi z propozycjami podobnymi (sekcje recommendations) wykorzystując odpowiednie klienty API.
"""

from flask import Blueprint, render_template
from app.ml.core_logic.movies.movie_recommender import recommend_movie
from app.ml.core_logic.games.game_recommender import recommend_game
from app.ml.engine import (movies, movie_sim, games, game_sim,
                   fetch_movie_details_cached, fetch_game_details_cached,
                   MOVIE_GENRES, GAME_GENRES)

content_bp = Blueprint('content_bp', __name__)

@content_bp.route("/movie/<path:title>")
def movie_details_page(title: str):
    details = fetch_movie_details_cached(title)
    base, recs = recommend_movie(movies, movie_sim, title)
    rec_items = []
    for t in recs:
        d = fetch_movie_details_cached(t)
        if d and d.get("Poster"):
            rec_items.append({"title": t, "poster": d.get("Poster")})
    return render_template("index.html", base_movie=title, base_poster=details.get("Poster") if details else None, base_overview=details.get("overview") if details else None, recommendations=rec_items[:14], show_results=True, initial_category="movie", current_type="movie")

@content_bp.route("/game/<path:title>")
def game_details_page(title: str):
    details = fetch_game_details_cached(title)
    base, recs = recommend_game(games, game_sim, title)

    rec_items = []
    for t in recs:
        d = fetch_game_details_cached(t)
        if d and d.get("Poster"):
            rec_items.append({"title": t, "poster": d.get("Poster")})
            if len(rec_items) >= 14:
                break

    return render_template(
        "index.html",
        base_game=title,
        base_poster=details.get("Poster") if details else None,
        base_summary=details.get("storyline") or details.get(
            "summary") if details else None,
        recommendations=rec_items,
        show_results=True,
        initial_category="game",
        current_type="game"
    )

@content_bp.route("/movies_by_genre/<genre_name>")
def movies_by_genre(genre_name: str):
    genre_id = MOVIE_GENRES.get(genre_name)
    if genre_id is None:
        return render_template("index.html", initial_category="movie", error_message=f"Nieznany gatunek: {genre_name}", show_results=False)
    mask = movies["genres"].astype(str).str.contains(
        rf"\b{genre_id}\b", regex=True, na=False)
    genre_df = movies.loc[mask]
    sample_df = genre_df.sample(n=min(len(genre_df), 40))
    genre_items = []
    for _, row in sample_df.iterrows():
        d = fetch_movie_details_cached(row["title"].strip())
        if d and d.get("Poster") and d.get("Poster") != "N/A":
            genre_items.append(
                {"title": row["title"], "poster": d.get("Poster")})
            if len(genre_items) >= 21:
                break
    return render_template("index.html", initial_category="movie", genre_items=genre_items, active_genre=genre_name, show_results=False)

@content_bp.route("/games_by_genre/<genre_name>")
def games_by_genre(genre_name: str):
    genre_id = GAME_GENRES.get(genre_name)
    if genre_id is None:
        return render_template("index.html", error_message=f"Nieznany gatunek: {genre_name}")
    mask = games["genre"].astype(str).str.contains(
        rf"\b{genre_id}\b", na=False)
    genre_df = games.loc[mask]
    sample_df = genre_df.sample(n=min(30, len(genre_df)))
    game_genre_items = []
    for _, row in sample_df.iterrows():
        d = fetch_game_details_cached(row["title"].strip())
        if d and d.get("Poster") and d.get("Poster") != "N/A":
            game_genre_items.append(
                {"title": row["title"], "poster": d.get("Poster")})
            if len(game_genre_items) >= 21:
                break
    return render_template("index.html", initial_category="game", game_genre_items=game_genre_items, active_game_genre=genre_name)
