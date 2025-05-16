import os
import random
import requests

API_KEY  = os.getenv("TMDB_API_KEY")
BASE_URL = "https://api.themoviedb.org/3"

def _load_genres() -> dict[str, int]:
    """
    Fetch the list of genres from TMDB once and cache it
    in a function attribute to survive patch.object().
    """
    # Initialize cache attribute on first call
    if not hasattr(_load_genres, "_cache") or _load_genres._cache is None:
        resp = requests.get(
            f"{BASE_URL}/genre/movie/list",
            params={"api_key": API_KEY, "language": "en-US"},
        ).json()
        # build lowercase-name → id map
        mapping = {g["name"].lower(): g["id"] for g in resp.get("genres", [])}
        # add common sci-fi shortcuts
        if "science fiction" in mapping:
            mapping["sci-fi"] = mapping["science fiction"]
            mapping["scifi"]  = mapping["science fiction"]
        _load_genres._cache = mapping
    return _load_genres._cache  # type: ignore[attr-defined]

def get_random_movie(genre_name: str) -> str:
    """
    Pick a random movie from a given genre via TMDB.
    """
    genres   = _load_genres()
    genre_id = genres.get(genre_name.lower())
    if not genre_id:
        return (
            f'I don’t recognize the genre "{genre_name}". '
            f'Try something like "comedy", "drama", or "action".'
        )

    params = {
        "api_key": API_KEY,
        "with_genres": genre_id,
        "language": "en-US",
        "include_adult": False,
        "page": 1,
    }
    data    = requests.get(f"{BASE_URL}/discover/movie", params=params).json()
    results = data.get("results", [])
    if not results:
        return f'No results found for genre "{genre_name}".'

    film     = random.choice(results)
    title    = film.get("title", "Unknown")
    year     = film.get("release_date", "")[:4]
    overview = film.get("overview", "")
    return f"{title} ({year}) – {overview}"
