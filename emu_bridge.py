import socket
import threading

LOCAL_HOST = '127.0.0.1'
LOCAL_PORT = 15554
REMOTE_PORT = 5554

def forward(src, dst):
    try:
        while True:
            data = src.recv(4096)
            if not data:
                break
            dst.sendall(data)
    except:
        pass
    finally:
        try: src.shutdown(socket.SHUT_RD)
        except: pass
        try: dst.shutdown(socket.SHUT_WR)
        except: pass
        src.close()
        dst.close()

def handle_connection(remote_sock, local_addr):
    try:
        local_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        local_sock.connect(local_addr)
        t1 = threading.Thread(target=forward, args=(remote_sock, local_sock))
        t2 = threading.Thread(target=forward, args=(local_sock, remote_sock))
        t1.start()
        t2.start()
    except Exception as e:
        print(f"Connection error: {e}")
        remote_sock.close()

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(('', REMOTE_PORT))
    server.listen(5)
    print(f"Listening on 0.0.0.0:{REMOTE_PORT}, forwarding to {LOCAL_HOST}:{LOCAL_PORT}")

    while True:
        try:
            client_sock, addr = server.accept()
            print(f"Accepted connection from {addr}")
            threading.Thread(target=handle_connection, args=(client_sock, (LOCAL_HOST, LOCAL_PORT)), daemon=True).start()
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Accept error: {e}")

    server.close()

if __name__ == '__main__':
    main()
