"""Medición de latencia de ida y vuelta con sockets TCP.

Uso (dos terminales, desde src/sockets):
  python latencia.py servidor            -> nodo-A en el puerto 5000, responde cada mensaje (eco)
  python latencia.py cliente             -> 1 corrida de calentamiento + 5 corridas de 100 envíos,
                                            con mensajes de ~100 bytes y de ~10 KB
  python latencia.py concurrente         -> nodo-A, nodo-B y nodo-C envían a la vez al servidor
"""
import csv
import json
import os
import socket
import sys
import threading
import time

HOST, PUERTO = "127.0.0.1", 5000
ENVIOS = 100
CORRIDAS = 5
TAMANOS = [100, 10_000]  # bytes aproximados de cada mensaje JSON

carpeta_data = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "data")
os.makedirs(carpeta_data, exist_ok=True)


def armar_mensaje(remitente, reloj, tamano):
    """Arma un JSON {sender, timestamp, message} de más o menos 'tamano' bytes."""
    base = {"sender": remitente, "timestamp": reloj, "message": ""}
    relleno = tamano - len(json.dumps(base)) - 1  # el -1 es por el \n
    base["message"] = "x" * max(relleno, 0)
    return (json.dumps(base) + "\n").encode("utf-8")


# ---------------------------------------------------------------- servidor (eco)
def atender(conn):
    with conn:
        lector = conn.makefile("r", encoding="utf-8")
        for linea in lector:                 # una línea = un mensaje completo
            conn.sendall(linea.encode("utf-8"))


def servidor():
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind((HOST, PUERTO))
    srv.listen()
    print(f"[nodo-A] servidor de eco en el puerto {PUERTO}. Ctrl+C para salir.")
    while True:
        conn, _ = srv.accept()
        threading.Thread(target=atender, args=(conn,), daemon=True).start()


# ---------------------------------------------------------------- cliente
def medir(remitente, tamano, corrida, filas):
    """Hace ENVIOS idas y vueltas por una misma conexión y guarda cada latencia en ms."""
    with socket.create_connection((HOST, PUERTO)) as s:
        lector = s.makefile("r", encoding="utf-8")
        for envio in range(1, ENVIOS + 1):
            datos = armar_mensaje(remitente, envio, tamano)
            inicio = time.perf_counter()
            s.sendall(datos)
            lector.readline()                # espera el eco completo
            fin = time.perf_counter()
            filas.append(["sockets", tamano, corrida, remitente, envio, round((fin - inicio) * 1000, 4)])


def guardar(nombre, filas):
    ruta = os.path.join(carpeta_data, nombre)
    with open(ruta, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["mecanismo", "tamano_bytes", "corrida", "nodo", "envio", "latencia_ms"])
        w.writerows(filas)
    print(f"Guardado: {ruta} ({len(filas)} filas)")


def cliente():
    filas = []
    for tamano in TAMANOS:
        medir("nodo-B", tamano, 0, [])        # corrida 0: calentamiento, se descarta
        for corrida in range(1, CORRIDAS + 1):
            medir("nodo-B", tamano, corrida, filas)
            print(f"tamaño {tamano} B, corrida {corrida}: listo")
    guardar("latencias_sockets.csv", filas)


def concurrente():
    filas, candado = [], threading.Lock()

    def trabajo(nodo, tamano):
        propias = []
        medir(nodo, tamano, 1, propias)
        with candado:
            filas.extend(propias)

    for tamano in TAMANOS:
        hilos = [threading.Thread(target=trabajo, args=(n, tamano)) for n in ("nodo-A", "nodo-B", "nodo-C")]
        for h in hilos:
            h.start()
        for h in hilos:
            h.join()
        print(f"tamaño {tamano} B: tres nodos a la vez, listo")
    guardar("latencias_sockets_concurrente.csv", filas)


if __name__ == "__main__":
    modo = sys.argv[1] if len(sys.argv) > 1 else ""
    if modo == "servidor":
        servidor()
    elif modo == "cliente":
        cliente()
    elif modo == "concurrente":
        concurrente()
    else:
        print(__doc__)
