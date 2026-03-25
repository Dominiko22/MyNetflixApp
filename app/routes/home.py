"""
Główny router (Widok) prezentacyjny interfejsu wizualnego UI.
Zarządza logiką domyślnej strony internetowej (Home) generując dynamiczne struktury
(Hero Banner, Półki karuzelowe wg popularności/gatunku) oraz panelem profilu gracza z ulubionymi wpisami.
"""

from flask import Blueprint, render_template, redirect, url_for, session
from app.db.models import db, User, Favorite
from app.ml.engine import fetch_movie_details_cached, fetch_game_details_cached, movies, games
import pandas as pd
import random

main_bp = Blueprint('main_bp', __name__)

@main_bp.route("/")
def home():
    # Pobieranie 14 hitów dla filmów
    top_movies_df = movies.sort_values(by="rating", ascending=False).head(14)
    popular_movies = []
    for t in top_movies_df["title"]:
        d = fetch_movie_details_cached(t)
        if d:
            popular_movies.append({"title": t, "poster": d.get("Poster"), "backdrop": d.get("Backdrop")})

    # Pobieranie 14 hitów dla gier
    top_games_df = games.sort_values(by="total_rating", ascending=False).head(
        14) if "total_rating" in games.columns else games.head(14)
    popular_games = []
    for t in top_games_df["title"]:
        d = fetch_game_details_cached(t)
        if d:
            popular_games.append({"title": t, "poster": d.get("Poster"), "backdrop": d.get("Backdrop")})

    # --- Hero Banner (Slider) ---
    hero_movies = []
    hero_games = []
    max_attempts = 40  # Zabezpieczenie przed nieskończoną pętlą
    attempts = 0
    wanted_hero_count = 5
    
    while (len(hero_movies) < wanted_hero_count or len(hero_games) < wanted_hero_count) and attempts < max_attempts:
        attempts += 1
        
        # Szukamy filmów aż uzbieramy 5 sztuk
        if len(hero_movies) < wanted_hero_count and not movies.empty:
            random_idx = random.randint(0, len(movies) - 1)
            t = movies.iloc[random_idx]["title"]
            d = fetch_movie_details_cached(t)
            if d and d.get("Backdrop"):
                if not any(item["title"] == t for item in hero_movies):
                    hero_movies.append({
                        "title": t,
                        "poster": d.get("Poster"),
                        "backdrop": d.get("Backdrop"),
                        "type": "movie"
                    })
                    
        # Szukamy gier aż uzbieramy 5 sztuk
        if len(hero_games) < wanted_hero_count and not games.empty:
            random_idx = random.randint(0, len(games) - 1)
            t = games.iloc[random_idx]["title"]
            d = fetch_game_details_cached(t)
            if d and d.get("Backdrop"):
                if not any(item["title"] == t for item in hero_games):
                    hero_games.append({
                        "title": t,
                        "poster": d.get("Poster"),
                        "backdrop": d.get("Backdrop"),
                        "type": "game"
                    })

    # --- Tematyczne Karuzele ---
    # Losujemy 2 gatunki/słowa kluczowe dla filmów i 1 dla gier, aby wykreować angażujące półki.
    movie_genres = ["Action", "Comedy", "Horror", "Drama", "Animation", "Sci-Fi", "Thriller"]
    game_genres = ["Action", "RPG", "Sports", "Adventure", "Strategy", "Shooter"]
    
    # Przykładowe kreatywne nagłówki
    movie_headers = {
        "Action": "Zastrzyk adrenaliny 💥", "Comedy": "Na poprawę humoru 😂", 
        "Horror": "Tylko dla odważnych 👻", "Drama": "Poruszające historie 🎭", 
        "Animation": "Wizualne perełki 🎨", "Sci-Fi": "Granice wyobraźni 🛸", 
        "Thriller": "Trzymające w napięciu 🔪"
    }
    game_headers = {
        "Action": "Szybka akcja i refleks ⚡", "RPG": "Epickie przygody na setki godzin 🗡️", 
        "Sports": "Sportowe emocje ⚽", "Adventure": "Wyrusz w nieznane 🗺️", 
        "Strategy": "Zostań genialnym taktykiem ♟️", "Shooter": "Gorące strzelaniny 🔫"
    }
    
    selected_movie_genres = random.sample(movie_genres, 2)
    selected_game_genre = random.choice(game_genres)
    
    # Funkcja pomocnicza do budowania rzędu
    def build_carousel_row(df, genre_col, target_genre, header, fetch_func, is_game=False):
        # Filtrujemy bazę po gatunku (zakładając że mamy kolumnę genres, dla bezpieczeństwa szukamy stringa)
        if "genres" in df.columns:
            filtered = df[df["genres"].fillna("").str.contains(target_genre, case=False, na=False)]
        else:
            filtered = df.head(50) # fallback
            
        items = []
        # Sortowanie np. po ocenie by odrzucić najsłabsze na stronie głównej
        sort_col = "total_rating" if is_game and "total_rating" in df.columns else ("rating" if "rating" in df.columns else None)
        if sort_col and not filtered.empty:
            top_filtered = filtered.sort_values(by=sort_col, ascending=False).head(20)
        else:
            top_filtered = filtered.head(20)
            
        # Z 20 najlepszych w gatunku, wybieramy 10 losowych do wyświetlenia
        if not top_filtered.empty:
            sampled = top_filtered.sample(n=min(10, len(top_filtered)))
            for t in sampled["title"]:
                d = fetch_func(t)
                if d and d.get("Poster"):
                    items.append({"title": t, "poster": d.get("Poster"), "backdrop": d.get("Backdrop")})
        return {"header": header, "content_items": items, "is_game": is_game}

    # Budujemy pule
    carousels = []
    
    # 1. Główny rząd (Globalne hity wszech czasów - mix)
    global_hits = popular_movies[:7] + popular_games[:7]
    random.shuffle(global_hits) # Mieszamy na pierwszej półce!
    # Jeśli mix się nie udał, dorzucamy fallbacki
    if not global_hits: global_hits = popular_movies
    carousels.append({"header": "Złota Aleja Rekomendacyjna 🏆", "content_items": global_hits, "is_game": False})
    
    # 2. Tematyczny Rząd Filmowy #1
    g1 = selected_movie_genres[0]
    carousels.append(build_carousel_row(movies, "genres", g1, movie_headers[g1], fetch_movie_details_cached))
    
    # 3. Tematyczny Rząd Gier #1
    gg1 = selected_game_genre
    carousels.append(build_carousel_row(games, "genres", gg1, game_headers[gg1], fetch_game_details_cached, is_game=True))
    
    # 4. Tematyczny Rząd Filmowy #2
    g2 = selected_movie_genres[1]
    carousels.append(build_carousel_row(movies, "genres", g2, movie_headers[g2], fetch_movie_details_cached))


    return render_template(
        "index.html",
        carousels=carousels, # Zamiast pojedynczych popular_movies i popular_games przekazujemy dynamiczne paczki!
        hero_movies=hero_movies,
        hero_games=hero_games,
        show_results=False,
        genre_items=None,
        game_genre_items=None
    )

@main_bp.route("/profile")
def profile_page():
    if 'user' not in session:
        return redirect(url_for('auth.login'))
    user = User.query.filter_by(
        email=session['user']['email'].strip().lower()).first()
    return render_template("profile.html", user=session['user'], favorites_movies=[f for f in user.favorites if f.category == 'movie'] if user else [], favorites_games=[f for f in user.favorites if f.category == 'game'] if user else [])

@main_bp.route('/delete_favorite/<int:fav_id>', methods=['POST'])
def delete_favorite(fav_id):
    fav = Favorite.query.get_or_404(fav_id)
    if 'user' in session and fav.user_email == session['user']['email']:
        db.session.delete(fav)
        db.session.commit()
    return redirect(url_for('main_bp.profile_page'))
