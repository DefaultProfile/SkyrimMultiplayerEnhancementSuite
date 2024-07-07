import json
import os
import hashlib

async def synchronize_files(response, websocket):
    file_list = json.loads(response)
    local_files = get_local_files()

    for file in file_list:
        if file not in local_files:
            await request_file(websocket, file)

def get_local_files():
    skyrim_data_dir = "C:/Path/To/Your/Skyrim/Data"
    local_files = {}
    for root, _, files in os.walk(skyrim_data_dir):
        for file in files:
            file_path = os.path.join(root, file)
            local_files[file_path] = hashlib.md5(open(file_path, 'rb').read()).hexdigest()
    return local_files

async def request_file(websocket, file):
    await websocket.send(json.dumps({"action": "request_file", "file": file}))
    response = await websocket.recv()
    save_file(file, response)

def save_file(file, data):
    with open(file, 'wb') as f:
        f.write(data)
