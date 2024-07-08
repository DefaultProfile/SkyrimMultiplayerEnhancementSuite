import asyncio

class Chat:
    def __init__(self):
        self.messages = []

    async def send_message(self, websocket, message):
        self.messages.append(message)
        await websocket.send(json.dumps({"action": "chat", "message": message}))

    async def receive_message(self, websocket):
        message = await websocket.recv()
        self.messages.append(message)
        return message
