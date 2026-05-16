from db.database import get_conn


# ── Users ─────────────────────────────────────────────────────
def create_user(name, email, password=None, google_id=None, avatar=None):
    conn = get_conn()
    try:
        conn.execute(
            "INSERT INTO users (name, email, password, google_id, avatar) VALUES (?, ?, ?, ?, ?)",
            (name, email, password, google_id, avatar)
        )
        conn.commit()
        return get_user_by_email(email)
    except Exception as e:
        print(f"Create user error: {e}")
        return None
    finally:
        conn.close()

def get_user_by_email(email):
    conn = get_conn()
    row = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
    conn.close()
    return dict(row) if row else None

def get_user_by_id(user_id):
    conn = get_conn()
    row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    conn.close()
    return dict(row) if row else None

def get_user_by_google_id(google_id):
    conn = get_conn()
    row = conn.execute("SELECT * FROM users WHERE google_id = ?", (google_id,)).fetchone()
    conn.close()
    return dict(row) if row else None

def update_user_google(user_id, google_id, avatar):
    conn = get_conn()
    conn.execute(
        "UPDATE users SET google_id = ?, avatar = ? WHERE id = ?",
        (google_id, avatar, user_id)
    )
    conn.commit()
    conn.close()

def update_profile(user_id, name, bio):
    conn = get_conn()
    conn.execute(
        "UPDATE users SET name = ?, bio = ? WHERE id = ?",
        (name, bio, user_id)
    )
    conn.commit()
    conn.close()

def update_avatar(user_id, avatar_path):
    conn = get_conn()
    conn.execute(
        "UPDATE users SET avatar = ? WHERE id = ?",
        (avatar_path, user_id)
    )
    conn.commit()
    conn.close()

def update_password(user_id, hashed_password):
    conn = get_conn()
    conn.execute(
        "UPDATE users SET password = ? WHERE id = ?",
        (hashed_password, user_id)
    )
    conn.commit()
    conn.close()


# ── Watchlist ─────────────────────────────────────────────────
def add_to_watchlist(user_id, movie_id, title, poster, rating, year, overview=""):
    conn = get_conn()
    try:
        conn.execute(
            """INSERT OR IGNORE INTO watchlist
               (user_id, movie_id, title, poster, rating, year, overview)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (user_id, movie_id, title, poster, rating, year, overview)
        )
        conn.commit()
        return True
    except Exception as e:
        print(f"DB error: {e}")
        return False
    finally:
        conn.close()

def get_watchlist(user_id):
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM watchlist WHERE user_id = ? ORDER BY added_at DESC", (user_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def remove_from_watchlist(user_id, movie_id):
    conn = get_conn()
    conn.execute(
        "DELETE FROM watchlist WHERE user_id = ? AND movie_id = ?", (user_id, movie_id)
    )
    conn.commit()
    conn.close()

def is_in_watchlist(user_id, movie_id):
    conn = get_conn()
    row = conn.execute(
        "SELECT 1 FROM watchlist WHERE user_id = ? AND movie_id = ?", (user_id, movie_id)
    ).fetchone()
    conn.close()
    return row is not None


# ── Watch History ─────────────────────────────────────────────
def add_to_history(user_id, movie_id, title, poster, user_rating, overview=""):
    conn = get_conn()
    conn.execute(
        """INSERT INTO watch_history
           (user_id, movie_id, title, poster, user_rating, overview)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (user_id, movie_id, title, poster, user_rating, overview)
    )
    conn.commit()
    conn.close()

def get_history(user_id):
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM watch_history WHERE user_id = ? ORDER BY watched_at DESC", (user_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_history_titles(user_id):
    conn = get_conn()
    rows = conn.execute(
        "SELECT DISTINCT title FROM watch_history WHERE user_id = ?", (user_id,)
    ).fetchall()
    conn.close()
    return [r[0] for r in rows]

def get_user_stats(user_id):
    conn = get_conn()
    watchlist_count = conn.execute(
        "SELECT COUNT(*) FROM watchlist WHERE user_id = ?", (user_id,)
    ).fetchone()[0]
    history_count = conn.execute(
        "SELECT COUNT(*) FROM watch_history WHERE user_id = ?", (user_id,)
    ).fetchone()[0]
    avg_rating = conn.execute(
        "SELECT AVG(user_rating) FROM watch_history WHERE user_id = ? AND user_rating > 0", (user_id,)
    ).fetchone()[0]
    conn.close()
    return {
        "watchlist":  watchlist_count,
        "watched":    history_count,
        "avg_rating": round(avg_rating, 1) if avg_rating else 0
    }