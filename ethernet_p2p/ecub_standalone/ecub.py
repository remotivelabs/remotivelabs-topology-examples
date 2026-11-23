#!/usr/bin/env python3
"""ECUB UDP gateway - forwards datagrams from NET1 to NET2 without modification."""

from __future__ import annotations

import logging
import os
import signal
import socket
import struct
import time

LISTEN_HOST = os.environ.get("LISTEN_HOST", "172.40.0.2")
LISTEN_PORT = int(os.environ.get("LISTEN_PORT", "1234"))
SEND_BIND_HOST = os.environ.get("SEND_BIND_HOST", "172.41.0.1")
SEND_BIND_PORT = int(os.environ.get("SEND_BIND_PORT", "4321"))
SEND_HOST = os.environ.get("SEND_HOST", "172.41.0.2")
SEND_PORT = int(os.environ.get("SEND_PORT", "4321"))

RECV_BUF_SIZE = 65535
HEADER_SIZE = 8  # 4 bytes frame_id + 4 bytes payload_len

logging.basicConfig(
    level=getattr(logging, os.environ.get("LOG_LEVEL", "INFO").upper(), logging.INFO),
    format="%(asctime)s.%(msecs)03d [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("ecub-gateway")

running = True


def _shutdown_handler(signum, frame):
    global running
    logger.info("Received signal %d, shutting down", signum)
    running = False


signal.signal(signal.SIGTERM, _shutdown_handler)
signal.signal(signal.SIGINT, _shutdown_handler)


def _bind_with_retry(sock, host, port, retries=5, delay=2.0):
    for attempt in range(retries):
        try:
            sock.bind((host, port))
            return
        except OSError as exc:
            if attempt < retries - 1:
                logger.warning("Bind to %s:%d failed (%s), retrying in %.1fs...", host, port, exc, delay)
                time.sleep(delay)
            else:
                raise


def main() -> None:
    recv_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    send_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    try:
        _bind_with_retry(recv_sock, LISTEN_HOST, LISTEN_PORT)
        recv_sock.settimeout(1.0)

        _bind_with_retry(send_sock, SEND_BIND_HOST, SEND_BIND_PORT)

        dest = (SEND_HOST, SEND_PORT)

        logger.info(
            "ECUB gateway started: listening on %s:%d, forwarding to %s:%d (from %s:%d)",
            LISTEN_HOST, LISTEN_PORT, SEND_HOST, SEND_PORT, SEND_BIND_HOST, SEND_BIND_PORT,
        )

        counter = 0
        while running:
            try:
                data, addr = recv_sock.recvfrom(RECV_BUF_SIZE)
            except socket.timeout:
                continue

            send_sock.sendto(data, dest)

            if len(data) >= HEADER_SIZE:
                frame_id, payload_len = struct.unpack("!II", data[:HEADER_SIZE])
                logger.info("#%d from %s:%d frame_id=0x%03X payload_len=%d total=%d", counter, addr[0], addr[1], frame_id, payload_len, len(data))
            else:
                logger.info("#%d from %s:%d raw_len=%d (short packet)", counter, addr[0], addr[1], len(data))

            counter += 1

    finally:
        recv_sock.close()
        send_sock.close()
        logger.info("ECUB gateway stopped after %d forwarded datagrams", counter)


if __name__ == "__main__":
    main()
