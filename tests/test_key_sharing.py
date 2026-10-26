from src.crypto.encryption import generate_key
from src.crypto.key_sharing import generate_rsa_keypair, wrap_key_for_recipient, unwrap_key_for_recipient

def test_wrapped_key_round_trip():
    private, public = generate_rsa_keypair()
    key = generate_key()
    assert unwrap_key_for_recipient(wrap_key_for_recipient(key, public), private) == key
