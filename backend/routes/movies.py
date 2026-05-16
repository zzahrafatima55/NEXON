from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from api.tmdb import search_movies, get_popular, get_trending, get_top_rated, get_trailer
from api.recommender import get_recommendation, get_similar
from db.queries import (add_to_watchlist, get_watchlist, remove_from_watchlist,
                        add_to_history, get_history, get_history_titles, is_in_watchlist)
import time

movies_bp = Blueprint('movies', __name__)

_cache = {"trending": [], "online": True, "checked": 0}


# ── Pages ─────────────────────────────────────────────────────
@movies_bp.route('/')
@login_required
def index():
    now = time.time()
    if now - _cache["checked"] > 300:
        try:
            data = get_trending()
            _cache["trending"] = data
            _cache["online"]   = True
        except Exception:
            _cache["online"] = False
        _cache["checked"] = now

    trending = _cache["trending"]
    featured = trending[0] if trending else None
    top10    = trending[:10]
    return render_template('index.html', trending=trending,
                           online=_cache["online"], featured=featured, top10=top10)


@movies_bp.route('/watchlist')
@login_required
def watchlist():
    return render_template('watchlist.html', movies=get_watchlist(current_user.id))


@movies_bp.route('/history')
@login_required
def history():
    movies  = get_history(current_user.id)
    ratings = [m['user_rating'] for m in movies if m.get('user_rating')]
    avg     = round(sum(ratings) / len(ratings), 1) if ratings else 0
    return render_template('history.html', movies=movies, avg_rating=avg)


# ── API ───────────────────────────────────────────────────────
@movies_bp.route('/api/search')
@login_required
def search():
    query = request.args.get('q', '').strip()
    if not query:
        return jsonify([])
    return jsonify(search_movies(query))


@movies_bp.route('/api/popular')
@login_required
def popular():
    return jsonify(get_popular())


@movies_bp.route('/api/trending')
@login_required
def trending():
    return jsonify(get_trending())


@movies_bp.route('/api/top_rated')
@login_required
def top_rated():
    return jsonify(get_top_rated())


@movies_bp.route('/api/recommend', methods=['POST'])
@login_required
def recommend():
    data    = request.json or {}
    mood    = data.get('mood', '').strip()
    if not mood:
        return jsonify({"error": "Mood is required"}), 400
    history = get_history_titles(current_user.id)
    result  = get_recommendation(mood, history)
    return jsonify({"result": result})


@movies_bp.route('/api/similar', methods=['POST'])
@login_required
def similar():
    data  = request.json or {}
    title = data.get('title', '').strip()
    if not title:
        return jsonify({"error": "Title is required"}), 400
    return jsonify({"result": get_similar(title)})


@movies_bp.route('/api/watchlist/add', methods=['POST'])
@login_required
def add_watchlist():
    d = request.json or {}
    add_to_watchlist(current_user.id, d['id'], d['title'], d.get('poster'),
                     d.get('rating'), d.get('year'), d.get('overview', ''))
    return jsonify({"success": True})


@movies_bp.route('/api/watchlist/remove', methods=['POST'])
@login_required
def remove_watchlist():
    d = request.json or {}
    remove_from_watchlist(current_user.id, d['id'])
    return jsonify({"success": True})


@movies_bp.route('/api/watchlist/check')
@login_required
def check_watchlist():
    movie_id = request.args.get('id', '')
    return jsonify({"in_watchlist": is_in_watchlist(current_user.id, movie_id)})


@movies_bp.route('/api/history/add', methods=['POST'])
@login_required
def add_history():
    d = request.json or {}
    add_to_history(current_user.id, d['id'], d['title'], d.get('poster'),
                   d.get('rating', 0), d.get('overview', ''))
    return jsonify({"success": True})

@movies_bp.route('/api/trailer/<movie_id>')
@login_required
def trailer(movie_id):
    url = get_trailer(movie_id)
    return jsonify({"url": url})
