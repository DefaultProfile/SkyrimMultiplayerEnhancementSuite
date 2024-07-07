import asyncio
import websockets
from modules.network import handle_client

async def main():
    async with websockets.serve(handle_client, "0.0.0.0", 5000):
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    asyncio.run(main())
