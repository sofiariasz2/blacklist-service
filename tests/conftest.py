import os

# Debe ir ANTES de importar la app: app/config.py lee el entorno al importarse.
# Así las pruebas corren sin DATABASE_URL ni RDS_* (por ejemplo en CodeBuild).
for var in ("DATABASE_URL", "RDS_HOSTNAME", "RDS_USERNAME", "RDS_PASSWORD", "RDS_PORT", "RDS_DB_NAME"):
    os.environ.pop(var, None)
os.environ["JWT_SECRET_KEY"] = "clave-de-pruebas-con-longitud-suficiente-para-hs256"

import pytest
from flask_jwt_extended import create_access_token

from app import create_app
from app.models import db

APP_UUID = "123e4567-e89b-12d3-a456-426614174000"


@pytest.fixture
def app():
    app = create_app(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            "JWT_SECRET_KEY": os.environ["JWT_SECRET_KEY"],
            "APP_VERSION": "test-1.0.0",
        }
    )
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()
        db.engine.dispose()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def auth_headers(app):
    """Token JWT real, firmado con la clave de la app."""
    token = create_access_token(identity="test")
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def valid_body():
    return {"email": "cliente@correo.com", "app_uuid": APP_UUID, "blocked_reason": "spam"}
