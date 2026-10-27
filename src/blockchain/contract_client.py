
"""Client for the deployed SecureFileSharing smart contract."""

import json

from web3 import Web3
from src.config.settings import ROOT, BLOCKCHAIN_RPC_URL, CONTRACT_ADDRESS


def get_web3() -> Web3:
    w3 = Web3(Web3.HTTPProvider(BLOCKCHAIN_RPC_URL))

    if not w3.is_connected():
        raise ConnectionError(
            f"Cannot connect to blockchain at {BLOCKCHAIN_RPC_URL}"
        )

    return w3


def get_contract():
    if not CONTRACT_ADDRESS:
        raise RuntimeError("CONTRACT_ADDRESS is empty. Check .env.")

    artifact_path = (
        ROOT / "contracts" / "artifacts" / "SecureFileSharing.json"
    )

    if not artifact_path.exists():
        raise FileNotFoundError(
            f"Contract artifact not found: {artifact_path}"
        )

    artifact = json.loads(
        artifact_path.read_text(encoding="utf-8")
    )

    w3 = get_web3()
    address = Web3.to_checksum_address(CONTRACT_ADDRESS)

    if not w3.eth.get_code(address):
        raise RuntimeError("No contract code at CONTRACT_ADDRESS.")

    contract = w3.eth.contract(
        address=address,
        abi=artifact["abi"],
    )

    return w3, contract


def to_chain_file_id(file_id: str) -> bytes:
    """Map the application's UUID string to a deterministic bytes32 ID."""
    return Web3.keccak(text=file_id)


def _send_transaction(function, account_address: str) -> str:
    """Send a transaction from an unlocked local development account."""
    w3, _ = get_contract()
    account = Web3.to_checksum_address(account_address)

    if account not in [
        Web3.to_checksum_address(a)
        for a in w3.eth.accounts
    ]:
        raise ValueError(
            "Account is not available in Ganache. "
            "Use an unlocked Ganache development account."
        )

    tx_hash = function.transact({
        "from": account,
        "chainId": w3.eth.chain_id,
    })

    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

    if receipt["status"] != 1:
        raise RuntimeError("Blockchain transaction failed.")

    return tx_hash.hex()


def register_file_on_chain(
    file_id: str,
    encrypted_content: bytes,
    owner_address: str,
) -> str:
    """Register the file ID and encrypted-content hash on-chain."""
    _, contract = get_contract()

    chain_file_id = to_chain_file_id(file_id)
    content_hash = Web3.keccak(encrypted_content)

    tx_hash = _send_transaction(
        contract.functions.registerFile(
            chain_file_id,
            content_hash,
        ),
        owner_address,
    )

    return tx_hash


def request_access_on_chain(
    file_id: str,
    requester_address: str,
) -> str:
    """Submit an access request on-chain."""
    _, contract = get_contract()

    return _send_transaction(
        contract.functions.requestAccess(
            to_chain_file_id(file_id)
        ),
        requester_address,
    )


def decide_access_on_chain(
    file_id: str,
    requester_address: str,
    owner_address: str,
    approve: bool,
) -> str:
    """Approve or reject a pending request as the file owner."""
    _, contract = get_contract()

    requester = Web3.to_checksum_address(requester_address)

    return _send_transaction(
        contract.functions.decideAccess(
            to_chain_file_id(file_id),
            requester,
            approve,
        ),
        owner_address,
    )


def is_approved(
    file_id: str,
    requester_address: str,
) -> bool:
    """Check the authoritative on-chain approval status."""
    _, contract = get_contract()

    return contract.functions.isApproved(
        to_chain_file_id(file_id),
        Web3.to_checksum_address(requester_address),
    ).call()
