from app.utils.signatures import generate_hmac_signature, constant_time_compare


def test_hmac_signature_generation():
    payload = '{"test": "data"}'
    secret = "secret_key"

    timestamp, signature = generate_hmac_signature(
        payload=payload,
        secret=secret,
    )

    assert isinstance(timestamp, int)
    assert isinstance(signature, str)
    assert len(signature) == 64  # SHA-256 hex length


def test_constant_time_compare():
    assert constant_time_compare("abc", "abc") is True
    assert constant_time_compare("abc", "abcd") is False
