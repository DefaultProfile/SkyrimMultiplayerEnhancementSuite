import asyncio
from modules.network import connect_to_server

async def main():
    server_url = "ws://10.0.0.154:5000"
    await connect_to_server(server_url)

if __name__ == "__main__":
    asyncio.run(main())
