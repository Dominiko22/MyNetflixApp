"""
Skrypt narzędziowy do ręcznego pozyskiwania tokenu dostępu OAuth2 Twitcha (IGDB API).
Nieużywany bezpośrednio przez aplikację, przydatny jedynie do logowania programistycznego
i wyciągania długoterminowych tokenów wpisywanych potem do pliku .env aplikacji.
"""

import requests

CLIENT_ID = "0t5srzummowwh0v6hwvirne5zjsbil"
CLIENT_SECRET = "cz42m1dxscsl9itdf9bs6e8g9j2jdr"

url = "https://id.twitch.tv/oauth2/token"
data = {
    "client_id": CLIENT_ID,
    "client_secret": CLIENT_SECRET,
    "grant_type": "client_credentials",
}

resp = requests.post(url, data=data, timeout=10)
resp.raise_for_status()
print(resp.json())
