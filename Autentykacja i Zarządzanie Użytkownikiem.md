## 1. Google OAuth 2.0 (auth.py)

Zamiast tworzyć własny system haseł, aplikacja korzysta z **OAuth 2.0** przez Google. Dzięki temu bezpieczeństwo logowania jest w rękach Google, co zwiększa zaufanie użytkowników i upraszcza proces logowania.

### Przepływ autoryzacji (Authorization Flow)

1. **Żądanie:** Użytkownik naciska „Zaloguj przez Google”.
    
2. **Przekierowanie:** Aplikacja wysyła użytkownika do serwerów Google z `CLIENT_ID`.
    
3. **Weryfikacja:** Google potwierdza tożsamość i odsyła kod autoryzacyjny do naszej bramy `auth.py`.
    
4. **Sesja:** Serwer Flask wymienia kod na token, pobiera adres e-mail i tworzy bezpieczną sesję.

## 2. Implementacja techniczna

W pliku `auth.py` zdefiniowano logikę obsługi odpowiedzi z serwerów Google oraz integrację z bazą danych SQLAlchemy.

> [!IMPORTANT] Integracja z Bazą Danych
>  System nie tworzy nowego konta przy każdym logowaniu. Najpierw sprawdza, czy 
>  e-mail istnieje w tabeli `User`. Jeśli nie – tworzy nowy rekord. Jeśli tak – loguje na istniejące konto.

```Python
# Fragment logiki w auth.py
from flask import session, redirect, url_for
from main import db, User

def handle_google_login(user_info):
    email = user_info.get('email')
    
    # Szukanie użytkownika w bazie danych
    user = User.query.filter_by(email=email).first()
    
    if not user:
        # Rejestracja nowego użytkownika (Lazy Registration)
        user = User(email=email)
        db.session.add(user)
        db.session.commit()
    
    # Zapisanie ID użytkownika w zaszyfrowanej sesji Flask
    session['user_id'] = user.id
    return redirect(url_for('dashboard'))
```

## 3. Bezpieczeństwo sesji

Aplikacja wykorzystuje mechanizm `session` z Flask, który przechowuje dane w przeglądarce w formie zaszyfrowanej.

- **SECRET_KEY:** Klucz w pliku `.env` służy do podpisywania ciasteczek sesji. Bez niego sesja jest niemożliwa do sfałszowania.
    
- **Wylogowanie:** Usunięcie `user_id` z sesji natychmiast odcina dostęp do chronionych tras (np. `/profile`).
    

> [!WARNING] Przechowywanie danych 
> System przechowuje jedynie **adres e-mail**. Żadne inne dane z konta Google (zdjęcia, kontakty, pliki) nie są pobierane ani przetwarzane, co jest zgodne z zasadą minimalizacji danych (GDPR/RODO).

## 4. Połączenie z Silnikiem Rekomendacji

Dzięki temu, że `auth.py` identyfikuje unikalnego użytkownika w bazie SQL, system może:

1. Pobierać listę ulubionych filmów/gier przypisanych do `user.id`.
    
2. Przekazywać te tytuły do funkcji `get_recommendations()` w folderze `algorytmy/`.
    
3. Wyświetlać spersonalizowaną stronę główną ("Ponieważ polubiłeś Interstellar...").