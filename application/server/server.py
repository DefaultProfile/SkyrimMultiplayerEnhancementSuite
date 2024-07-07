import asyncio
import websockets
from modules.network import register

start_server = websockets.serve(register, "0.0.0.0", 5000)
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
