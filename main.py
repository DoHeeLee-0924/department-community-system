from flask import Flask

from config import SECRET_KEY, CATEGORIES
from database import init_db
from utils import current_user
from pages.auth import auth_bp
from pages.posts import posts_bp
from pages.admin import admin_bp


def create_app():
    app = Flask(__name__)
    app.secret_key = SECRET_KEY

    app.register_blueprint(auth_bp)
    app.register_blueprint(posts_bp)
    app.register_blueprint(admin_bp)

    @app.context_processor
    def inject_common_data():
        return {
            "user": current_user(),
            "categories": CATEGORIES,
        }

    return app


app = create_app()

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
