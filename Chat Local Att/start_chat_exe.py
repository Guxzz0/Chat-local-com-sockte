import subprocess
import sys
import time
import os

CREATE_NO_WINDOW = 0x08000000

def start_server():
    if sys.platform.startswith("win"):
        subprocess.Popen(
            ["pythonw", "server.py"],
            creationflags=CREATE_NO_WINDOW
        )
    else:
        subprocess.Popen(["python3", "server.py"])

def start_client():
    if sys.platform.startswith("win"):
        subprocess.Popen(
            ["pythonw", "client_gui.py"],
            creationflags=CREATE_NO_WINDOW
        )
    else:
        subprocess.Popen(["python3", "client_gui.py"])

if __name__ == "__main__":
    start_server()
    time.sleep(1)

    start_client()
    time.sleep(0.3)
    start_client()

    # Nada aparece — totalmente oculto