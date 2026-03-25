
# Dokumentacja Architekturalna

## Widok komponentów
Aplikacja została zaprojektowana w architekturze **Monolithic with External Service Gateways**, tzn. aplikacja działa jako jeden spójny monolit, w którym cała logika znajduje się w jednym projekcie. Komunikacja z usługami zewnętrznymi odbywa się przez wydzielone bramy, które porządkują i izolują integracje z zewnętrznymi API.


```mermaid 
graph TD
	subgraph Frontend 
		A[HTML templates] --> B[Static CSS files]
	end 
	subgraph Backend_Flask 
		C[Flask routes main.py] --> D[User auth auth.py]
		C --> E[TF IDF recommender] 
	end 
	subgraph Data_Layer 
		F[(SQLite database)] 
		G[Dataset: movies.csv / games.csv] 
	end 
	subgraph External_Services 
		H[TMDB API] 
		I[IGDB API] 
		J[Google OAuth] 
	end 
	
	C <--> F 
	C <--> G 
	C <--> H 
	C <--> I 
	D <--> J
```

>[!NOTE] Model Monolityczny z Bramami 
>Aplikacja działa jako spójny monolit, co ułatwia zarządzanie stanem sesji i bazą danych. Komunikacja z usługami zewnętrznymi (TMDB, IGDB, Google) jest izolowana w folderze `algorytmy/`, co pozwala na łatwą wymianę dostawcy danych w przyszłości bez ingerencji w kod serwera Flask.