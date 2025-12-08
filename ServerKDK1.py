"""
ServerKDK.py
TPRG2131 – Programming for Technology II
Project 2 – Server / Client

Matching server for current client progress:
- Waits for the client to connect
- Receives JSON packets
- Splits packets using newline
- Converts JSON strings into Python dictionaries
- Prints received data to the console
"""

import socket
import json

# Server must match client settings
HOST = "192.168.2.178"
PORT = 5000

print(f"Server starting on {HOST}:{PORT} ...")
print("Waiting for client connection...\n")


