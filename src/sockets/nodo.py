import csv
import json
import os
import random
import socket
import sys
import threading
import time
import uuid
from datetime import datetime

# Los tres nodos y sus puertos
NODOS = {"nodo-A": 5000, "nodo-B": 5001, "nodo-C": 5002}

nombre = sys.argv[1]                                   # por ejemplo: nodo-A
envios = int(sys.argv[2]) if len(sys.argv) > 2 else 7  # 3 nodos x 7 = 21 mensajes
puerto = NODOS[nombre]

reloj = 0                    # reloj de Lamport de este nodo
candado = threading.Lock()   # el reloj lo tocan dos hilos: el que envía y el que recibe

# CSV de eventos en la carpeta data/ del repositorio
carpeta_data = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "data")
os.makedirs(carpeta_data, exist_ok=True)
archivo = open(os.path.join(carpeta_data, f"eventos_sockets_{nombre}.csv"), "w", newline="", encoding="utf-8")
escritor = csv.writer(archivo)
escritor.writerow(["nodo", "tipo_evento", "reloj", "hora_real", "id_mensaje", "contraparte"])


def registrar(tipo, valor, id_mensaje, contraparte):
    escritor.writerow([nombre, tipo, valor, datetime.now().isoformat(sep=" "), id_mensaje, contraparte])
    archivo.flush()
    print(f"[{nombre}] {tipo:9} reloj={valor:3}  {contraparte}  ({id_mensaje})")


def atender(conn):
    """Recibe un mensaje y aplica la regla de Lamport: max(local, recibido) + 1."""
    global reloj
    with conn:
        linea = conn.makefile("r", encoding="utf-8").readline()
        msg = json.loads(linea)
        id_mensaje = msg["message"].split("|")[0]
        with candado:
            reloj = max(reloj, msg["timestamp"]) + 1
            registrar("recepcion", reloj, id_mensaje, msg["sender"])


def servidor():
    """Escucha en su puerto; cada conexión se atiende en un hilo aparte."""
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind(("127.0.0.1", puerto))
    srv.listen()
    while True:
        conn, _ = srv.accept()
        threading.Thread(target=atender, args=(conn,), daemon=True).start()


def enviar(destino):
    """Antes de enviar, el reloj sube en 1 y ese valor viaja como timestamp."""
    global reloj
    id_mensaje = uuid.uuid4().hex[:8]
    with candado:
        reloj += 1
        msg = {"sender": nombre, "timestamp": reloj, "message": f"{id_mensaje}|hola {destino}"}
        registrar("envio", reloj, id_mensaje, destino)
    with socket.create_connection(("127.0.0.1", NODOS[destino])) as s:
        s.sendall((json.dumps(msg) + "\n").encode("utf-8"))  # el \n delimita el mensaje


threading.Thread(target=servidor, daemon=True).start()
print(f"[{nombre}] escuchando en el puerto {puerto}")
input("Presiona Enter cuando los tres nodos estén encendidos... ")

otros = [n for n in NODOS if n != nombre]
for _ in range(envios):
    enviar(random.choice(otros))
    time.sleep(random.uniform(0.2, 1.0))

print(f"[{nombre}] terminé mis envíos; sigo recibiendo 5 segundos más")
time.sleep(5)
archivo.close()
