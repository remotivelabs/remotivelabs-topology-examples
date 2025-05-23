import os
import socket

if __name__ == "__main__":
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind(("0.0.0.0", int(os.environ["SERVER_PORT"])))

    while True:
        message, address = server_socket.recvfrom(1024)
        print("/".join(map(str, address)) + " " + message[:4].hex() + "[" + message[4:5].hex() + "]" + message[5:].hex())
