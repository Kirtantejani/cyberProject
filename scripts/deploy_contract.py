"""Compile and deploy SecureFileSharing.sol to a local EVM JSON-RPC node."""
import json
from pathlib import Path
from solcx import compile_standard
from web3 import Web3
from src.config.settings import ROOT, BLOCKCHAIN_RPC_URL, CHAIN_ID

SOLC_VERSION = "0.8.20"

def main():
    
    source_path = ROOT / "contracts" / "SecureFileSharing.sol"
    source = source_path.read_text(encoding="utf-8")
    compiled = compile_standard({
    "language": "Solidity",
    "sources": {
        "SecureFileSharing.sol": {"content": source}
    },
    "settings": {
        "evmVersion": "paris",
        "outputSelection": {
            "*": {
                "*": ["abi", "evm.bytecode"]
            }
       	 }
   	 }
	}, solc_binary="/opt/homebrew/bin/solc")
    contract_data = compiled["contracts"]["SecureFileSharing.sol"]["SecureFileSharing"]
    artifact = {"abi": contract_data["abi"], "bytecode": contract_data["evm"]["bytecode"]["object"]}
    artifact_path = ROOT / "contracts" / "artifacts" / "SecureFileSharing.json"
    artifact_path.write_text(json.dumps(artifact, indent=2), encoding="utf-8")

    w3 = Web3(Web3.HTTPProvider(BLOCKCHAIN_RPC_URL))
    if not w3.is_connected():
        raise SystemExit(f"Cannot connect to {BLOCKCHAIN_RPC_URL}. Start Ganache and check the RPC URL.")
    account = w3.eth.accounts[0]
    factory = w3.eth.contract(abi=artifact["abi"], bytecode=artifact["bytecode"])
    tx_hash = factory.constructor().transact({"from": account, "chainId": CHAIN_ID})
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    print("Contract deployed:", receipt.contractAddress)
    print("Add this to your local .env:")
    print(f"CONTRACT_ADDRESS={receipt.contractAddress}")

if __name__ == "__main__":
    main()
