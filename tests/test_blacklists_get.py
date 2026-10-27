from .conftest import APP_UUID


def test_get_blacklists_email_bloqueado_200(client, auth_headers):
    client.post(
        "/blacklists",
        json={"email": "malo@mail.com", "app_uuid": APP_UUID, "blocked_reason": "spam"},
        headers=auth_headers,
    )
    r = client.get("/blacklists/malo@mail.com", headers=auth_headers)
    assert r.status_code == 200
    assert r.json == {"is_blacklisted": True, "blocked_reason": "spam"}


def test_get_blacklists_email_no_bloqueado_200(client, auth_headers):
    r = client.get("/blacklists/libre@mail.com", headers=auth_headers)
    assert r.status_code == 200
    assert r.json == {"is_blacklisted": False, "blocked_reason": None}


def test_get_blacklists_bloqueado_sin_motivo_200(client, auth_headers):
    client.post("/blacklists", json={"email": "sm@mail.com", "app_uuid": APP_UUID}, headers=auth_headers)
    r = client.get("/blacklists/sm@mail.com", headers=auth_headers)
    assert r.status_code == 200
    assert r.json == {"is_blacklisted": True, "blocked_reason": None}


def test_get_blacklists_busqueda_ignora_mayusculas_200(client, auth_headers):
    client.post("/blacklists", json={"email": "caso@mail.com", "app_uuid": APP_UUID}, headers=auth_headers)
    r = client.get("/blacklists/CASO@Mail.com", headers=auth_headers)
    assert r.status_code == 200
    assert r.json["is_blacklisted"] is True


def test_get_blacklists_sin_token_401(client):
    r = client.get("/blacklists/a@b.com")
    assert r.status_code == 401


def test_get_blacklists_token_invalido_401(client):
    r = client.get("/blacklists/a@b.com", headers={"Authorization": "Bearer basura"})
    assert r.status_code == 401
