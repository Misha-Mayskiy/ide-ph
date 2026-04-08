from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from jose import jwt

from app.main import create_app


@pytest.fixture()
def client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    db_path = tmp_path / "test.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite+aiosqlite:///{db_path.as_posix()}")
    monkeypatch.setenv("JWT_SECRET", "test-secret")
    monkeypatch.setenv("AUTO_CREATE_TABLES", "true")
    monkeypatch.setenv("OPENAI_API_KEY", "")

    app = create_app()
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture()
def auth_header() -> dict[str, str]:
    token = jwt.encode({"sub": "user-1"}, "test-secret", algorithm="HS256")
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture()
def auth_header_other_user() -> dict[str, str]:
    token = jwt.encode({"sub": "user-2"}, "test-secret", algorithm="HS256")
    return {"Authorization": f"Bearer {token}"}
