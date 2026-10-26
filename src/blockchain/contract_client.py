"""Optional Web3 client. Deploy the Solidity contract before using chain methods."""
from web3 import Web3
from src.config.settings import BLOCKCHAIN_RPC_URL, CONTRACT_ADDRESS

def connect():
    w3 = Web3(Web3.HTTPProvider(BLOCKCHAIN_RPC_URL, request_kwargs={"timeout": 3}))
    if not w3.is_connected():
        raise ConnectionError(f"Cannot connect to blockchain at {BLOCKCHAIN_RPC_URL}")
    return w3

def load_contract(abi: list):
    if not CONTRACT_ADDRESS:
        raise ValueError("Set CONTRACT_ADDRESS in your local .env after deploying the contract.")
    w3 = connect()
    return w3, w3.eth.contract(address=Web3.to_checksum_address(CONTRACT_ADDRESS), abi=abi)
