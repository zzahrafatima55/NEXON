import requests

def is_online() -> bool:
    try:
        requests.get("https://api.themoviedb.org", timeout=1)
        return True
    except Exception:
        return False