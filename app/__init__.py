from flask import Flask
from flask_jwt_extended import JWTManager
from flask_restful import Api

from .config import Config
from .models import db, ma
from .resources import BlacklistCheck, BlacklistCreate, Ping


def create_app(config_overrides=None):
    app = Flask(__name__)
    app.config.from_object(Config)
    if config_overrides:
        app.config.update(config_overrides)

    db.init_app(app)
    ma.init_app(app)
    jwt = JWTManager(app)

    # Respuestas JSON claras cuando falta o falla el token
    @jwt.unauthorized_loader
    def missing_token(reason):
        return {"msg": "Falta el token de autorización (Bearer)."}, 401

    @jwt.invalid_token_loader
    def invalid_token(reason):
        return {"msg": "Token de autorización inválido."}, 401

    api = Api(app)
    api.add_resource(BlacklistCreate, "/blacklists")
    api.add_resource(BlacklistCheck, "/blacklists/<string:email>")
    api.add_resource(Ping, "/", "/ping")

    with app.app_context():
        db.create_all()

    return app
