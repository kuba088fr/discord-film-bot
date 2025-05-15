import os
import requests
import pytest
from unittest.mock import patch
from src.movie_api import _load_genres, get_random_movie

@pytest.fixture(autouse=True)
def dummy_key(monkeypatch):
    monkeypatch.setenv("TMDB_API_KEY", "fake_key")

def test_load_genres_caches(monkeypatch):
    fake = {"genres":[{"id":1,"name":"Drama"}]}
    monkeypatch.setattr(requests, "get", lambda *a, **k: type("",(),{"json":lambda s: fake})())
    m1 = _load_genres()
    m2 = _load_genres()
    assert m1 is m2  # cached

def test_get_random_movie_unknown_genre():
    with pytest.raises(Exception):
        get_random_movie("nonexistent")
