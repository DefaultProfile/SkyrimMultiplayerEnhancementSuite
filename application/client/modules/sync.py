import os
import hashlib
import json

async def get_local_file_checksums(skyrim_data_dir):
    local_checksums = {}
    for root, _, files in os.walk(skyrim_data_dir):
        for file in files:
            file_path = os.path.join(root, file)
            with open(file_path, 'rb') as f:
                local_checksums[file] = hashlib.md5(f.read()).hexdigest()
    return local_checksums

async def verify_files(websocket, local_checksums, skyrim_data_dir):
    await send_message(websocket, json.dumps({"action": "verify", "checksums": local_checksums, "skyrim_data_dir": skyrim_data_dir}))
    response = await receive_message(websocket)
    return json.loads(response)

async def synchronize_files(websocket, discrepancies, skyrim_data_dir):
    for file in discrepancies['missing'] + discrepancies['mismatch']:
        await download_file(websocket, file, skyrim_data_dir)
