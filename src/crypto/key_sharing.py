from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding

def generate_rsa_keypair():
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=3072)
    public_pem = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    return private_key, public_pem

def wrap_key_for_recipient(aes_key: bytes, recipient_public_pem: bytes) -> bytes:
    public_key = serialization.load_pem_public_key(recipient_public_pem)
    return public_key.encrypt(
        aes_key,
        padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None),
    )

def unwrap_key_for_recipient(wrapped_key: bytes, recipient_private_key) -> bytes:
    return recipient_private_key.decrypt(
        wrapped_key,
        padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None),
    )
