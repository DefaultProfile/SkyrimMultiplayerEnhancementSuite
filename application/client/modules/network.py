import asyncio
import websockets

async def connect_to_server(server_url):
    return await websockets.connect(server_url)

async def send_message(websocket, message):
    await websocket.send(message)

async def receive_message(websocket):
    return await websocket.recv()
