import asyncio
import websockets
import json
from .sync import synchronize_files

async def connect_to_server(server_url):
    async with websockets.connect(server_url) as websocket:
        await websocket.send(json.dumps({"action": "request_file_list"}))
        response = await websocket.recv()
        await synchronize_files(response, websocket)
