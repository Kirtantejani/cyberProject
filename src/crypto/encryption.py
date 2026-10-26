import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

KEY_BYTES = 32
NONCE_BYTES = 12

def generate_key() -> bytes:
    """Create a cryptographically secure 256-bit AES key."""
    return AESGCM.generate_key(bit_length=256)

def encrypt_bytes(plaintext: bytes, key: bytes, associated_data: bytes | None = None) -> tuple[bytes, bytes]:
    if len(key) != KEY_BYTES:
        raise ValueError("AES-256 key must be exactly 32 bytes.")
    nonce = os.urandom(NONCE_BYTES)
    return nonce, AESGCM(key).encrypt(nonce, plaintext, associated_data)

def decrypt_bytes(nonce: bytes, ciphertext: bytes, key: bytes, associated_data: bytes | None = None) -> bytes:
    if len(key) != KEY_BYTES:
        raise ValueError("AES-256 key must be exactly 32 bytes.")
    if len(nonce) != NONCE_BYTES:
        raise ValueError("AES-GCM nonce must be 12 bytes.")
    return AESGCM(key).decrypt(nonce, ciphertext, associated_data)
