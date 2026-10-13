"""Genera el token Bearer estático (no expira).

Uso:  JWT_SECRET_KEY=<la misma clave que en Beanstalk> python generate_token.py
El token solo es válido mientras la app use esa misma JWT_SECRET_KEY.
"""
from flask_jwt_extended import create_access_token

from app import create_app

app = create_app()
with app.app_context():
    print(create_access_token(identity="blacklist-client"))
