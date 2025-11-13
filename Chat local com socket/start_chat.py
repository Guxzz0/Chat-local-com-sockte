import subprocess
import time
import sys

def start_server():
    print("[INFO] Iniciando o servidor...")
    
    if sys.platform.startswith("win"):
        subprocess.Popen(["start", "cmd", "/k", "python server.py"], shell=True)
    else:
        subprocess.Popen(["gnome-terminal", "--", "python3", "server.py"])
    time.sleep(2) 

def start_client():
    print("[INFO] Iniciando cliente...")
   
    if sys.platform.startswith("win"):
        subprocess.Popen(["start", "cmd", "/k", "python client.py"], shell=True)
    else:
        subprocess.Popen(["gnome-terminal", "--", "python3", "client.py"])

if __name__ == "__main__":
    start_server()

    
    start_client()
    time.sleep(1)
    start_client()

    print("\n✅ Servidor e dois clientes iniciados com sucesso!")
    print("Digite os apelidos em cada janela de cliente e comece o chat.")