from fastapi import HTTPException

from app.security.auth import require_api_key


def test_missing_api_key(monkeypatch):
    monkeypatch.delenv("ISML_API_KEY", raising=False)

    try:
        require_api_key(None)
        assert False
    except HTTPException as exc:
        assert exc.status_code == 500


def test_invalid_api_key(monkeypatch):
    monkeypatch.setenv("ISML_API_KEY", "correct-key")

    try:
        require_api_key("wrong-key")
        assert False
    except HTTPException as exc:
        assert exc.status_code == 401


def test_valid_api_key(monkeypatch):
    monkeypatch.setenv("ISML_API_KEY", "correct-key")

    assert require_api_key("correct-key") is True