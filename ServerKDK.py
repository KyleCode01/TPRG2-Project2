# ServerKDK.py
# TPRG2131 – Programming for Technology II
# Project 2 – Server / Client
# Kyle Krepelka 
# 100923825
#
# Server application:
# Listens on a TCP socket for a single client connection.
# Receives newline-delimited JSON objects from the client.
# Extracts 6 fields from each JSON object and displays them in a Tkinter GUI.
# Toggles a Unicode LED icon each time new data is received.
# Provides an Exit button to close the GUI cleanly.
# 
# This script is intended to run on either a Raspberry Pi or a PC,


import socket
import json
import threading
import tkinter as tk
from tkinter import messagebox  

#  SERVER CONFIGURATION 
# NOTE: This IP/port must match the values used by the client.
HOST = "10.102.13.61"   # Server IP address 
PORT = 5000              # TCP port number to listen on


# GUI CLASS 
class ServerGUI:
    def __init__(self, root: tk.Tk) -> None:
        """Initialize and lay out all GUI widgets."""
        self.root = root
        self.root.title("Server JSON Viewer")

        # Track LED state so we can flip between ON/OFF.
        self.led_state = False

        # Dictionary of labels used to display each JSON field.
        # Keys correspond to the expected JSON keys sent by the client.
        self.labels = {
            "iteration": tk.Label(root, text="Iteration: --", font=("Arial", 14)),
            "core_temp_C": tk.Label(root, text="Core Temp: --", font=("Arial", 14)),
            "voltage": tk.Label(root, text="Voltage: --", font=("Arial", 14)),
            "clock_arm": tk.Label(root, text="ARM Clock: --", font=("Arial", 14)),
            "clock_core": tk.Label(root, text="Core Clock: --", font=("Arial", 14)),
            "throttled": tk.Label(root, text="Throttled: --", font=("Arial", 14)),
        }

        # Pack labels vertically into the window.
        for label in self.labels.values():
            label.pack(pady=3)

        # Unicode LED indicator (red/green circle emoji).
        self.led_label = tk.Label(root, text="🔴", font=("Arial", 40))
        self.led_label.pack(pady=10)

        # Exit button to close the program.
        self.exit_btn = tk.Button(root, text="Exit", command=self.exit_program)
        self.exit_btn.pack(pady=10)


    def update_display(self, data: dict) -> None:
        try:
            # Update individual label text if the key exists in the data dict.
            for key, label in self.labels.items():
                if key in data:
                    label.config(text=f"{key}: {data[key]}")

            # Flip LED state each time new, valid JSON data arrives.
            self.led_state = not self.led_state
            self.led_label.config(text="🟢" if self.led_state else "🔴")

        except Exception as e:
            # Any issues updating the GUI are printed as system messages.
            print(f"Error updating GUI: {e}")


    def exit_program(self) -> None:
        # Gracefully exit the program 
        self.root.destroy()
        exit(0)


# SERVER FUNCTION 
def start_server(gui: ServerGUI) -> None:
    # Start the TCP server and handle a single client connection.
    # gui (ServerGUI): Instance of the GUI used for display updates.
    try:
        # Create TCP/IP socket.
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((HOST, PORT))       # Bind to chosen interface/port.
            s.listen(1)                # Listen for a single incoming connection.
            print("Server running... waiting for client connection.")

            # Wait for and accept a client connection.
            conn, addr = s.accept()
            print(f"Client connected from {addr}")

            # 'conn' will be used to receive data while connected.
            with conn:
                buffer = ""  # Buffer for partial lines between recv() calls.

                while True:
                    # Read up to 1024 bytes from the socket.
                    data = conn.recv(1024).decode()

                    # If no data, client has disconnected; break the loop.
                    if not data:
                        break

                    buffer += data

                    # JSON packets are separated by newline characters.
                    while "\n" in buffer:
                        # Split off one full line (packet).
                        packet, buffer = buffer.split("\n", 1)

                        try:
                            # Attempt to decode JSON.
                            json_data = json.loads(packet)

                            # Schedule thread-safe GUI update.
                            gui.root.after(0, gui.update_display, json_data)

                        except json.JSONDecodeError:
                            # Ignore incomplete or malformed JSON lines.
                            pass

    except Exception as e:
        # Any unexpected socket / runtime errors show as system messages.
        print(f"Server error: {e}")


#  MAIN GUARD 
if __name__ == "__main__":
    # Create the Tkinter root window and GUI instance.
    root = tk.Tk()
    gui = ServerGUI(root)

    # Run the blocking socket server in a background thread so that the
    # Tkinter mainloop remains responsive.
    thread = threading.Thread(target=start_server, args=(gui,), daemon=True)
    thread.start()

    # Start the Tkinter event loop (blocks until window is closed).
    root.mainloop()
