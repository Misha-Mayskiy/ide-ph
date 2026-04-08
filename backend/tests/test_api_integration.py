import time


def _wait_generation_done(client, generation_id: str, headers: dict[str, str], timeout: float = 8.0):
    started = time.time()
    while time.time() - started < timeout:
        response = client.get(f"/api/v1/generations/{generation_id}", headers=headers)
        assert response.status_code == 200
        body = response.json()
        if body["status"] in {"succeeded", "failed"}:
            return body
        time.sleep(0.2)
    raise AssertionError("generation job did not complete in time")


def test_generation_lifecycle_and_contract(client, auth_header):
    create_resp = client.post(
        "/api/v1/generations",
        headers=auth_header,
        json={"prompt": "dark split layout with vim", "locale": "ru"},
    )
    assert create_resp.status_code == 201

    body = create_resp.json()
    assert set(body.keys()) == {"generationId", "status", "pollUrl"}
    assert body["status"] == "queued"

    result = _wait_generation_done(client, body["generationId"], auth_header)
    assert set(result.keys()) == {"status", "progress", "ideConfig", "error"}
    assert result["status"] == "succeeded"
    assert result["ideConfig"]["theme"]["preset"] == "dark"


def test_profile_crud_and_user_isolation(client, auth_header, auth_header_other_user):
    ide_config = {
        "version": "1.0",
        "theme": {"preset": "light"},
        "layout": {"preset": "classic", "ratios": {"left": 0.2, "center": 0.6, "right": 0.2}},
        "panels": [
            {"id": "explorer", "position": "left", "visible": True, "size": 280},
            {"id": "terminal", "position": "bottom", "visible": True, "size": 260},
            {"id": "tabs", "position": "top", "visible": True, "size": 120},
            {"id": "statusBar", "position": "bottom", "visible": True, "size": 40},
        ],
        "editor": {"fontSize": 14},
        "keymap": {"preset": "vscode", "overrides": {}},
    }

    create_resp = client.post(
        "/api/v1/profiles",
        headers=auth_header,
        json={"name": "My profile", "ideConfig": ide_config},
    )
    assert create_resp.status_code == 201
    profile_id = create_resp.json()["id"]

    list_resp = client.get("/api/v1/profiles", headers=auth_header)
    assert list_resp.status_code == 200
    assert len(list_resp.json()["items"]) == 1

    forbidden_resp = client.get(f"/api/v1/profiles/{profile_id}", headers=auth_header_other_user)
    assert forbidden_resp.status_code == 404

    update_resp = client.put(
        f"/api/v1/profiles/{profile_id}",
        headers=auth_header,
        json={"name": "Updated profile"},
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["name"] == "Updated profile"

    delete_resp = client.delete(f"/api/v1/profiles/{profile_id}", headers=auth_header)
    assert delete_resp.status_code == 204
