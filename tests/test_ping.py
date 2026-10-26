def test_ping_sin_token_200(client):
    r = client.get("/ping")
    assert r.status_code == 200
    assert r.json == {"status": "ok", "version": "test-1.0.0"}


def test_raiz_alias_de_ping_200(client):
    r = client.get("/")
    assert r.status_code == 200
    assert r.json["status"] == "ok"
