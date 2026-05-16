from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from api.tmdb import search_movies, get_popular, get_trending, get_top_rated, get_trailer
from flask_login import login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt
from authlib.integrations.flask_client import OAuth
from db.queries import (create_user, get_user_by_email, get_user_by_id,
                        get_user_by_google_id, update_user_google,
                        get_user_stats, update_profile, update_avatar, update_password)
import os
import uuid

auth_bp = Blueprint('auth', __name__)
bcrypt  = Bcrypt()
oauth   = OAuth()

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), '..', '..', 'frontend', 'static', 'avatars')

def init_oauth(app):
    oauth.init_app(app)
    oauth.register(
        name='google',
        client_id=os.getenv('GOOGLE_CLIENT_ID'),
        client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
        client_kwargs={'scope': 'openid email profile'}
    )


# ── User class for Flask-Login ────────────────────────────────
class User:
    def __init__(self, data):
        self.id           = data['id']
        self.name         = data['name']
        self.email        = data['email']
        self.avatar       = data.get('avatar')
        self.bio          = data.get('bio', '')
        self.is_active    = True
        self.is_authenticated = True
        self.is_anonymous = False

    def get_id(self):
        return str(self.id)

    @property
    def initial(self):
        return self.name[0].upper() if self.name else '?'


# ── Auth Routes ───────────────────────────────────────────────
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email    = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        user_data = get_user_by_email(email)

        if not user_data:
            return render_template('login.html', error='No account found with that email.')
        if not user_data.get('password'):
            return render_template('login.html', error='This account uses Google Sign In.')
        if not bcrypt.check_password_hash(user_data['password'], password):
            return render_template('login.html', error='Incorrect password.')

        login_user(User(user_data), remember=True)
        return redirect(url_for('movies.index'))

    return render_template('login.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name     = request.form.get('name', '').strip()
        email    = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        if not name or not email or not password:
            return render_template('register.html', error='All fields are required.')
        if len(password) < 6:
            return render_template('register.html', error='Password must be at least 6 characters.')
        if get_user_by_email(email):
            return render_template('register.html', error='An account with this email already exists.')

        hashed    = bcrypt.generate_password_hash(password).decode('utf-8')
        user_data = create_user(name, email, password=hashed)

        if not user_data:
            return render_template('register.html', error='Something went wrong. Try again.')

        login_user(User(user_data), remember=True)
        return redirect(url_for('movies.index'))

    return render_template('register.html')


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


@auth_bp.route('/dashboard')
@login_required
def dashboard():
    user_data = get_user_by_id(current_user.id)
    stats     = get_user_stats(current_user.id)
    return render_template('dashboard.html', user=User(user_data), stats=stats)


# ── Profile Update Routes ─────────────────────────────────────
@auth_bp.route('/api/profile/update', methods=['POST'])
@login_required
def profile_update():
    data = request.json or {}
    name = data.get('name', '').strip()
    bio  = data.get('bio', '').strip()
    if not name:
        return jsonify({"error": "Name is required"}), 400
    update_profile(current_user.id, name, bio)
    return jsonify({"success": True, "name": name, "bio": bio})


@auth_bp.route('/api/profile/avatar', methods=['POST'])
@login_required
def profile_avatar():
    if 'avatar' not in request.files:
        return jsonify({"error": "No file"}), 400

    file = request.files['avatar']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    allowed = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    ext = file.filename.rsplit('.', 1)[-1].lower()
    if ext not in allowed:
        return jsonify({"error": "Invalid file type"}), 400

    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    filename = f"{current_user.id}_{uuid.uuid4().hex[:8]}.{ext}"
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    avatar_url = f"/static/avatars/{filename}"
    update_avatar(current_user.id, avatar_url)
    return jsonify({"success": True, "avatar": avatar_url})


@auth_bp.route('/api/profile/password', methods=['POST'])
@login_required
def profile_password():
    data         = request.json or {}
    current_pass = data.get('current_password', '')
    new_pass     = data.get('new_password', '')

    if len(new_pass) < 6:
        return jsonify({"error": "New password must be at least 6 characters"}), 400

    user_data = get_user_by_id(current_user.id)

    if not user_data.get('password'):
        return jsonify({"error": "This account uses Google Sign In — no password to change"}), 400

    if not bcrypt.check_password_hash(user_data['password'], current_pass):
        return jsonify({"error": "Current password is incorrect"}), 400

    hashed = bcrypt.generate_password_hash(new_pass).decode('utf-8')
    update_password(current_user.id, hashed)
    return jsonify({"success": True})


# ── Google OAuth ──────────────────────────────────────────────
@auth_bp.route('/auth/google')
def google_login():
    redirect_uri = url_for('auth.google_callback', _external=True)
    return oauth.google.authorize_redirect(redirect_uri)


@auth_bp.route('/auth/google/callback')
def google_callback():
    try:
        token     = oauth.google.authorize_access_token()
        user_info = token.get('userinfo')
        if not user_info:
            return redirect(url_for('auth.login'))

        google_id = user_info['sub']
        email     = user_info['email']
        name      = user_info.get('name', email.split('@')[0])
        avatar    = user_info.get('picture')

        user_data = get_user_by_google_id(google_id)
        if not user_data:
            user_data = get_user_by_email(email)
            if user_data:
                update_user_google(user_data['id'], google_id, avatar)
                user_data = get_user_by_email(email)
            else:
                user_data = create_user(name, email, google_id=google_id, avatar=avatar)

        if not user_data:
            return redirect(url_for('auth.login'))

        login_user(User(user_data), remember=True)
        return redirect(url_for('movies.index'))

    except Exception as e:
        print(f"Google auth error: {e}")
        return redirect(url_for('auth.login'))