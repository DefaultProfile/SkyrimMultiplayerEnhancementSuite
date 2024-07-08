import os

def find_skyrim_data_directories(skyrim_data_dir_name):
    found_directories = []
    for drive in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
        skyrim_data_dir = os.path.join(f"{drive}:", skyrim_data_dir_name)
        if os.path.exists(skyrim_data_dir):
            found_directories.append(skyrim_data_dir)
    return found_directories
