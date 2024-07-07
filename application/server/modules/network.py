import asyncio
import websockets
import json
from .sync import handle_file_request

connected_clients = {}

async def register(websocket):
    client_id = id(websocket)
    connected_clients[client_id] = websocket
    try:
        async for message in websocket:
            await handle_message(client_id, message)
    finally:
        del connected_clients[client_id]

async def handle_message(client_id, message):
    data = json.loads(message)
    if data['action'] == 'request_file_list':
        await handle_file_request(client_id)
