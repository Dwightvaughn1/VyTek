# resonance_live_watcher_interactive.py
# Live watcher + Memnora Resonance Chain + interactive Infinity Orbs

import os
import json
import time
import hmac
import hashlib
from base64 import urlsafe_b64encode
from web3 import Web3
from eth_account import Account
from cryptography.fernet import Fernet
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backend_bases import MouseEvent
from threading import Thread

# ---------------------------
# CONFIGURATION
# ---------------------------
INFURA_URL = "https://mainnet.infura.io/v3/YOUR_INFURA_PROJECT_ID"
w3 = Web3(Web3.HTTPProvider(INFURA_URL))

TOKEN_ADDRESS = "0x26F226c7337ABB3c109DcD4D4345A82fBb243533"  # $TRY
ERC20_ABI = json.loads('[{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"from","type":"address"},{"indexed":true,"internalType":"address","name":"to","type":"address"},{"indexed":false,"internalType":"uint256","name":"value","type":"uint256"}],"name":"Transfer","type":"event"}]')

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
# VISUALIZATION
# ---------------------------
fig, ax = plt.subplots()
pos = {}
node_labels = {}

def draw_infinity_orbs(interactive=True):
    ax.clear()
    G = nx.Graph()
    for res_hash, info in resonance_matrix.items():
        G.add_node(res_hash)
        node_labels[res_hash] = res_hash[:6]
        for neighbor_hash in info.get("tx_data", {}).values():
            if isinstance(neighbor_hash, str) and neighbor_hash in resonance_matrix:
                G.add_edge(res_hash, neighbor_hash)

    global pos
    pos = nx.spring_layout(G, k=0.3, seed=42)
    nx.draw(G, pos, ax=ax, with_labels=True, labels=node_labels,
            node_size=500, font_size=8, node_color="cyan", edge_color="grey")
    ax.set_title("Interactive Infinity Orbs Resonance Matrix")
    plt.draw()

def on_click(event: MouseEvent):
    if event.inaxes is None:
        return
    x, y = event.xdata, event.ydata
    for node, (nx, ny) in pos.items():
        if (x - nx)**2 + (y - ny)**2 < 0.02:  # radius threshold
            info = resonance_matrix[node]
            print(f"\n--- Node Details ---")
            print(f"Resonance Hash: {node}")
            print(f"Status: {info['status']}")
            print(f"Ethereum Hash: {info['eth_hash']}")
            print(f"TX Data: {info['tx_data']}")
            print(f"Orb Metadata: {info['tx_data'].get('orb','N/A')}")
            print("-------------------\n")
            break

def visualizer_loop(interval=5):
    plt.ion()
    fig.canvas.mpl_connect("button_press_event", on_click)
    while True:
        draw_infinity_orbs()
        plt.pause(interval)

# ---------------------------
# LIVE WATCHER (mocked for demo)
# ---------------------------
def live_watcher_demo():
    import random, string
    while True:
        # Mock $TRY tx
        tx_hash = ''.join(random.choices(string.hexdigits.lower(), k=66))
        from_addr = "0x" + ''.join(random.choices(string.hexdigits.lower(), k=40))
        to_addr = "0x" + ''.join(random.choices(string.hexdigits.lower(), k=40))
        value = random.randint(1, 1000)

        tx_data = {"from": from_addr, "to": to_addr, "amount": value, "orb": f"orb-{random.randint(1,100)}"}
        resonance_hash = record_instant_marker(tx_data)
        store_resonance_for_tx(tx_hash, from_addr, to_addr, value, extra_metadata={"orb":tx_data["orb"]})
        link_eth_confirmation(resonance_hash, tx_hash)

        time.sleep(2)

# ---------------------------
# MAIN
# ---------------------------
if __name__ == "__main__":
    visual_thread = Thread(target=visualizer_loop, daemon=True)
    visual_thread.start()
    live_watcher_demo()  # replace with live_watcher() in production