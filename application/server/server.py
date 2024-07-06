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
        self.id = id(websocket)
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
        async for message in websocket:
            await process_message(client, message)
    finally:
        del connected_clients[client.id]

async def process_message(client, message):
    data = json.loads(message)
    if data['action'] == 'fetch_config':
        await fetch_config(client)
    elif data['action'] == 'verify':
        await verify_files(client, data)
    elif data['action'] == 'download':
        await send_file(client, data['file_path'])
    elif data['action'] == 'move':
        await update_position(client, data['movement_data'])

async def fetch_config(client):
    config = {
        "skyrim_data_dir_name": "SteamLibrary/steamapps/common/Skyrim Special Edition/Data"
    }
    await client.send(json.dumps(config))

async def verify_files(client, data):
    client.skyrim_data_dir = data['skyrim_data_dir']
    local_checksums = await get_local_file_checksums(client.skyrim_data_dir)
    discrepancies = compare_checksums(local_checksums, data['checksums'])
    await client.send(json.dumps(discrepancies))

async def send_file(client, file_path):
    file_full_path = os.path.join(client.skyrim_data_dir, file_path)
    with open(file_full_path, 'rb') as f:
        file_data = f.read()
    await client.send(json.dumps({"action": "file_data", "file_path": file_path, "file_data": file_data.decode('latin1')}))

async def update_position(client, movement_data):
    for other_client in connected_clients.values():
        if other_client.id != client.id:
            await other_client.send(json.dumps({"action": "move", "movement_data": movement_data}))

async def get_local_file_checksums(skyrim_data_dir):
    local_checksums = {}
    for root, _, files in os.walk(skyrim_data_dir):
        for file in files:
            file_path = os.path.join(root, file)
            with open(file_path, 'rb') as f:
                local_checksums[file] = hashlib.md5(f.read()).hexdigest()
    return local_checksums

def compare_checksums(local_checksums, client_checksums):
    discrepancies = {"missing": [], "mismatch": [], "unexpected": []}
    for file, checksum in client_checksums.items():
        if file not in local_checksums:
            discrepancies['missing'].append(file)
        elif local_checksums[file] != checksum:
            discrepancies['mismatch'].append(file)
    for file in local_checksums:
        if file not in client_checksums:
            discrepancies['unexpected'].append(file)
    return discrepancies

start_server = websockets.serve(register, "0.0.0.0", 5000)
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
