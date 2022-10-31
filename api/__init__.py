from apiflask import APIFlask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from config import Config

db = SQLAlchemy()
migrate = Migrate()
cors = CORS()

def create_app(config=Config):
    """Application factory."""
    app = APIFlask(
        __name__,
        title="Blog API",
        version="1.0.0",
        docs_ui="elements"
    )
    app.config.from_object(config)

    db.init_app(app)
    migrate.init_app(app, db)
    if app.config["USE_CORS"]:
        cors.init_app(app)

    from . import models

    register_blueprints(app)

    return app 


def register_blueprints(app: APIFlask):
    """Register blueprints function."""
    from .resources.users import users 
    app.register_blueprint(users)

    from .resources.tokens import tokens
    app.register_blueprint(tokens)

    from .resources.posts import posts
    app.register_blueprint(posts)

    from .resources.follows import follows
    app.register_blueprint(follows)
    