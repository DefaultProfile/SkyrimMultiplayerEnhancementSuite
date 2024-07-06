import asyncio
import hashlib
import json
import os
import subprocess
import sys

def install_package(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

try:
    import websockets
except ImportError:
    print("websockets module not found. Installing...")
    install_package("websockets")
    import websockets

class Client:
    def __init__(self, server_url):
        self.server_url = server_url
        self.skyrim_data_dir_name = None
        self.skyrim_data_dir = None

    async def fetch_config(self, websocket):
        await websocket.send(json.dumps({"action": "fetch_config"}))
        response = await websocket.recv()
        config = json.loads(response)
        self.skyrim_data_dir_name = config['skyrim_data_dir_name']

    async def find_skyrim_data_directories(self):
        found_directories = []
        for drive in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
            skyrim_data_dir = os.path.join(f"{drive}:", self.skyrim_data_dir_name)
            if os.path.exists(skyrim_data_dir):
                found_directories.append(skyrim_data_dir)
        return found_directories

    async def get_local_file_checksums(self):
        local_checksums = {}
        for root, _, files in os.walk(self.skyrim_data_dir):
            for file in files:
                file_path = os.path.join(root, file)
                with open(file_path, 'rb') as f:
                    local_checksums[file] = hashlib.md5(f.read()).hexdigest()
        return local_checksums

    async def verify_files(self, websocket):
        local_checksums = await self.get_local_file_checksums()
        await websocket.send(json.dumps({"action": "verify", "checksums": local_checksums, "skyrim_data_dir": self.skyrim_data_dir}))
        response = await websocket.recv()
        discrepancies = json.loads(response)

        if discrepancies['missing']:
            print(f"Missing files: {discrepancies['missing']}")
        if discrepancies['mismatch']:
            print(f"Checksum mismatch: {discrepancies['mismatch']}")
        if discrepancies['unexpected']:
            print(f"Unexpected files: {discrepancies['unexpected']}")

    async def synchronize_files(self, websocket):
        local_checksums = await self.get_local_file_checksums()
        await websocket.send(json.dumps({"action": "verify", "checksums": local_checksums, "skyrim_data_dir": self.skyrim_data_dir}))
        response = await websocket.recv()
        discrepancies = json.loads(response)

        for file in discrepancies['missing'] + discrepancies['mismatch']:
            await self.download_file(websocket, file)

    async def download_file(self, websocket, file_path):
        await websocket.send(json.dumps({"action": "download", "file_path": file_path}))
        response = await websocket.recv()
        file_data = json.loads(response)

        file_full_path = os.path.join(self.skyrim_data_dir, file_path)
        os.makedirs(os.path.dirname(file_full_path), exist_ok=True)
        with open(file_full_path, 'wb') as f:
            f.write(file_data)

    async def move_character(self, websocket, movement_data):
        await websocket.send(json.dumps({"action": "move", "movement_data": movement_data}))

    def prompt_user_for_directory(self, directories):
        print("Multiple Skyrim Special Edition/Data directories found:")
        for i, directory in enumerate(directories):
            print(f"{i + 1}. {directory}")
        
        choice = input("Select the correct directory by entering the corresponding number: ")
        try:
            choice_index = int(choice) - 1
            if 0 <= choice_index < len(directories):
                return directories[choice_index]
            else:
                print("Invalid selection. Please try again.")
                return self.prompt_user_for_directory(directories)
        except ValueError:
            print("Invalid input. Please enter a number.")
            return self.prompt_user_for_directory(directories)

    async def run(self):
        async with websockets.connect(self.server_url) as websocket:
            await self.fetch_config(websocket)
            found_directories = await self.find_skyrim_data_directories()
            if not found_directories:
                self.skyrim_data_dir = input("Skyrim Special Edition/Data directory not found. Please specify the path to the Skyrim Data folder: ")
            elif len(found_directories) == 1:
                self.skyrim_data_dir = found_directories[0]
            else:
                self.skyrim_data_dir = self.prompt_user_for_directory(found_directories)

            await self.synchronize_files(websocket)
            await self.verify_files(websocket)
            
            # Example movement data (to be replaced with actual game data)
            movement_data = {"player_id": 1, "position": {"x": 100, "y": 200, "z": 300}}
            await self.move_character(websocket, movement_data)

# Connect to the server and run the client
server_url = "ws://10.0.0.154:5000"
client = Client(server_url)
asyncio.run(client.run())
