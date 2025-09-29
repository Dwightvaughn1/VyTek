# resonance_live_watcher.py
# Live watcher for $TRY token with Memnora Resonance Chain integration

import os
import json
import time
import hmac
import hashlib
from base64 import urlsafe_b64encode
from web3 import Web3
from eth_account import Account
from cryptography.fernet import Fernet

# ---------------------------
# CONFIGURATION
# ---------------------------
INFURA_URL = "https://mainnet.infura.io/v3/YOUR_INFURA_PROJECT_ID"
w3 = Web3(Web3.HTTPProvider(INFURA_URL))

TOKEN_ADDRESS = "0x26F226c7337ABB3c109DcD4D4345A82fBb243533"  # $TRY
ERC20_ABI = json.loads('[{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"from","type":"address"},{"indexed":true,"internalType":"address","name":"to","type":"address"},{"indexed":false,"internalType":"uint256","name":"value","type":"uint256"}],"name":"Transfer","type":"event"}]')

REGISTRY_CONTRACT = "0xYourMerkleRegistryAddress"
REGISTRY_ABI = json.loads('[{"inputs":[],"stateMutability":"nonpayable","type":"constructor"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"bytes32","name":"root","type":"bytes32"},{"indexed":false,"internalType":"uint256","name":"timestamp","type":"uint256"}],"name":"RootUpdated","type":"event"},{"inputs":[],"name":"latestRoot","outputs":[{"internalType":"bytes32","name":"","type":"bytes32"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"bytes32","name":"root","type":"bytes32"}],"name":"updateRoot","outputs":[],"stateMutability":"nonpayable","type":"function"}]')

PRIVATE_KEY = "0xYOUR_PRIVATE_KEY"
ACCOUNT = Account.from_key(PRIVATE_KEY)
CHAIN_ID = 1

STORAGE_DIR = "resonance_storage"
if not os.path.exists(STORAGE_DIR):
    os.makedirs(STORAGE_DIR)

# Secrets
resonance_hmac_key = os.urandom(32)
fernet_key = Fernet.generate_key()
fernet = Fernet(fernet_key)

resonance_matrix = {}
burned_tokens = 0
TOTAL_SUPPLY = 1_021_000_000
BURN_TARGET = 1_000_000_000

# ---------------------------
# UTILITIES
# ---------------------------
def derive_resonance_id(tx_hash: str) -> str:
    return hmac.new(resonance_hmac_key, tx_hash.encode(), hashlib.sha256).hexdigest()

def encrypt_payload(payload: dict) -> bytes:
    return fernet.encrypt(json.dumps(payload).encode())

def decrypt_payload(token: bytes) -> dict:
    return json.loads(fernet.decrypt(token).decode())

def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

def create_resonance_hash(data: str) -> str:
    return hashlib.sha256(data.encode()).hexdigest()

# ---------------------------
# MERKLE TREE
# ---------------------------
def build_merkle_tree(leaves):
    if not leaves: return None, []
    level = [bytes.fromhex(h) for h in leaves]
    tree = [level]
    while len(level) > 1:
        next_level = []
        for i in range(0, len(level), 2):
            left = level[i]
            right = level[i+1] if i+1 < len(level) else left
            combined = hashlib.sha256(left + right).digest()
            next_level.append(combined)
        level = next_level
        tree.append(level)
    root = tree[-1][0].hex()
    return root, [[n.hex() for n in lvl] for lvl in tree]

def collect_all_encrypted_hashes():
    leaves = []
    for filename in sorted(os.listdir(STORAGE_DIR)):
        if filename.endswith(".blob"):
            with open(os.path.join(STORAGE_DIR, filename), "rb") as fh:
                blob = fh.read()
            leaves.append(sha256_bytes(blob))
    return leaves

# ---------------------------
# RESONANCE FUNCTIONS
# ---------------------------
def store_resonance_for_tx(tx_hash, from_addr, to_addr, value, extra_metadata=None):
    resonance_id = derive_resonance_id(tx_hash)
    payload = {
        "resonance_id": resonance_id,
        "tx_hash": tx_hash,
        "from": from_addr,
        "to": to_addr,
        "value": value,
        "timestamp": int(time.time()),
        "matrix_pointer": f"/secure_storage/{resonance_id}",
        "metadata": extra_metadata or {}
    }
    token = encrypt_payload(payload)
    encrypted_hash = sha256_bytes(token)
    with open(os.path.join(STORAGE_DIR, f"{resonance_id}.blob"), "wb") as f:
        f.write(token)
    return resonance_id, token.hex(), encrypted_hash

def record_instant_marker(tx_data):
    resonance_hash = create_resonance_hash(json.dumps(tx_data) + str(time.time()))
    resonance_matrix[resonance_hash] = {
        "status": "PENDING",
        "eth_hash": None,
        "tx_data": tx_data
    }
    return resonance_hash

def link_eth_confirmation(resonance_hash, eth_hash):
    if resonance_hash in resonance_matrix:
        resonance_matrix[resonance_hash]["eth_hash"] = eth_hash
        resonance_matrix[resonance_hash]["status"] = "CONFIRMED"

# ---------------------------
# ETH TRANSACTION
# ---------------------------
def send_eth_transaction(to_address, amount_eth):
    nonce = w3.eth.get_transaction_count(ACCOUNT.address)
    tx = {
        "nonce": nonce,
        "to": to_address,
        "value": w3.to_wei(amount_eth, "ether"),
        "gas": 21000,
        "gasPrice": w3.to_wei("30", "gwei"),
        "chainId": CHAIN_ID
    }
    signed_tx = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    return w3.to_hex(tx_hash)

# ---------------------------
# MERKLE ANCHOR
# ---------------------------
def anchor_merkle_root(root_hex):
    contract = w3.eth.contract(address=REGISTRY_CONTRACT, abi=REGISTRY_ABI)
    nonce = w3.eth.get_transaction_count(ACCOUNT.address)
    tx = contract.functions.updateRoot("0x" + root_hex).build_transaction({
        "from": ACCOUNT.address,
        "nonce": nonce,
        "gas": 200000,
        "gasPrice": w3.to_wei("30", "gwei"),
        "chainId": CHAIN_ID
    })
    signed = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)
    print(f"[Merkle Anchor] Root {root_hex}, tx {tx_hash.hex()}")

# ---------------------------
# BURN LOGIC
# ---------------------------
def burn_tokens(circulating_supply):
    global burned_tokens
    if burned_tokens < BURN_TARGET and circulating_supply >= TOTAL_SUPPLY:
        burned_tokens += BURN_TARGET
        remaining = TOTAL_SUPPLY - burned_tokens
        print(f"[Burn] Burned {BURN_TARGET} tokens. Remaining supply: {remaining}")
        return BURN_TARGET
    return 0

# ---------------------------
# LIVE WATCHER
# ---------------------------
def live_watcher(poll_interval=10):
    token_contract = w3.eth.contract(address=TOKEN_ADDRESS, abi=ERC20_ABI)
    last_block = w3.eth.block_number

    print("[Watcher] Starting live watcher...")
    while True:
        current_block = w3.eth.block_number
        if current_block > last_block:
            for event in token_contract.events.Transfer.createFilter(fromBlock=last_block+1, toBlock=current_block).get_all_entries():
                tx_hash = event.transactionHash.hex()
                from_addr = event.args['from']
                to_addr = event.args['to']
                value = event.args['value']

                tx_data = {"from": from_addr, "to": to_addr, "amount": value}
                resonance_hash = record_instant_marker(tx_data)
                store_resonance_for_tx(tx_hash, from_addr, to_addr, value, extra_metadata={"orb":"orb-42"})
                link_eth_confirmation(resonance_hash, tx_hash)

            last_block = current_block

            # Build and anchor Merkle root every new block batch
            leaves = collect_all_encrypted_hashes()
            if leaves:
                root, _ = build_merkle_tree(leaves)
                anchor_merkle_root(root)

        time.sleep(poll_interval)

# ---------------------------
# START WATCHER
# ---------------------------
if __name__ == "__main__":
    live_watcher()