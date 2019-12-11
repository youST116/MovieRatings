from flask import Flask, current_app
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap

db=SQLAlchemy()

def create_app(config_class=Config):

    app = Flask(__name__)
    app.config.from_object(config_class)
    db.init_app(app)
    bootstrap = Bootstrap(app)

    #
    from app.main import bp as main_routes_bp
    app.register_blueprint(main_routes_bp)
    return app;
