# Instrukcja Uruchomienia i Konfiguracji

Ten dokument przeprowadzi Cię przez proces instalacji środowiska, konfiguracji kluczy API oraz pierwszego uruchomienia systemu rekomendacji.

![[Pasted image 20260112182659.png]]

## 1. Wymagania wstępne

Zanim zaczniesz, upewnij się, że masz zainstalowane:

- **Python 3.9+**
    
- **Git**
    
- Konto deweloperskie w: **TMDB**, **Twitch (IGDB)** oraz **Google Cloud Console**.

## 2. Instalacja środowiska

Skopiuj repozytorium i przygotuj izolowane środowisko wirtualne:

```Bash
# 1. Sklonuj repozytorium
git clone https://github.com/twoj-username/media-recommender.git
cd media-recommender

# 2. Stwórz środowisko wirtualne
python -m venv venv

# 3. Aktywuj środowisko
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 4. Zainstaluj biblioteki
pip install -r requirements.txt
```

## 3. Konfiguracja zmiennych środowiskowych (`.env`)

Aplikacja wymaga kluczy API do poprawnego działania. Stwórz w głównym folderze plik o nazwie `.env` i uzupełnij go według wzoru:

```Python
# Flask Security
SECRET_KEY=twoj_bardzo_tajny_klucz

# API Keys
TMDB_API_KEY=twoj_klucz_tmdb
IGDB_CLIENT_ID=twoj_client_id_igdb
IGDB_CLIENT_SECRET=twoj_client_secret_igdb

# Google OAuth
GOOGLE_CLIENT_ID=twoj_google_id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=twoj_google_secret
```

>[!WARNING] Bezpieczeństwo 
>Plik `.env` jest automatycznie ignorowany przez Git (dzięki `.gitignore`). Nigdy nie usuwaj go z listy ignorowanych, aby Twoje klucze nie wyciekły do sieci.

## 4. Inicjalizacja Danych (ETL)

Przed pierwszym uruchomieniem serwera musisz wygenerować lokalne bazy danych CSV oraz zainicjować bazę SQL.

```Bash
# 1. Pobierz dane o filmach z TMDB
python algorytmy/generate_movies_from_tmdb.py

# 2. Pobierz dane o grach z IGDB
python algorytmy/generate_games_from_igdb.py
```

## 5. Uruchomienie aplikacji

Gdy dane są gotowe, a klucze skonfigurowane, możesz odpalić serwer deweloperski:

```Bash
flask run
```
>[!NOTE] Adres
>Aplikacja będzie dostępna pod adresem: `http://127.0.0.1:5000`


## 6. Przegląd Struktury Projektu

- 📂 **`algorytmy/`** – Serce systemu. Zawiera silniki rekomendacji oraz bramy (gateways) do zewnętrznych API.
    
    - `recommender_movies.py` / `recommender_games.py` – Logika wektoryzacji i podobieństwa.
        
    - `tmdb.py` / `igdb.py` – Moduły komunikacji z API.
        
- 📂 **`dataset/`** – Folder na wygenerowane pliki CSV (wynik działania skryptów ETL).
    
- 📂 **`instance/`** – Zawiera lokalną bazę danych SQLite (`database.db`).
    
- 📂 **`templates/`** & **`static/`** – Warstwa prezentacji (HTML/CSS).
    
- 📄 **`main.py`** – Punkt wejścia aplikacji Flask, łączący autoryzację z logiką rekomendacji.
    
- 📄 **`auth.py`** – Obsługa logowania przez Google OAuth.