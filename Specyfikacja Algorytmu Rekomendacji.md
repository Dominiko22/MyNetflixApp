# Specyfikacja Algorytmu Rekomendacji

## 1. Wektoryzacja Tekstu (TF-IDF)
System nie działa na zasadzie prostego dopasowywania słów kluczowych. Zamiast tego każdy film lub gra jest zamieniany na wektor, czyli zestaw liczb, który opisuje jego treść na podstawie opisu fabuły.

Dzięki temu można porównywać tytuły między sobą i sprawdzać, które są do siebie najbardziej podobne.
## Dlaczego TF-IDF?
Zwykłe liczenie słów nie daje dobrych efektów, bo traktuje wszystkie słowa tak samo. TF-IDF działa trochę mądrzej:

- **Pomija** bardzo częste słowa, które niewiele wnoszą (np. „the”,  „movie”)
- **Podkreśla** słowa charakterystyczne dla danego tytułu (np. „cyberpunk”, „assassin”, „noir”), które faktycznie coś o nim mówią.

> [!NOTE]  Uwaga - przygotowanie danych
>Opis fabuły jest łączony z metadanymi, takimi jak gatunki, żeby algorytm miał więcej kontekstu i lepiej rozumiał, o czym jest dany tytuł.

```python
# Implementacja procesu w recommender_movies.py
from sklearn.feature_extraction.text import TfidfVectorizer

# Inicjalizacja z usunięciem angielskich "stop words"
vectorizer = TfidfVectorizer(stop_words='english')

# Budowa profilu: Konkatenacja gatunków i opisu fabuły
movies['combined'] = movies['genres'] + " " + movies['overview']

# Generowanie macierzy rzadkiej (sparse matrix)
# fillna('') zapobiega błędom w przypadku braku opisu w bazie
tfidf_matrix = vectorizer.fit_transform(movies['combined'].fillna(''))
```

# Algorytm Podobieństwa Cosinusowego

## 2. Podobieństwo Cosinusowe (Cosine Similarity)
Po zamianie opisów na wektory przy pomocy TF-IDF każdy film lub gra jest opisana jako zestaw liczb. Żeby wygenerować rekomendacje, trzeba teraz sprawdzić, które z tych wektorów są do siebie najbardziej podobne.
## Zasada działania
Zamiast liczyć klasyczną odległość między punktami, algorytm sprawdza **kąt między wektorami**. Im mniejszy kąt, tym bardziej podobne są do siebie dwa tytuły. 

Matematycznie wyrażamy to wzorem:
![[Zrzut ekranu 2026-01-12 173520.png]]

### Dlaczego to kluczowe w NLP?
Podobieństwo cosinusowe dobrze radzi sobie z opisami o różnej długości. Jeden tytuł może mieć krótki opis, a drugi bardzo długi, ale jeśli pojawiają się w nich podobne słowa, takie jak „space”, „war” czy „galaxy”, to algorytm uzna je za podobne i zwróci wysoki wynik dopasowania.

> [!IMPORTANT] Interpretacja wyników
> - **Wynik 1.0 (Cos θ = 1):** Wektory mają ten sam kierunek. Treści są identyczne tematycznie.
> - **Wynik 0.0 (Cos θ = 0):** Wektory są prostopadłe. Treści nie mają ze sobą nic wspólnego.

## Implementacja techniczna
W projekcie wykorzystujemy zoptymalizowaną funkcję z biblioteki `scikit-learn`.

```python
# Fragment z recommender_movies.py / recommender_games.py
from sklearn.metrics.pairwise import cosine_similarity

# similarity to macierz (n_samples, n_samples)
# Każdy wiersz zawiera stopień podobieństwa do każdego innego elementu
similarity = cosine_similarity(tfidf_matrix)

# Pobieramy podobieństwo dla konkretnego filmu (po jego indeksie)
def get_scores(item_index, similarity_matrix):
    # Zwraca listę wag dla wszystkich tytułów względem wybranego
    return list(enumerate(similarity_matrix[item_index]))
```

## 3. Obsługa zapytań i Fuzzy Matching

W praktyce użytkownicy często wpisują tytuły z literówkami albo skrócone nazwy, na przykład „Wiedzmin” zamiast „Wiedźmin 3: Dziki Gon”. Żeby system był faktycznie użyteczny, dodano mechanizm **dopasowania rozmytego**.

### Jak to działa?
Do wyszukiwania tytułów w bazie używana jest biblioteka `difflib`. Porównuje ona wpisany tekst z nazwami w bazie i sprawdza, jak bardzo są do siebie podobne. Dzięki temu nawet niedokładnie wpisany tytuł może zostać poprawnie rozpoznany.

> [!INFO] Parametr Cutoff 
> W projekcie zastosowano próg `cutoff=0.6`. Oznacza to, że system uzna tytuł za pasujący, jeśli jest on co najmniej w 60% zgodny z wpisaną frazą. Zapobiega to zwracaniu zupełnie przypadkowych wyników przy krótkich zapytaniach.

```Python
from difflib import get_close_matches

# Szukanie najbliższego dopasowania w liście tytułów
matches = get_close_matches(user_input.lower(), titles_list, n=1, cutoff=0.6)
```
## 4. Ranking i selekcja rekomendacji

Ostatni etap to przekształcenie macierzy podobieństwa w listę najlepszych propozycji dla użytkownika – zwykle 10 albo 30 tytułów.

### Eliminacja elementu bazowego

Każdy film czy gra jest w pełni podobna do samego siebie (wynik 1.0). Pokazywanie użytkownikowi dokładnie tego, o który zapytał, nie ma sensu – psuje doświadczenie.

> [!IMPORTANT] Logika Slicingu 
> System zawsze sortuje wyniki malejąco, a następnie wykonuje operację `[1:top_n+1]`. Pominięcie indeksu `[0]` gwarantuje, że na liście znajdą się wyłącznie **nowe** propozycje.

W Pythonie wygląda to tak:

```Python
# Logika sortowania w recommender_games.py
def sort_scores(scores_list, top_n=30):
    # 1. Sortowanie od najwyższego podobieństwa (1.0 -> 0.0)
    sorted_list = sorted(scores_list, key=lambda x: x[1], reverse=True)
    
    # 2. Zwrócenie wyników z pominięciem pierwszego (bazowego) tytułu
    return sorted_list[1: top_n + 1]
```

### Cały przepływ danych

1. **Input:** Użytkownik wpisuje nazwę filmu lub gry.
    
2. **Fuzzy Match:** System dopasowuje tytuł w bazie CSV.
    
3. **Similarity:** Pobieramy wiersz z macierzy podobieństwa dla tego tytułu.
    
4. **Sort & Slice:** Wyniki są sortowane, a zapytanie użytkownika zostaje pominięte.
    
5. **Output:** Lista tytułów trafia do API TMDB/IGDB, żeby pobrać okładki i dane dodatkowe.
    

> [!TIP] Skalowalność 
> Macierz podobieństwa jest wyliczana tylko raz przy starcie serwera, więc generowanie rekomendacji zajmuje dosłownie milisekundy – interfejs działa bardzo szybko.