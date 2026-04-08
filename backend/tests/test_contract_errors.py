def test_error_contract_requires_code_message(client):
    response = client.get("/api/v1/profiles")
    assert response.status_code == 403
    body = response.json()
    assert "code" in body
    assert "message" in body
