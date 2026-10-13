import pytest
from flask_jwt_extended import create_access_token

from app import create_app
from app.models import db

UUID = "123e4567-e89b-12d3-a456-426614174000"


@pytest.fixture
def client():
    app = create_app({"TESTING": True, "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"})
    with app.app_context():
        db.create_all()
        token = create_access_token(identity="test")
        c = app.test_client()
        c.auth = {"Authorization": f"Bearer {token}"}
        yield c


def test_ping_sin_token(client):
    r = client.get("/ping")
    assert r.status_code == 200 and r.json["status"] == "ok"


def test_post_y_get(client):
    body = {"email": "Test@Mail.com", "app_uuid": UUID, "blocked_reason": "spam"}
    r = client.post("/blacklists", json=body, headers={**client.auth, "X-Forwarded-For": "1.2.3.4, 10.0.0.1"})
    assert r.status_code == 201
    assert r.json["data"]["request_ip"] == "1.2.3.4"

    r = client.get("/blacklists/test@mail.com", headers=client.auth)
    assert r.json == {"is_blacklisted": True, "blocked_reason": "spam"}


def test_get_no_bloqueado(client):
    r = client.get("/blacklists/libre@mail.com", headers=client.auth)
    assert r.json["is_blacklisted"] is False


def test_sin_token(client):
    assert client.post("/blacklists", json={}).status_code == 401
    assert client.get("/blacklists/a@b.com").status_code == 401


def test_token_invalido(client):
    r = client.get("/blacklists/a@b.com", headers={"Authorization": "Bearer basura"})
    assert r.status_code == 401


@pytest.mark.parametrize("body", [
    {"app_uuid": UUID},                                   # falta email
    {"email": "no-es-email", "app_uuid": UUID},           # email inválido
    {"email": "a@b.com"},                                 # falta uuid
    {"email": "a@b.com", "app_uuid": "123"},              # uuid inválido
    {"email": "a@b.com", "app_uuid": UUID, "blocked_reason": "x" * 256},  # motivo > 255
])
def test_validaciones(client, body):
    assert client.post("/blacklists", json=body, headers=client.auth).status_code == 400


def test_duplicado(client):
    body = {"email": "dup@mail.com", "app_uuid": UUID}
    client.post("/blacklists", json=body, headers=client.auth)
    assert client.post("/blacklists", json=body, headers=client.auth).status_code == 409


def test_motivo_opcional(client):
    r = client.post("/blacklists", json={"email": "x@mail.com", "app_uuid": UUID}, headers=client.auth)
    assert r.status_code == 201
