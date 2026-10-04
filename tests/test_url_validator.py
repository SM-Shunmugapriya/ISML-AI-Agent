from app.security.url_validator import validate_external_url


def test_valid_https_url():
    assert validate_external_url("https://example.com") is True


def test_valid_http_url():
    assert validate_external_url("http://example.com") is True


def test_blocks_localhost():
    assert validate_external_url("http://localhost:8000") is False


def test_blocks_loopback_ip():
    assert validate_external_url("http://127.0.0.1") is False


def test_blocks_private_ip():
    assert validate_external_url("http://192.168.1.10") is False


def test_blocks_metadata_endpoint():
    assert validate_external_url(
        "http://metadata.google.internal"
    ) is False


def test_blocks_unsupported_scheme():
    assert validate_external_url("file:///etc/passwd") is False


def test_blocks_empty_url():
    assert validate_external_url("") is False