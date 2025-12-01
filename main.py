"""Główna aplikacja Flask udostępniająca API do rekomendacji filmów i gier."""

from flask import Flask, request, jsonify, render_template
from algorytmy.tmdb import fetch_movie_details   # <-- tu zmiana
from algorytmy.recommender_movies import load_movies, recommend_movie
from algorytmy.recommender_games import load_games, recommend_game

app = Flask(__name__)

movies, movie_sim = load_movies()
games, game_sim = load_games()


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/recommend_movie", methods=["GET"])
def recommend_movie_endpoint():
    title = request.args.get("title", "").strip()
    if not title:
        return jsonify({"error": "Brak tytułu filmu w zapytaniu"}), 400

    # algorytm rekomendacji
    base, recs = recommend_movie(movies, movie_sim, title)
    if base is None:
        return jsonify({"error": "Nie znaleziono podobnego filmu"}), 404

    # film bazowy – szczegóły z TMDB
    base_details = fetch_movie_details(base)
    base_poster = base_details.get("Poster") if base_details else None
    base_overview = base_details.get("overview") if base_details else None

    # rekomendacje z plakatami
    rec_items = []
    for t in recs:
        details = fetch_movie_details(t)
        rec_items.append({
            "title": t,
            "poster": details.get("Poster") if details else None,
        })

    return jsonify({
        "base_movie": base,
        "base_poster": base_poster,
        "base_overview": base_overview,   # <-- opis filmu bazowego
        "recommendations": rec_items,
    })



@app.route("/recommend_game", methods=["GET"])
def recommend_game_endpoint():
    title = request.args.get("title", "").strip()
    if not title:
        return jsonify({"error": "Brak tytułu gry w zapytaniu"}), 400

    base, recs = recommend_game(games, game_sim, title)
    if base is None:
        return jsonify({"error": "Nie znaleziono podobnej gry"}), 404

    return jsonify({
        "base_game": base,
        "recommendations": recs
    })


if __name__ == "__main__":
    app.run(debug=True)
