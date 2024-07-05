import os
import shutil

# Define paths
source_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'application'))
destination_dir = '/path/to/destination'  # Update this path

# Ensure the destination directory exists
os.makedirs(destination_dir, exist_ok=True)

# Copy the files
for file_name in ['server/server.py', 'client/client.py']:
    full_file_name = os.path.join(source_dir, file_name)
    if os.path.isfile(full_file_name):
        shutil.copy(full_file_name, destination_dir)

print("Files deployed successfully!")
