"""
Tests for OpenClaw AI - validates core functionality and security
"""
import os
import pytest
from fastapi.testclient import TestClient

# Set JWT secret before importing the app
os.environ.setdefault("JWT_SECRET_KEY", "test_secret_key_that_is_long_enough_for_validation")


@pytest.fixture(scope="module")
def client():
    import main
    return TestClient(main.app)


# ── Security module tests ──────────────────────────────────────────────────────

class TestPasswordValidator:
    def test_rejects_short_password(self):
        from security import PasswordValidator
        valid, msg = PasswordValidator.validate("short")
        assert not valid
        assert "12 characters" in msg

    def test_rejects_missing_uppercase(self):
        from security import PasswordValidator
        valid, msg = PasswordValidator.validate("validpassword1!", require_uppercase=True)
        assert not valid
        assert "uppercase" in msg

    def test_rejects_missing_number(self):
        from security import PasswordValidator
        valid, msg = PasswordValidator.validate("ValidPassword!", require_numbers=True)
        assert not valid
        assert "number" in msg

    def test_rejects_missing_special(self):
        from security import PasswordValidator
        valid, msg = PasswordValidator.validate("ValidPassword1", require_special=True)
        assert not valid
        assert "special" in msg

    def test_accepts_strong_password(self):
        from security import PasswordValidator
        valid, msg = PasswordValidator.validate("ValidPassword1!")
        assert valid
        assert msg == ""


class TestInputSanitizer:
    def test_sanitize_filename_strips_path(self):
        from security import InputSanitizer
        result = InputSanitizer.sanitize_filename("../etc/passwd")
        assert "/" not in result
        assert result == "passwd"

    def test_sanitize_filename_no_hidden_files(self):
        from security import InputSanitizer
        result = InputSanitizer.sanitize_filename(".hidden")
        assert not result.startswith(".")

    def test_sanitize_filename_empty_becomes_unnamed(self):
        from security import InputSanitizer
        result = InputSanitizer.sanitize_filename("!!!")
        assert result == "unnamed_file"

    def test_validate_path_safe(self):
        from security import InputSanitizer
        assert InputSanitizer.validate_path("/tmp/test/file.txt", "/tmp/test") is True

    def test_validate_path_traversal_blocked(self):
        from security import InputSanitizer
        assert InputSanitizer.validate_path("/tmp/test/../../etc/passwd", "/tmp/test") is False

    def test_sanitize_input_removes_null_bytes(self):
        from security import InputSanitizer
        result = InputSanitizer.sanitize_input("hello\x00world")
        assert "\x00" not in result
        assert result == "helloworld"

    def test_sanitize_input_truncates_at_max_length(self):
        from security import InputSanitizer
        result = InputSanitizer.sanitize_input("a" * 200, max_length=100)
        assert len(result) == 100


class TestAuthManager:
    def test_hash_and_verify_password(self):
        from security import AuthManager
        auth = AuthManager(secret_key="a_secret_key_that_is_long_enough_32")
        hashed = auth.hash_password("TestPassword1!")
        assert auth.verify_password("TestPassword1!", hashed) is True
        assert auth.verify_password("WrongPassword", hashed) is False

    def test_create_and_verify_token(self):
        from security import AuthManager
        auth = AuthManager(secret_key="a_secret_key_that_is_long_enough_32")
        token = auth.create_access_token({"sub": "testuser"})
        payload = auth.verify_token(token)
        assert payload is not None
        assert payload["sub"] == "testuser"

    def test_verify_invalid_token_returns_none(self):
        from security import AuthManager
        auth = AuthManager(secret_key="a_secret_key_that_is_long_enough_32")
        result = auth.verify_token("not.a.valid.token")
        assert result is None


class TestEncryptionManager:
    def test_encrypt_decrypt_roundtrip(self):
        from security import EncryptionManager
        enc = EncryptionManager()
        data = "Hello, World!"
        encrypted = enc.encrypt(data)
        assert enc.decrypt_to_string(encrypted) == data

    def test_password_based_encrypt_decrypt(self):
        from security import EncryptionManager
        enc = EncryptionManager(password="mypassword")
        data = "Secret data"
        encrypted = enc.encrypt(data)
        assert enc.decrypt_to_string(encrypted) == data

    def test_encrypt_bytes_input(self):
        from security import EncryptionManager
        enc = EncryptionManager()
        data = b"Byte data"
        encrypted = enc.encrypt(data)
        assert enc.decrypt(encrypted) == data


class TestHelpers:
    def test_generate_secure_token_length(self):
        from security import generate_secure_token
        token = generate_secure_token(16)
        assert len(token) == 32  # hex encoding: 16 bytes = 32 chars

    def test_generate_secure_token_is_unique(self):
        from security import generate_secure_token
        assert generate_secure_token() != generate_secure_token()

    def test_hash_data_is_deterministic(self):
        from security import hash_data
        assert hash_data("test") == hash_data("test")

    def test_hash_data_is_hex_sha256(self):
        from security import hash_data
        result = hash_data("test")
        assert len(result) == 64
        assert all(c in "0123456789abcdef" for c in result)


# ── API endpoint tests ─────────────────────────────────────────────────────────

class TestHealthEndpoints:
    def test_root_returns_healthy(self, client):
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["secure_mode"] is True

    def test_health_check_returns_healthy(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

    def test_security_status_endpoint(self, client):
        response = client.get("/security/status")
        assert response.status_code == 200
        data = response.json()
        assert "secure_mode" in data
        assert "encryption_enabled" in data
        assert "rate_limiting_enabled" in data


class TestSecurityHeaders:
    def test_security_headers_present(self, client):
        response = client.get("/")
        assert response.headers.get("x-content-type-options") == "nosniff"
        assert response.headers.get("x-frame-options") == "DENY"
        assert response.headers.get("x-xss-protection") == "1; mode=block"
        assert "content-security-policy" in response.headers


class TestAuthEndpoints:
    def test_register_with_weak_password_is_rejected(self, client):
        response = client.post("/auth/register", json={
            "username": "testuser",
            "password": "short"
        })
        # 422: pydantic validation (min_length=12 on the model)
        assert response.status_code == 422

    def test_register_with_strong_password_succeeds(self, client):
        response = client.post("/auth/register", json={
            "username": "testuser",
            "password": "StrongPass1!"
        })
        assert response.status_code == 201
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_register_returns_valid_jwt(self, client):
        response = client.post("/auth/register", json={
            "username": "jwtuser",
            "password": "StrongPass1!"
        })
        assert response.status_code == 201
        token = response.json()["access_token"]
        # Token should be a JWT (three dot-separated parts)
        assert len(token.split(".")) == 3


class TestChatEndpoint:
    def test_chat_returns_response(self, client):
        response = client.post("/chat", json={"message": "Hello!"})
        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        assert "session_id" in data
        assert "timestamp" in data

    def test_chat_with_session_id_preserves_it(self, client):
        session_id = "my-test-session-id"
        response = client.post("/chat", json={
            "message": "Hello!",
            "session_id": session_id
        })
        assert response.status_code == 200
        assert response.json()["session_id"] == session_id

    def test_chat_rejects_empty_message(self, client):
        response = client.post("/chat", json={"message": ""})
        assert response.status_code == 422

    def test_chat_sanitizes_null_bytes(self, client):
        response = client.post("/chat", json={"message": "hello\x00world"})
        assert response.status_code == 200
        # The response should not echo back null bytes
        assert "\x00" not in response.json()["response"]
