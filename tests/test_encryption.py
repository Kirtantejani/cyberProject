import pytest
from cryptography.exceptions import InvalidTag
from src.crypto.encryption import generate_key, encrypt_bytes, decrypt_bytes

def test_round_trip():
    key = generate_key()
    nonce, ciphertext = encrypt_bytes(b"secret", key)
    assert decrypt_bytes(nonce, ciphertext, key) == b"secret"

def test_wrong_key_rejected():
    key = generate_key()
    nonce, ciphertext = encrypt_bytes(b"secret", key)
    with pytest.raises(InvalidTag):
        decrypt_bytes(nonce, ciphertext, generate_key())

def test_tampering_rejected():
    key = generate_key()
    nonce, ciphertext = encrypt_bytes(b"secret", key)
    corrupted = ciphertext[:-1] + bytes([ciphertext[-1] ^ 1])
    with pytest.raises(InvalidTag):
        decrypt_bytes(nonce, corrupted, key)

def test_aad_mismatch_rejected():
    key = generate_key()
    nonce, ciphertext = encrypt_bytes(b"secret", key, b"id-1")
    with pytest.raises(InvalidTag):
        decrypt_bytes(nonce, ciphertext, key, b"id-2")
