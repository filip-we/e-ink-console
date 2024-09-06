import logging

import os
import socket
import signal


class LinuxProcessHandler:
    def __init__(self):
        self.log = logging.getLogger()
        self.terminated = False
        signal.signal(signal.SIGTERM, self.handle_sigterm)

        self.sd_notify_socket = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
        self.socket_address = os.getenv("NOTIFY_SOCKET", None)
        if not self.socket_address:
            self.log.warning("Could not find socket to talk to systemd with.")
            return

        if self.socket_address[0] == "@":
            self.socket_address = 0x00 + self.socket_address[1:]
        self.sd_notify_socket.connect(self.socket_address)
        self.log.info("systemd-socket is connected.")

    def handle_sigterm(self, signal, frame):
        self.log.debug("Received a SIGTERM signal. Flagging the progam to exit.")
        self.terminated = True

    def sd_notify(self, msg):
        if not self.socket_address:
            self.log.debug("Skipping sending message since socket was not setup.")
            return

        self.log.debug(f"Sending message to systemd: {msg}")
        self.sd_notify_socket.sendall(msg.encode("utf-8"))
