# ClientKDK.py
# TPRG2131 – Programming for Technology II
# Project 2 – Server / Client
# Client program:
# Works on BOTH Raspberry Pi and PC
# If on a Pi → collects real vcgencmd data
# If on a PC → uses safe dummy values
# Sends 50 JSON packets (2 seconds apart)
# Shows GUI with blinking LED + Exit button

import platform
import socket
import subprocess
import json
import time
import threading
import tkinter as tk


# PLATFORM DETECTION
IS_PI = (
    platform.system() == "Linux"
    and "raspberrypi" in platform.uname().node.lower()
)

if IS_PI:
    print("Running on Raspberry Pi – vcgencmd enabled.")
else:
    print("Running on PC – using simulated data (no vcgencmd).")


# SERVER CONFIGURATION
HOST = "10.102.13.61"   # Must match ServerKDK.py
PORT = 5000


# DATA COLLECTION FUNCTION
def get_vcgen_data(iteration: int) -> dict:
    """
    Collects Pi system data. If running on a PC, returns
    simulated values so the program can still operate.
    """

    # REAL DATA (PI ONLY)
    if IS_PI:
        try:
            def cmd(x: str) -> str:
                return subprocess.check_output(
                    ["vcgencmd"] + x.split()
                ).decode().strip()

            temp_raw = cmd("measure_temp").replace("temp=", "").replace("'C", "")
            temp_f = round(float(temp_raw), 1)

            # CHANGE: voltage now converted to float
            volts_raw = cmd("measure_volts")                 # e.g. "volt=0.84V"
            volts_clean = volts_raw.replace("volt=", "").replace("V", "")
            volts_f = round(float(volts_clean), 2)           # float with 2 decimals

            clock_arm = cmd("measure_clock arm")
            clock_core = cmd("measure_clock core")
            throttled = cmd("get_throttled")

            return {
                "iteration": iteration,
                "core_temp_C": temp_f,
                "voltage": volts_f,        # <-- NOW A FLOAT VALUE
                "clock_arm": clock_arm,
                "clock_core": clock_core,
                "throttled": throttled
            }

        except Exception as e:
            return {"error": str(e), "iteration": iteration}

    # SIMULATED DATA (PC MODE) 
    return {
        "iteration": iteration,
        "core_temp_C": 42.0,
        "voltage": 1.20,                             # <-- SIMULATED FLOAT VALUE
        "clock_arm": "frequency(45)=1500000000",
        "clock_core": "frequency(1)=500000000",
        "throttled": "throttled=0x0",
        "NOTE": "Simulated values – running on PC"
    }


# CLIENT NETWORK FUNCTION
def run_client() -> None:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT))
            print("Connected to server.")

            for i in range(1, 51):
                data = get_vcgen_data(i)
                json_data = json.dumps(data).encode()
                s.sendall(json_data + b"\n")
                time.sleep(2)

            print("Completed 50 iterations. Closing connection.")

    except Exception as e:
        print(f"Connection error: {e}")
        exit(0)

    exit(0)


# CLIENT GUI CLASS
class ClientGUI:
    """Simple blinking LED + Exit button."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        root.title("Client")

        self.led_on = False

        self.label_led = tk.Label(root, text="🔴", font=("Arial", 40))
        self.label_led.pack(pady=10)

        self.exit_button = tk.Button(root, text="Exit", command=self.exit_client)
        self.exit_button.pack(pady=10)

        self.toggle_led()

    def toggle_led(self):
        self.led_on = not self.led_on
        self.label_led.config(text="🟢" if self.led_on else "🔴")
        self.root.after(500, self.toggle_led)

    def exit_client(self):
        self.root.destroy()
        exit(0)


# MAIN PROGRAM
if __name__ == "__main__":
    root = tk.Tk()
    gui = ClientGUI(root)

    t = threading.Thread(target=run_client, daemon=True)
    t.start()

    root.mainloop()
