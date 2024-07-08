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

def compare_checksums(local_checksums, client_checksums):
    discrepancies = {"missing": [], "mismatch": [], "unexpected": []}
    for file, checksum in client_checksums.items():
        if file not in local_checksums:
            discrepancies['missing'].append(file)
        elif local_checksums[file] != checksum:
            discrepancies['mismatch'].append(file)
    for file in local_checksums:
        if file not in client_checksums:
            discrepancies['unexpected'].append(file)
    return discrepancies
