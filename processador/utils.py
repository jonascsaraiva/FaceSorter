import os
from datetime import datetime

LOG_PATH = os.path.join(os.getcwd(), "logs")
os.makedirs(LOG_PATH, exist_ok=True)
ARQUIVO_LOG = os.path.join(LOG_PATH, "log.txt")

def registrar_log(mensagem):
    hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(ARQUIVO_LOG, "a", encoding="utf-8") as log:
        log.write(f"[{hora}] {mensagem}\n")
