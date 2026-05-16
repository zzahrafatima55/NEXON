import requests
import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

TOKEN    = os.getenv("TMDB_API_KEY")
IMG_BASE      = "https://image.tmdb.org/t/p/original"
BACKDROP_BASE = "https://image.tmdb.org/t/p/original"
HEADERS  = {"Authorization": f"Bearer {TOKEN}"}
BASE = "https://api.themoviedb.org/3"


def _format(results):
    movies = []
    for m in results:
        movies.append({
            "id":       str(m.get("id")),
            "title":    m.get("title", "Unknown"),
            "overview": m.get("overview", ""),
            "poster":   IMG_BASE + m["poster_path"] if m.get("poster_path") else None,
            "rating":   round(m.get("vote_average", 0), 1),
            "year":     m.get("release_date", "")[:4],
        })
    return movies


def search_movies(query):
    r = requests.get(f"{BASE}/search/movie", headers=HEADERS,
                     params={"query": query}, timeout=5)
    return _format(r.json().get("results", [])[:12])


def get_trending():
    r = requests.get(f"{BASE}/trending/movie/week", headers=HEADERS, timeout=5)
    return _format(r.json().get("results", [])[:14])

def get_popular():
    r = requests.get(f"{BASE}/movie/popular", headers=HEADERS, timeout=5)
    return _format(r.json().get("results", [])[:14])

def get_top_rated():
    r = requests.get(f"{BASE}/movie/top_rated", headers=HEADERS, timeout=5)
    return _format(r.json().get("results", [])[:14])
def get_trailer(movie_id):
    r = requests.get(f"{BASE}/movie/{movie_id}/videos", headers=HEADERS, timeout=5)
    results = r.json().get("results", [])
    # find official YouTube trailer
    for v in results:
        if v.get("type") == "Trailer" and v.get("site") == "YouTube":
            return f"https://www.youtube.com/embed/{v['key']}?autoplay=1"
    # fallback to any teaser
    for v in results:
        if v.get("site") == "YouTube":
            return f"https://www.youtube.com/embed/{v['key']}?autoplay=1"
    return None
def _format(results):
    movies = []
    for m in results:
        movies.append({
            "id":       str(m.get("id")),
            "title":    m.get("title", "Unknown"),
            "overview": m.get("overview", ""),
            "poster":   IMG_BASE + m["poster_path"] if m.get("poster_path") else None,
            "backdrop": BACKDROP_BASE + m["backdrop_path"] if m.get("backdrop_path") else None,
            "rating":   round(m.get("vote_average", 0), 1),
            "year":     m.get("release_date", "")[:4],
        })
    return movies