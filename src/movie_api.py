import os, random, requests

API_KEY = os.getenv("TMDB_API_KEY")
BASE_URL = "https://api.themoviedb.org/3"

# Cache dla listy gatunków, żeby nie pobierać za każdym razem
_genre_map: dict[str, int] | None = None


def _load_genres() -> dict[str, int]:
    global _genre_map
    if _genre_map is None:
        resp = requests.get(
            f"{BASE_URL}/genre/movie/list",
            params={"api_key": API_KEY, "language": "en-US"},
        ).json()
        # zbuduj mapę: nazwa_lower → id
        _genre_map = {g["name"].lower(): g["id"] for g in resp.get("genres", [])}
        # TMDB używa pełnej nazwy, więc dodaj też zwykle skróty:
        if "science fiction" in _genre_map:
            _genre_map["sci-fi"] = _genre_map["science fiction"]
            _genre_map["scifi"] = _genre_map["science fiction"]
    return _genre_map


def get_random_movie(genre_name: str) -> str:
    genres = _load_genres()
    genre_id = genres.get(genre_name.lower())
    if not genre_id:
        return (
            f'Nie znam gatunku "{genre_name}". Spróbuj np. "comedy", "drama", "action".'
        )

    # Pobierz pierwszą stronę wyników z tym ID
    params = {
        "api_key": API_KEY,
        "with_genres": genre_id,
        "language": "en-US",
        "include_adult": False,
        "page": 1,
    }
    data = requests.get(f"{BASE_URL}/discover/movie", params=params).json()
    results = data.get("results", [])
    if not results:
        return "Brak wyników dla tego gatunku."

    film = random.choice(results)
    title = film.get("title", "Unknown")
    year = film.get("release_date", "")[:4]
    overview = film.get("overview", "")
    return f"{title} ({year}) – {overview}"
