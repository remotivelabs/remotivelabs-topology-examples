import os
import socket
import sys

if len(sys.argv) != 2:
    print("send.py <frameId>#<payload>")
    sys.exit(1)

res = sys.argv[1].split("#", 1)

if len(res) != 2:
    print("send.py <frameId>#<payload>")
    sys.exit(1)

frame_id, payload = res

if len(payload) % 2 != 0:
    print("Payload must be in hexadecimal bytes")
    sys.exit(1)

frame_id_bytes = int(frame_id, 16).to_bytes(4, "big")  # 4 bytes
length_bytes = (len(payload) // 2).to_bytes(1, "big")  # 1 byte
payload_bytes = bytearray.fromhex(payload)  # payload
data = frame_id_bytes + length_bytes + payload_bytes

udp_client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sent_bytes_count = udp_client_socket.sendto(data, (os.environ["TARGET_HOST"], int(os.environ["TARGET_PORT"])))
