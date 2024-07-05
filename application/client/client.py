import socket

def send_message():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('127.0.0.1', 9999))
    client_socket.send('Hello, server'.encode())
    response = client_socket.recv(1024).decode()
    print(f'Received: {response}')
    client_socket.close()

if __name__ == "__main__":
    send_message()
