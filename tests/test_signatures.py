from src.crypto.signatures import generate_signing_keypair, sign_data, verify_signature, sha256_hex

def test_signature_valid():
    private, public = generate_signing_keypair()
    data = b"file-id:hash"
    assert verify_signature(public, data, sign_data(private, data))

def test_signature_rejects_changed_data():
    private, public = generate_signing_keypair()
    signature = sign_data(private, b"original")
    assert not verify_signature(public, b"changed", signature)

def test_sha256_deterministic():
    assert sha256_hex(b"abc") == sha256_hex(b"abc")
