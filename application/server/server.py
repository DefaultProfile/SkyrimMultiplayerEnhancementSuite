import socket

def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('0.0.0.0', 9999))
    server_socket.listen(5)
    print('Server listening on port 9999')

    while True:
        client_socket, addr = server_socket.accept()
        print(f'Connection from {addr}')
        handle_client(client_socket)

def handle_client(client_socket):
    request = client_socket.recv(1024).decode()
    print(f'Received: {request}')
    client_socket.send('ACK'.encode())
    client_socket.close()

if __name__ == "__main__":
    start_server()
