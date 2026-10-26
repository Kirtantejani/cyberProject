import hashlib
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.exceptions import InvalidSignature

def generate_signing_keypair():
    private_key = ec.generate_private_key(ec.SECP256R1())
    public_key_pem = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    return private_key, public_key_pem

def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def sign_data(private_key, data: bytes) -> bytes:
    return private_key.sign(data, ec.ECDSA(hashes.SHA256()))

def verify_signature(public_key_pem: bytes, data: bytes, signature: bytes) -> bool:
    public_key = serialization.load_pem_public_key(public_key_pem)
    try:
        public_key.verify(signature, data, ec.ECDSA(hashes.SHA256()))
        return True
    except InvalidSignature:
        return False
