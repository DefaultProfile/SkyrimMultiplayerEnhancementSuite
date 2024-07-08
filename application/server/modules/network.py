import websockets

async def connect_to_server(server_url):
    return await websockets.connect(server_url)

async def send_message(websocket, message):
    await websocket.send(message)

async def receive_message(websocket):
    return await websocket.recv()

async def start_server(handler, host, port):
    return await websockets.serve(handler, host, port)
