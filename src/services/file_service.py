import uuid
from datetime import datetime, timezone

from cryptography.hazmat.primitives import serialization

from src.crypto.encryption import (
    generate_key,
    encrypt_bytes,
    decrypt_bytes,
)
from src.crypto.signatures import (
    generate_signing_keypair,
    sign_data,
    sha256_hex,
    verify_signature,
)
from src.crypto.key_sharing import (
    generate_rsa_keypair,
    unwrap_key_for_recipient,
)
from src.services.approved_key_sharing import wrap_key_if_approved
from src.storage.file_storage import save_encrypted, read_encrypted
from src.storage.metadata_store import read_collection, write_collection
from src.config.settings import KEYS_DIR
from src.blockchain.contract_client import (
    register_file_on_chain,
    request_access_on_chain,
    decide_access_on_chain,
    is_approved,
    get_contract,
    to_chain_file_id,
)
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

def _get_requester_rsa_keypair(requester_address: str):
    """Load or create an RSA key pair for this local demo requester."""
    address = requester_address.lower().removeprefix("0x")

    if not address or any(c not in "0123456789abcdef" for c in address):
        raise ValueError("Invalid requester address.")

    path = KEYS_DIR / f"requester_{address}.pem"

    if path.exists():
        private_key = serialization.load_pem_private_key(
            path.read_bytes(),
            password=None,
        )
        public_pem = private_key.public_key().public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )
        return private_key, public_pem

    private_key, public_pem = generate_rsa_keypair()

    path.write_bytes(
        private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )
    )

    return private_key, public_pem


def store_encrypted_file(
    filename: str,
    content: bytes, 
    owner_id: str,
    owner_address: str | None = None,
) -> dict:
    file_id = str(uuid.uuid4())
    key = generate_key()
    aad = file_id.encode()
    nonce, ciphertext = encrypt_bytes(content, key, aad)
    save_encrypted(file_id, ciphertext)
    digest = sha256_hex(content)
    signer = _get_private_key()
    signature = sign_data(signer, f"{file_id}:{digest}".encode())

    # Register on-chain when the caller supplies the owner's Ganache address.
    # The address must belong to the actual file owner.
    blockchain_tx_hash = None
    blockchain_registered = False

    if owner_address:
        blockchain_tx_hash = register_file_on_chain(
            file_id=file_id,
            encrypted_content=ciphertext,
            owner_address=owner_address,
        )
        blockchain_registered = True

    records = read_collection("files")
    record = {
    "file_id": file_id,
    "filename": filename,
    "owner_id": owner_id,
    "owner_address": owner_address,
    "file_hash": digest,
    "nonce_hex": nonce.hex(),
    "signature_hex": signature.hex(),
    "created_at": _now(),
    "status": "stored",
    "blockchain_registered": blockchain_registered,
    "blockchain_tx_hash": blockchain_tx_hash,
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

def create_request(
    file_id: str,
    requester_id: str,
    reason: str,
    requester_address: str | None = None,
) -> dict:
    if not reason.strip():
        raise ValueError("A reason is required.")

    file_record = next(
        (f for f in list_files() if f["file_id"] == file_id),
        None,
    )
    if not file_record:
        raise ValueError("File not found.")

    records = read_collection("requests")

    if any(
        r["file_id"] == file_id
        and r["requester_id"] == requester_id
        and r["status"] == "pending"
        for r in records
    ):
        raise ValueError("You already have a pending request for this file.")

    # Blockchain-registered files must submit requests on-chain.
    tx_hash = None
    if file_record.get("blockchain_registered"):
        if not requester_address:
            raise ValueError("Select a Ganache account to request access.")
        tx_hash = request_access_on_chain(file_id, requester_address)

    req = {
        "request_id": str(uuid.uuid4()),
        "file_id": file_id,
        "requester_id": requester_id,
        "requester_address": requester_address,
        "reason": reason.strip(),
        "status": "pending",
        "created_at": _now(),
        "blockchain_tx_hash": tx_hash,
        "blockchain_registered": bool(file_record.get("blockchain_registered")),
    }

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



def decide_request(
    request_id: str,
    approve: bool,
    owner_address: str | None = None,
) -> None:
    requests = read_collection("requests")
    files = {f["file_id"]: f for f in list_files()}

    req = next(
        (r for r in requests if r["request_id"] == request_id),
        None,
    )
    if req is None:
        raise ValueError("Request not found.")

    if req["status"] != "pending":
        raise ValueError("This request has already been decided.")

    file_record = files.get(req["file_id"])
    if file_record is None:
        raise ValueError("File not found.")

    tx_hash = None

    if file_record.get("blockchain_registered"):
        if not owner_address:
            raise ValueError("Select the file owner's Ganache account.")

        expected_owner = file_record.get("owner_address")
        if not expected_owner or owner_address.lower() != expected_owner.lower():
            raise PermissionError("Selected Ganache account does not own this file.")

        requester_address = req.get("requester_address")
        if not requester_address:
            raise ValueError("Requester blockchain address is missing.")

        tx_hash = decide_access_on_chain(
            req["file_id"],
            requester_address,
            owner_address,
            approve,
        )

    req["status"] = "approved" if approve else "rejected"
    req["decided_at"] = _now()

    if tx_hash:
        req["blockchain_decision_tx_hash"] = tx_hash

    write_collection("requests", requests)



def download_for_requester(
    file_id: str,
    requester_id: str,
    requester_address: str | None = None,
) -> tuple[str, bytes]:
    files = {f["file_id"]: f for f in list_files()}
    record = files.get(file_id)

    if not record:
        raise ValueError("File not found.")

    matching_request = next(
        (
            r for r in read_collection("requests")
            if r["file_id"] == file_id
            and r["requester_id"] == requester_id
        ),
        None,
    )

    if not matching_request:
        raise PermissionError("No access request found for this file.")

    if record.get("blockchain_registered"):
        if not requester_address:
            raise PermissionError("Select your Ganache account before downloading.")

        stored_address = matching_request.get("requester_address") or ""
        if stored_address.lower() != requester_address.lower():
            raise PermissionError("This request belongs to another blockchain account.")

        # Confirm approval directly against the smart contract.
        if not is_approved(file_id, requester_address):
            raise PermissionError("The smart contract has not approved this request.")

    elif matching_request.get("status") != "approved":
        raise PermissionError("An owner-approved access request is required.")

    keys = [
        k for k in read_collection("demo_keys")
        if k["file_id"] == file_id
    ]
    if not keys:
        raise RuntimeError("Demo key unavailable.")

    aes_key = bytes.fromhex(keys[0]["key_hex"])

    if record.get("blockchain_registered"):
        # Wrap the AES key for this requester only after contract approval.
        private_key, public_pem = _get_requester_rsa_keypair(requester_address)
        _, contract = get_contract()

        wrapped_key = wrap_key_if_approved(
            contract,
            to_chain_file_id(file_id),
            requester_address,
            aes_key,
            public_pem,
        )

        key = unwrap_key_for_recipient(wrapped_key, private_key)
    else:
        # Preserve local-only behavior for existing tests and legacy records.
        key = aes_key

    plaintext = decrypt_bytes(
        bytes.fromhex(record["nonce_hex"]),
        read_encrypted(file_id),
        key,
        file_id.encode(),
    )

    digest = sha256_hex(plaintext)
    if digest != record["file_hash"]:
        raise ValueError("Integrity verification failed: file hash does not match.")

    public_key_pem = _get_private_key().public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )

    try:
        signature = bytes.fromhex(record["signature_hex"])
        valid_signature = verify_signature(
            public_key_pem,
            f"{file_id}:{digest}".encode(),
            signature,
        )
    except (ValueError, TypeError):
        valid_signature = False

    if not valid_signature:
        raise ValueError("Digital signature verification failed.")

    return record["filename"], plaintext