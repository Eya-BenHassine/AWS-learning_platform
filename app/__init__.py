from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
from config import Config
import markdown
from markupsafe import Markup  # <-- CHANGED: Import from markupsafe instead of flask

db = SQLAlchemy()
login_manager = LoginManager()
bcrypt = Bcrypt()
migrate = Migrate()

login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    migrate.init_app(app, db)
    
    # Register markdown filter
    @app.template_filter('markdown')
    def markdown_filter(text):
        if not text:
            return ''
        # Convert markdown to HTML with extensions
        extensions = ['extra', 'fenced_code', 'tables', 'nl2br', 'sane_lists']
        html = markdown.markdown(text, extensions=extensions)
        return Markup(html)
    
    # Register blueprints
    from app.auth import bp as auth_bp
    from app.routes import bp as main_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    
    # Import models so Alembic migrations can detect them
    from app import models
    
    return app