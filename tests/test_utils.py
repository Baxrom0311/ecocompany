"""
Test Utils — hashing, pagination, sanitize
"""
from app.utils.hashing import hash_password, verify_password
from app.utils.sanitize import sanitize_html
from app.services.auth_service import create_access_token, verify_token


class TestHashing:
    def test_hash_and_verify(self):
        hashed = hash_password("MyPassword123!")
        assert hashed != "MyPassword123!"
        assert verify_password("MyPassword123!", hashed) is True

    def test_wrong_password(self):
        hashed = hash_password("Correct123!")
        assert verify_password("Wrong123!", hashed) is False

    def test_empty_password(self):
        hashed = hash_password("")
        assert verify_password("", hashed) is True
        assert verify_password("notempty", hashed) is False

    def test_unicode_password(self):
        hashed = hash_password("Парoль123!")
        assert verify_password("Парoль123!", hashed) is True

    def test_different_hashes(self):
        h1 = hash_password("Same123!")
        h2 = hash_password("Same123!")
        assert h1 != h2  # bcrypt har safar unique salt ishlatadi


class TestSanitize:
    def test_strip_script(self):
        assert sanitize_html("<script>alert('xss')</script>") == "alert('xss')"

    def test_strip_html_tags(self):
        assert sanitize_html("<b>Bold</b> <i>italic</i>") == "Bold italic"

    def test_strip_iframe(self):
        assert sanitize_html('<iframe src="evil.com"></iframe>') == ""

    def test_plain_text_unchanged(self):
        text = "Oddiy matn, hech narsa o'zgarmaydi"
        assert sanitize_html(text) == text

    def test_empty_string(self):
        assert sanitize_html("") == ""

    def test_nested_tags(self):
        result = sanitize_html("<div><p>Text <script>x</script></p></div>")
        assert "<script>" not in result
        assert "Text" in result


class TestJWT:
    def test_create_and_verify(self):
        token = create_access_token({"sub": "test-user-id"})
        payload = verify_token(token)
        assert payload is not None
        assert payload["sub"] == "test-user-id"

    def test_invalid_token(self):
        result = verify_token("invalid.token.here")
        assert result is None

    def test_empty_token(self):
        result = verify_token("")
        assert result is None

    def test_payload_fields(self):
        token = create_access_token({"sub": "123", "role": "admin"})
        payload = verify_token(token)
        assert payload["sub"] == "123"
        assert "exp" in payload
