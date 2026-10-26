from datetime import datetime

import jwt

from app.models import Blacklist, db

from .conftest import APP_UUID


def test_post_blacklists_exito_201(client, auth_headers, valid_body):
    r = client.post("/blacklists", json=valid_body, headers=auth_headers)
    assert r.status_code == 201
    assert "cliente@correo.com" in r.json["msg"]
    assert r.json["data"]["email"] == "cliente@correo.com"
    assert r.json["data"]["app_uuid"] == APP_UUID
    assert r.json["data"]["blocked_reason"] == "spam"


def test_post_blacklists_guarda_request_ip_de_x_forwarded_for_201(client, auth_headers, valid_body):
    headers = {**auth_headers, "X-Forwarded-For": "1.2.3.4, 10.0.0.1"}
    r = client.post("/blacklists", json=valid_body, headers=headers)
    assert r.status_code == 201
    assert r.json["data"]["request_ip"] == "1.2.3.4"

    entry = Blacklist.query.filter_by(email="cliente@correo.com").one()
    assert entry.request_ip == "1.2.3.4"


def test_post_blacklists_sin_x_forwarded_for_usa_remote_addr_201(client, auth_headers, valid_body):
    r = client.post("/blacklists", json=valid_body, headers=auth_headers)
    assert r.status_code == 201
    assert r.json["data"]["request_ip"] == "127.0.0.1"


def test_post_blacklists_guarda_created_at_201(client, auth_headers, valid_body):
    r = client.post("/blacklists", json=valid_body, headers=auth_headers)
    assert r.status_code == 201
    assert datetime.fromisoformat(r.json["data"]["created_at"])

    db.session.expire_all()
    entry = Blacklist.query.filter_by(email="cliente@correo.com").one()
    assert isinstance(entry.created_at, datetime)


def test_post_blacklists_normaliza_email_a_minusculas_201(client, auth_headers):
    body = {"email": "Test@Mail.COM", "app_uuid": APP_UUID}
    r = client.post("/blacklists", json=body, headers=auth_headers)
    assert r.status_code == 201
    assert r.json["data"]["email"] == "test@mail.com"


def test_post_blacklists_sin_blocked_reason_201(client, auth_headers):
    body = {"email": "x@mail.com", "app_uuid": APP_UUID}
    r = client.post("/blacklists", json=body, headers=auth_headers)
    assert r.status_code == 201
    assert r.json["data"]["blocked_reason"] is None


def test_post_blacklists_uuid_invalido_400(client, auth_headers):
    body = {"email": "a@b.com", "app_uuid": "no-es-un-uuid"}
    r = client.post("/blacklists", json=body, headers=auth_headers)
    assert r.status_code == 400
    assert "app_uuid" in r.json["errors"]


def test_post_blacklists_email_invalido_400(client, auth_headers):
    body = {"email": "no-es-email", "app_uuid": APP_UUID}
    r = client.post("/blacklists", json=body, headers=auth_headers)
    assert r.status_code == 400
    assert "email" in r.json["errors"]


def test_post_blacklists_blocked_reason_mayor_a_255_400(client, auth_headers):
    body = {"email": "a@b.com", "app_uuid": APP_UUID, "blocked_reason": "x" * 256}
    r = client.post("/blacklists", json=body, headers=auth_headers)
    assert r.status_code == 400
    assert "blocked_reason" in r.json["errors"]


def test_post_blacklists_blocked_reason_de_255_es_valido_201(client, auth_headers):
    body = {"email": "a@b.com", "app_uuid": APP_UUID, "blocked_reason": "x" * 255}
    r = client.post("/blacklists", json=body, headers=auth_headers)
    assert r.status_code == 201


def test_post_blacklists_sin_campos_obligatorios_400(client, auth_headers):
    r = client.post("/blacklists", json={}, headers=auth_headers)
    assert r.status_code == 400
    assert {"email", "app_uuid"} <= set(r.json["errors"])


def test_post_blacklists_sin_token_401(client, valid_body):
    r = client.post("/blacklists", json=valid_body)
    assert r.status_code == 401


def test_post_blacklists_token_invalido_401(client, valid_body):
    headers = {"Authorization": "Bearer token-basura"}
    r = client.post("/blacklists", json=valid_body, headers=headers)
    assert r.status_code == 401


def test_post_blacklists_token_firmado_con_otra_clave_401(client, valid_body):
    ajeno = jwt.encode({"sub": "intruso", "type": "access"}, "otra-clave-distinta-de-32-bytes-o-mas!!", algorithm="HS256")
    r = client.post("/blacklists", json=valid_body, headers={"Authorization": f"Bearer {ajeno}"})
    assert r.status_code == 401


def test_post_blacklists_email_duplicado_409(client, auth_headers, valid_body):
    assert client.post("/blacklists", json=valid_body, headers=auth_headers).status_code == 201
    r = client.post("/blacklists", json=valid_body, headers=auth_headers)
    assert r.status_code == 409
    assert "cliente@correo.com" in r.json["msg"]


def test_post_blacklists_email_duplicado_distinto_case_409(client, auth_headers, valid_body):
    client.post("/blacklists", json=valid_body, headers=auth_headers)
    otro = {**valid_body, "email": "CLIENTE@correo.com"}
    r = client.post("/blacklists", json=otro, headers=auth_headers)
    assert r.status_code == 409
