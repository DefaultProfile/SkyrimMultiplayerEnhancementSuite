import asyncio
import websockets
import hashlib
import os
import json
import subprocess
import sys

def install_package(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

try:
    import websockets
except ImportError:
    print("websockets module not found. Installing...")
    install_package("websockets")
    import websockets

class Client:
    def __init__(self, websocket):
        self.websocket = websocket
        self.id = id(websocket)  # Unique identifier for the client
        self.skyrim_data_dir = None

    async def send(self, message):
        await self.websocket.send(message)

    async def receive(self):
        return await self.websocket.recv()

connected_clients = {}

async def register(websocket):
    client = Client(websocket)
    connected_clients[client.id] = client
    try:
        # Send config.json to the client
        await send_config_file(client)
        await client.websocket.wait_closed()
    finally:
        del connected_clients[client.id]

async def handler(websocket, path):
    await register(websocket)
    async for message in websocket:
        data = json.loads(message)
        action = data.get("action")
        
        if action == "verify":
            await handle_verify(websocket, data)
        elif action == "sync":
            await handle_sync(websocket, data)
        elif action == "move":
            await handle_move(data)

async def send_config_file(client):
    config_path = "config.json"
    if os.path.exists(config_path):
        with open(config_path, 'r') as file:
            config_data = file.read()
        await client.send(json.dumps({"action": "config", "config_data": config_data}))

async def handle_verify(websocket, data):
    client = get_client_by_websocket(websocket)
    checksums = data.get("checksums", {})
    client.skyrim_data_dir = data.get("skyrim_data_dir")
    
    server_checksums = get_server_checksums(client.skyrim_data_dir)
    discrepancies = {
        "missing": [file for file in server_checksums if file not in checksums],
        "mismatch": [file for file in checksums if checksums[file] != server_checksums.get(file)],
        "unexpected": [file for file in checksums if file not in server_checksums]
    }
    
    await client.send(json.dumps(discrepancies))

async def handle_sync(websocket, data):
    client = get_client_by_websocket(websocket)
    # Sync logic here

async def handle_move(data):
    for client in connected_clients.values():
        await client.send(json.dumps(data))

def get_server_checksums(skyrim_data_dir):
    checksums = {}
    for root, _, files in os.walk(skyrim_data_dir):
        for file in files:
            file_path = os.path.join(root, file)
            with open(file_path, 'rb') as f:
                checksums[file] = hashlib.md5(f.read()).hexdigest()
    return checksums

def get_client_by_websocket(websocket):
    for client in connected_clients.values():
        if client.websocket == websocket:
            return client
    return None

async def main():
    async with websockets.serve(handler, "0.0.0.0", 5000):
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    asyncio.run(main())
