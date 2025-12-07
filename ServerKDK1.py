"""
ClientKDK.py
TPRG2131 – Programming for Technology II
Project 2 – Server / Client

Raspberry Pi client program:
- Connects to server
- Collects vcgencmd data every 2 seconds (50 iterations)
- Sends JSON data to the server
- Shows a simple GUI LED + Exit button
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
# Exit cleanly if not running on a Raspberry Pi
if platform.system() != "Linux" or "raspberrypi" not in platform.uname().node.lower():
    print("This program must be run on a Raspberry Pi. Exiting...")
    exit(0)
    
# SERVER CONFIGURATION 
HOST = "192.168.2.178"   # Must match ServerKDK.py
PORT = 5000


#DATA COLLECTION FUNCTION
def get_vcgen_data(iteration: int) -> dict:
    """
    Collect 5 vcgencmd values from a Raspberry Pi and return them
    collated in a dictionary, along with the given iteration count.
    One of the values (core temperature) is converted to a float and
    restricted to 1 decimal place.
    """
    try:
        def cmd(x: str) -> str:
            """Run a vcgencmd command and return stripped string output."""
            return subprocess.check_output(["vcgencmd"] + x.split()).decode().strip()

        # 1) Core temperature -> float with 1 decimal place
        temp_raw = cmd("measure_temp").replace("temp=", "").replace("'C", "")
        temp_f = round(float(temp_raw), 1)

        # 2) Core voltage
        volts = cmd("measure_volts")

        # 3) ARM clock frequency
        clock_arm = cmd("measure_clock arm")

        # 4) Core clock frequency
        clock_core = cmd("measure_clock core")

        # 5) Throttled status
        throttled = cmd("get_throttled")

        return {
            "iteration": iteration,
            "core_temp_C": temp_f,
            "voltage": volts,
            "clock_arm": clock_arm,
            "clock_core": clock_core,
            "throttled": throttled
        }

    except Exception as e:
        # Return an error dict instead of crashing
        return {"error": str(e), "iteration": iteration}

