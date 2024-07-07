import json
from .sync import send_file_list, send_file

async def handle_client(websocket, path):
    async for message in websocket:
        data = json.loads(message)
        if data["action"] == "request_file_list":
            await send_file_list(websocket)
        elif data["action"] == "request_file":
            await send_file(websocket, data["file"])
