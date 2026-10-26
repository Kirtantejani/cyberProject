import hashlib
import uuid
from datetime import datetime, timezone
from src.crypto.encryption import generate_key, encrypt_bytes, decrypt_bytes
from src.crypto.signatures import generate_signing_keypair, sign_data, sha256_hex
from src.storage.file_storage import save_encrypted, read_encrypted
from src.storage.metadata_store import read_collection, write_collection
from src.config.settings import KEYS_DIR

def _now():
    return datetime.now(timezone.utc).isoformat()

def _get_private_key():
    # Demo-only key persistence. Protect this directory and never commit its contents.
    from cryptography.hazmat.primitives import serialization
    path = KEYS_DIR / "demo_signing_key.pem"
    if path.exists():
        return serialization.load_pem_private_key(path.read_bytes(), password=None)
    private_key, _ = generate_signing_keypair()
    path.write_bytes(private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    ))
    return private_key

def store_encrypted_file(filename: str, content: bytes, owner_id: str) -> dict:
    file_id = str(uuid.uuid4())
    key = generate_key()
    aad = file_id.encode()
    nonce, ciphertext = encrypt_bytes(content, key, aad)
    save_encrypted(file_id, ciphertext)
    digest = sha256_hex(content)
    signer = _get_private_key()
    signature = sign_data(signer, f"{file_id}:{digest}".encode())
    records = read_collection("files")
    record = {
        "file_id": file_id, "filename": filename, "owner_id": owner_id,
        "file_hash": digest, "nonce_hex": nonce.hex(), "signature_hex": signature.hex(),
        "created_at": _now(), "status": "stored"
    }
    records.append(record)
    write_collection("files", records)
    keys = read_collection("demo_keys")
    keys.append({"file_id": file_id, "key_hex": key.hex(), "owner_id": owner_id})
    write_collection("demo_keys", keys)
    return record

def list_files(owner_id: str | None = None) -> list[dict]:
    records = read_collection("files")
    return [r for r in records if owner_id is None or r["owner_id"] == owner_id]

def create_request(file_id: str, requester_id: str, reason: str) -> dict:
    if not reason.strip():
        raise ValueError("A reason is required.")
    if not any(f["file_id"] == file_id for f in list_files()):
        raise ValueError("File not found.")
    records = read_collection("requests")
    if any(r["file_id"] == file_id and r["requester_id"] == requester_id and r["status"] == "pending" for r in records):
        raise ValueError("You already have a pending request for this file.")
    req = {"request_id": str(uuid.uuid4()), "file_id": file_id, "requester_id": requester_id,
           "reason": reason.strip(), "status": "pending", "created_at": _now()}
    records.append(req)
    write_collection("requests", records)
    return req

def list_requests(owner_id: str | None = None, requester_id: str | None = None) -> list[dict]:
    files = {f["file_id"]: f for f in list_files()}
    result = []
    for req in read_collection("requests"):
        file = files.get(req["file_id"])
        if not file:
            continue
        if owner_id is not None and file["owner_id"] != owner_id:
            continue
        if requester_id is not None and req["requester_id"] != requester_id:
            continue
        result.append(req)
    return result

def decide_request(request_id: str, approve: bool) -> None:
    requests = read_collection("requests")
    files = {f["file_id"]: f for f in list_files()}
    for req in requests:
        if req["request_id"] == request_id:
            req["status"] = "approved" if approve else "rejected"
            req["decided_at"] = _now()
            write_collection("requests", requests)
            return
    raise ValueError("Request not found.")

def download_for_requester(file_id: str, requester_id: str) -> tuple[str, bytes]:
    approved = any(r["file_id"] == file_id and r["requester_id"] == requester_id and r["status"] == "approved"
                   for r in read_collection("requests"))
    if not approved:
        raise PermissionError("An owner-approved access request is required.")
    files = {f["file_id"]: f for f in list_files()}
    record = files.get(file_id)
    if not record:
        raise ValueError("File not found.")
    keys = [k for k in read_collection("demo_keys") if k["file_id"] == file_id]
    if not keys:
        raise RuntimeError("Demo key unavailable.")
    key = bytes.fromhex(keys[0]["key_hex"])
    plaintext = decrypt_bytes(bytes.fromhex(record["nonce_hex"]), read_encrypted(file_id), key, file_id.encode())
    if hashlib.sha256(plaintext).hexdigest() != record["file_hash"]:
        raise ValueError("Integrity verification failed.")
    return record["filename"], plaintext
