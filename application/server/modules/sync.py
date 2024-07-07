import json
import os
import hashlib

async def send_file_list(websocket):
    skyrim_data_dir = "C:/Path/To/Your/Skyrim/Data"
    files = get_local_files(skyrim_data_dir)
    await websocket.send(json.dumps(files))

def get_local_files(skyrim_data_dir):
    local_files = {}
    for root, _, files in os.walk(skyrim_data_dir):
        for file in files:
            file_path = os.path.join(root, file)
            local_files[file_path] = hashlib.md5(open(file_path, 'rb').read()).hexdigest()
    return local_files

async def send_file(websocket, file):
    with open(file, 'rb') as f:
        data = f.read()
    await websocket.send(data)
