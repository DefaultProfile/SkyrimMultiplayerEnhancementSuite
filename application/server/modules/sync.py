import json
import os
import hashlib

async def handle_file_request(client_id):
    file_list = get_file_list()
    await connected_clients[client_id].send(json.dumps(file_list))

def get_file_list():
    file_list = {}
    skyrim_data_dir = "path_to_skyrim_data"
    for root, _, files in os.walk(skyrim_data_dir):
        for file in files:
            file_path = os.path.join(root, file)
            with open(file_path, 'rb') as f:
                file_list[file] = hashlib.md5(f.read()).hexdigest()
    return file_list
