import os
from pathlib import Path
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[2]
load_dotenv(ROOT / ".env")
DATA_DIR = ROOT / "data"
ENCRYPTED_DIR = DATA_DIR / "encrypted"
METADATA_DIR = DATA_DIR / "metadata"
DECRYPTED_DIR = DATA_DIR / "decrypted"
KEYS_DIR = ROOT / "keys"
for directory in (ENCRYPTED_DIR, METADATA_DIR, DECRYPTED_DIR, KEYS_DIR):
    directory.mkdir(parents=True, exist_ok=True)

BLOCKCHAIN_RPC_URL = os.getenv("BLOCKCHAIN_RPC_URL", "http://127.0.0.1:7545")
CONTRACT_ADDRESS = os.getenv("CONTRACT_ADDRESS", "")
CHAIN_ID = int(os.getenv("CHAIN_ID", "1337"))
