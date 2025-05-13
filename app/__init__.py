from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from .config import Config
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
mail = Mail()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    mail.init_app(app)

    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'

    # Register blueprints
    from .blueprints.main import main
    from .blueprints.auth import auth
    from .blueprints.admin import admin
    from .blueprints.agent import agent
    from .blueprints.user import user
    from .blueprints.property import property
    from .blueprints.booking import booking
    from .blueprints.payment import payment

    app.register_blueprint(main)
    app.register_blueprint(auth)
    app.register_blueprint(admin)
    app.register_blueprint(agent)
    app.register_blueprint(user)
    app.register_blueprint(property)
    app.register_blueprint(booking)
    app.register_blueprint(payment)

    return app