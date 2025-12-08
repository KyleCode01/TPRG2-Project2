"""
ClientKDK.py
TPRG2131 – Programming for Technology II
Project 2 – Server / Client

Raspberry Pi client program:

- Verifies that it is running on a Raspberry Pi (exits cleanly if not).
- Connects to the server (HOST, PORT) via TCP.
- Every 2 seconds, collects 5 vcgencmd values from the Pi:
    * Core temperature (float, 1 decimal place)
    * Voltage
    * ARM clock
    * Core clock
    * Throttled status
- Adds an iteration counter (1..50) to the data.
- Packages each reading as a JSON string and sends it to the server,
  one JSON object per line.
- Performs exactly 50 iterations, then closes the connection and exits.
- Provides a simple Tkinter GUI with:
    * A Unicode LED that toggles at regular intervals to indicate activity.
    * An Exit button to close the client gracefully.
"""

import os
import platform
import socket
import subprocess
import json
import time
import threading
import tkinter as tk
from tkinter import messagebox

# PLATFORM VALIDATION 
# The project requires this script to be run on a Raspberry Pi.
# If it is launched on a non-Pi system (e.g., Windows PC), it should
# exit gracefully with a clear message and no Python error tracebacks.
if platform.system() != "Linux" or "raspberrypi" not in platform.uname().node.lower():
    print("This program must be run on a Raspberry Pi. Exiting...")
    exit(0)


# SERVER CONFIGURATION 
# Must match the HOST and PORT used by the server script.
HOST = "192.168.2.178"
PORT = 5000


#  DATA COLLECTION FUNCTION
def get_vcgen_data(iteration: int) -> dict:
    """
    Collect 5 vcgencmd values from a Raspberry Pi and return them
    collated in a dictionary, along with the given iteration count.

    One of the values (core temperature) is converted to a float and
    restricted to 1 decimal place, as required.

    Parameters:
        iteration (int): Counter indicating which sample (1..50) this is.

    Returns:
        dict: Data dictionary on success, or a dictionary containing
              an "error" key if something goes wrong.
    """
    try:
        def cmd(x: str) -> str:
            """
            Helper function to run a vcgencmd command and return its
            decoded string output with leading/trailing whitespace removed.
            """
            return subprocess.check_output(["vcgencmd"] + x.split()).decode().strip()

        # Collect 5 vcgencmd values:
        # 1) Core temperature (e.g., "temp=34.0'C")
        temp_raw = cmd("measure_temp").replace("temp=", "").replace("'C", "")

        # 2) Core voltage (string, e.g., "volt=0.85V")
        volts = cmd("measure_volts")

        # 3) ARM clock frequency
        clock_arm = cmd("measure_clock arm")

        # 4) Core clock frequency
        clock_core = cmd("measure_clock core")

        # 5) Throttled status flags
        throttled = cmd("get_throttled")

        # Convert temperature to float and restrict to 1 decimal place.
        temp_f = round(float(temp_raw), 1)

        # Build the collated data set.
        return {
            "iteration": iteration,
            "core_temp_C": temp_f,
            "voltage": volts,
            "clock_arm": clock_arm,
            "clock_core": clock_core,
            "throttled": throttled
        }

    except Exception as e:
        # If something fails (e.g., vcgencmd not found), return an "error" field.
        # This way the rest of the program can continue gracefully.
        return {"error": str(e), "iteration": iteration}




# CLIENT FUNCTION 
def run_client() -> None:
    try:
        # Create TCP socket and attempt connection to the server.
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT))
            print("Connected to server.")

            # Perform 50 data collection/transmission iterations.
            for i in range(1, 51):
                # Gather Pi status data.
                data = get_vcgen_data(i)

                # Convert dictionary to JSON string and encode to bytes.
                json_data = json.dumps(data).encode()

                # Send JSON line, terminated by newline to help the server split packets.
                s.sendall(json_data + b"\n")

                # Wait required 2 seconds before next sample.
                time.sleep(2)

            print("Completed 50 iterations. Closing connection.")

    except Exception as e:
        # Any connection / runtime issues are printed as system messages only.
        print(f"Connection error: {e}")
        exit(0)

    # Normal exit after loop completion.
    exit(0)



