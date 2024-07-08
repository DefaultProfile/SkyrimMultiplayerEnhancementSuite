import asyncio
import json
from modules.network import connect_to_server, send_message, receive_message
from modules.sync import get_local_file_checksums, verify_files, synchronize_files
from modules.game_state import GameState
from modules.utilities import find_skyrim_data_directories
from modules.chat import Chat
from modules.movement import Movement

class Client:
    def __init__(self, server_url):
        self.server_url = server_url
        self.skyrim_data_dir_name = None
        self.skyrim_data_dir = None
        self.game_state = GameState()
        self.chat = Chat()
        self.movement = Movement()

    async def fetch_config(self, websocket):
        await send_message(websocket, json.dumps({"action": "fetch_config"}))
        response = await receive_message(websocket)
        config = json.loads(response)
        self.skyrim_data_dir_name = config['skyrim_data_dir_name']

    async def run(self):
        async with connect_to_server(self.server_url) as websocket:
            await self.fetch_config(websocket)
            found_directories = find_skyrim_data_directories(self.skyrim_data_dir_name)
            if not found_directories:
                self.skyrim_data_dir = input("Skyrim Special Edition/Data directory not found. Please specify the path to the Skyrim Data folder: ")
            elif len(found_directories) == 1:
                self.skyrim_data_dir = found_directories[0]
            else:
                self.skyrim_data_dir = self.prompt_user_for_directory(found_directories)

            local_checksums = await get_local_file_checksums(self.skyrim_data_dir)
            discrepancies = await verify_files(websocket, local_checksums, self.skyrim_data_dir)
            await synchronize_files(websocket, discrepancies, self.skyrim_data_dir)

            # Example movement data (to be replaced with actual game data)
            movement_data = {"player_id": 1, "position": {"x": 100, "y": 200, "z": 300}}
            await self.movement.move_character(websocket, movement_data)

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

# Connect to the server and run the client
server_url = "ws://10.0.0.154:5000"
client = Client(server_url)
asyncio.run(client.run())
