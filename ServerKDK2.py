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

# Create server socket
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen(1)

    # Accept client
    conn, addr = s.accept()
    print(f"Client connected from: {addr}\n")

    with conn:
        buffer = ""

        while True:
            # Receive up to 1024 bytes
            data = conn.recv(1024).decode()

            # If client disconnects
            if not data:
                print("\nClient disconnected.")
                break

            buffer += data

            # Split JSON packets on newline
            while "\n" in buffer:
                packet, buffer = buffer.split("\n", 1)

                try:
                    json_data = json.loads(packet)
                    print("Received JSON:", json_data)
                except json.JSONDecodeError:
                    # Ignore incomplete or broken packets
                    pass



