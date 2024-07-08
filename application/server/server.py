import asyncio
import json
import os
import hashlib
import websockets
from modules.network import start_server, send_message, receive_message
from modules.sync import get_local_file_checksums, compare_checksums
from modules.game_state import GameState
from modules.chat import Chat
from modules.movement import Movement

class Server:
    def __init__(self):
        self.connected_clients = {}
        self.game_state = GameState()
        self.chat = Chat()
        self.movement = Movement()

    async def handle_client(self, websocket, path):
        client_id = id(websocket)
        self.connected_clients[client_id] = websocket
        try:
            async for message in websocket:
                await self.process_message(client_id, message)
        finally:
            del self.connected_clients[client_id]

    async def process_message(self, client_id, message):
        data = json.loads(message)
        if data['action'] == 'fetch_config':
            await self.send_config(client_id)
        elif data['action'] == 'verify':
            await self.verify_files(client_id, data)
        elif data['action'] == 'download':
            await self.send_file(client_id, data['file_path'])
        elif data['action'] == 'move':
            await self.update_position(client_id, data['movement_data'])

    async def send_config(self, client_id):
        config = {
            "skyrim_data_dir_name": "SteamLibrary/steamapps/common/Skyrim Special Edition/Data"
        }
        await send_message(self.connected_clients[client_id], json.dumps(config))

    async def verify_files(self, client_id, data):
        skyrim_data_dir = data['skyrim_data_dir']
        local_checksums = await get_local_file_checksums(skyrim_data_dir)
        discrepancies = compare_checksums(local_checksums, data['checksums'])
        await send_message(self.connected_clients[client_id], json.dumps(discrepancies))

    async def send_file(self, client_id, file_path):
        skyrim_data_dir = self.connected_clients[client_id].skyrim_data_dir
        file_full_path = os.path.join(skyrim_data_dir, file_path)
        with open(file_full_path, 'rb') as f:
            file_data = f.read()
        await send_message(self.connected_clients[client_id], json.dumps(file_data))

    async def update_position(self, client_id, movement_data):
        for other_client_id, other_client in self.connected_clients.items():
            if other_client_id != client_id:
                await send_message(other_client, json.dumps({"action": "move", "movement_data": movement_data}))

# Initialize and start the server
server = Server()
start_server = websockets.serve(server.handle_client, "0.0.0.0", 5000)

# Run the event loop
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
