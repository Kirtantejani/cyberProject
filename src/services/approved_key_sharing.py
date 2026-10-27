"""RSA-OAEP key sharing gated by blockchain access approval."""

from web3 import Web3

from src.crypto.key_sharing import wrap_key_for_recipient


def wrap_key_if_approved(
    contract,
    file_id: bytes,
    requester_address: str,
    aes_key: bytes,
    recipient_public_pem: bytes,
) -> bytes:
    """Wrap an AES key only if the contract approves this requester."""

    if len(file_id) != 32:
        raise ValueError("file_id must be exactly 32 bytes")

    requester = Web3.to_checksum_address(requester_address)

    approved = contract.functions.isApproved(
        file_id, requester
    ).call()

    if not approved:
        raise PermissionError(
            "Access denied: recipient is not approved for this file."
        )

    return wrap_key_for_recipient(aes_key, recipient_public_pem)
