from dotenv import load_dotenv
import os
from datetime import timedelta

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, '.env'))

from flask import Flask
from flask_login import LoginManager
from flask_cors import CORS

from db.database import init_db
from db.queries import get_user_by_id
from routes.movies import movies_bp
from auth.routes import auth_bp, bcrypt, init_oauth, User

app = Flask(__name__,
            template_folder=os.path.join(BASE_DIR, '..', 'frontend', 'templates'),
            static_folder=os.path.join(BASE_DIR, '..', 'frontend', 'static'))

app.secret_key = os.getenv('SECRET_KEY', 'fallback_secret')
app.config['REMEMBER_COOKIE_DURATION'] = timedelta(days=30)
app.config['REMEMBER_COOKIE_SECURE']   = False
app.config['REMEMBER_COOKIE_HTTPONLY'] = True

CORS(app)
bcrypt.init_app(app)
init_oauth(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Please log in to continue.'

@login_manager.user_loader
def load_user(user_id):
    data = get_user_by_id(int(user_id))
    return User(data) if data else None

app.register_blueprint(auth_bp)
app.register_blueprint(movies_bp)

if __name__ == '__main__':
    init_db()
    port = int(os.environ.get('PORT', 5000))
    print("🎬 Nexon running")
    app.run(debug=False, host='0.0.0.0', port=port)