import json
import uuid
from pathlib import Path

from web3 import Web3
from src.config.settings import (
    ROOT,
    BLOCKCHAIN_RPC_URL,
    CONTRACT_ADDRESS,
)

def main():
    if not CONTRACT_ADDRESS:
        raise RuntimeError(
            "CONTRACT_ADDRESS is empty. Check your local .env file."
        )

    w3 = Web3(Web3.HTTPProvider(BLOCKCHAIN_RPC_URL))
    if not w3.is_connected():
        raise RuntimeError("Cannot connect to Ganache.")

    artifact_path = ROOT / "contracts" / "artifacts" / "SecureFileSharing.json"
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))

    contract = w3.eth.contract(
        address=Web3.to_checksum_address(CONTRACT_ADDRESS),
        abi=artifact["abi"],
    )

    code = w3.eth.get_code(contract.address)
    if not code:
        raise RuntimeError("No contract code found at this address.")

    accounts = w3.eth.accounts
    if len(accounts) < 2:
        raise RuntimeError("Ganache needs at least two accounts.")

    owner = accounts[0]
    requester = accounts[1]

    # Generate a unique demo file ID so the test can be rerun.
    file_id = Web3.keccak(text=f"demo-file-{uuid.uuid4()}")
    content_hash = Web3.keccak(text="demo-encrypted-file-hash")

    print("Connected to Ganache:", w3.is_connected())
    print("Contract:", contract.address)
    print("Owner:", owner)
    print("Requester:", requester)

    # 1. Owner registers a demo file.
    tx = contract.functions.registerFile(
        file_id, content_hash
    ).transact({"from": owner})
    w3.eth.wait_for_transaction_receipt(tx)
    print("PASS: File registered")

    # 2. Requester requests access.
    tx = contract.functions.requestAccess(
        file_id
    ).transact({"from": requester})
    w3.eth.wait_for_transaction_receipt(tx)
    print("PASS: Access requested")

    # 3. Access should not yet be approved.
    approved = contract.functions.isApproved(
        file_id, requester
    ).call()
    assert approved is False, "Access should initially be unapproved"
    print("PASS: Access is pending, not approved")

    # 4. Owner approves the requester.
    tx = contract.functions.decideAccess(
        file_id, requester, True
    ).transact({"from": owner})
    w3.eth.wait_for_transaction_receipt(tx)
    print("PASS: Owner approved access")

    # 5. Verify the final decision.
    approved = contract.functions.isApproved(
        file_id, requester
    ).call()
    assert approved is True, "Access should now be approved"
    print("PASS: isApproved returned True")
    print("\nALL ACCESS-CONTROL TESTS PASSED")

if __name__ == "__main__":
    main()
