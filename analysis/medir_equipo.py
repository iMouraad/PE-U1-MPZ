"""Ejecuta los clientes publicados y conserva una sesión propia de mediciones.

Desde la raíz del repositorio:
python analysis/medir_equipo.py sockets --salida data/melanie/sockets

La duración de cada corrida incluye conexiones y trabajo de los clientes.
Las latencias individuales conservan los límites del cliente original.
"""

import argparse
from concurrent.futures import ThreadPoolExecutor
import csv
from datetime import datetime
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import platform
import socket
import subprocess
import sys
from tempfile import mkdtemp
import threading
import time


CAMPOS = [
    "equipo", "corrida", "modo", "bytes_mensaje", "id_mensaje",
    "latencia_ms", "duracion_corrida_s", "calentamiento", "cliente",
]


def cargar_cliente(raiz, mecanismo):
    archivo = raiz / "src" / mecanismo / "latencia.py"
    spec = importlib.util.spec_from_file_location(f"medicion_{mecanismo}", archivo)
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo, archivo


def medir_cliente(modulo, mecanismo, cliente, tamano, corrida, modo):
    if mecanismo == "grpc":
        return modulo.medir_cliente(cliente, tamano, corrida, modo)
    filas = []
    modulo.medir(cliente, tamano, corrida, filas)
    return [
        (f"sockets-{modo}-{tamano}-c{corrida}-{nodo}-{envio:03d}", latencia, nodo)
        for _, _, _, nodo, envio, latencia in filas
    ]


def medir_corrida(modulo, mecanismo, modo, tamano, corrida):
    clientes = ("nodo-B",)
    if modo == "concurrente":
        clientes = ("nodo-A", "nodo-B", "nodo-C")
    barrera = threading.Barrier(len(clientes))

    def trabajo(cliente):
        barrera.wait(timeout=15)
        return medir_cliente(modulo, mecanismo, cliente, tamano, corrida, modo)

    inicio = time.perf_counter()
    if modo == "secuencial":
        resultados = trabajo(clientes[0])
    else:
        with ThreadPoolExecutor(max_workers=len(clientes)) as ejecutor:
            tareas = [ejecutor.submit(trabajo, cliente) for cliente in clientes]
            resultados = [fila for tarea in tareas for fila in tarea.result()]
    duracion = time.perf_counter() - inicio
    if len(resultados) != modulo.ENVIOS * len(clientes):
        raise RuntimeError("La corrida no contiene todos los mensajes esperados")
    return [
        [platform.node(), corrida, modo, tamano, identificador, latencia,
         duracion, int(corrida == 0), cliente]
        for identificador, latencia, cliente in resultados
    ]


def esperar_servidor(modulo, mecanismo, proceso):
    if mecanismo == "grpc":
        with modulo.grpc.insecure_channel(f"{modulo.HOST}:{modulo.PUERTO}") as canal:
            modulo.grpc.channel_ready_future(canal).result(timeout=10)
        return
    limite = time.monotonic() + 10
    while time.monotonic() < limite:
        if proceso.poll() is not None:
            raise RuntimeError("El servidor terminó antes de comenzar")
        try:
            with socket.create_connection((modulo.HOST, modulo.PUERTO), timeout=.5):
                return
        except (ConnectionRefusedError, TimeoutError):
            time.sleep(.1)
    raise RuntimeError("El servidor TCP no quedó disponible")


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("mecanismo", choices=("sockets", "grpc"))
    parser.add_argument("--salida", type=Path, required=True, help="Carpeta nueva de resultados")
    parser.add_argument("--repeticiones", type=int, default=5)
    args = parser.parse_args()
    if args.repeticiones < 5:
        parser.error("Se requieren al menos cinco repeticiones válidas")
    if args.salida.exists():
        parser.error("La carpeta de salida ya existe")
    raiz = Path(__file__).resolve().parents[1]
    modulo, fuente = cargar_cliente(raiz, args.mecanismo)
    with socket.socket() as comprobacion:
        comprobacion.bind((modulo.HOST, modulo.PUERTO))

    args.salida.parent.mkdir(parents=True, exist_ok=True)
    inicio = datetime.now().astimezone().isoformat()
    temporal = Path(mkdtemp(prefix="corrida-", dir=args.salida.parent))
    try:
        carpeta = Path(temporal) / "resultados"
        carpeta.mkdir()
        with (carpeta / "servidor.log").open("w", encoding="utf-8") as registro:
            servidor = subprocess.Popen(
                [sys.executable, "-X", "utf8", "-u", str(fuente), "servidor"],
                stdout=registro, stderr=subprocess.STDOUT,
            )
            try:
                esperar_servidor(modulo, args.mecanismo, servidor)
                print(f"{args.mecanismo}: servidor disponible en {modulo.HOST}:{modulo.PUERTO}", flush=True)
                for modo in ("secuencial", "concurrente"):
                    filas = []
                    for tamano in modulo.TAMANOS:
                        for corrida in range(args.repeticiones + 1):
                            nuevas = medir_corrida(modulo, args.mecanismo, modo, tamano, corrida)
                            filas.extend(nuevas)
                            print(f"{modo} | {tamano} B | corrida {corrida} | {len(nuevas)} mensajes", flush=True)
                    with (carpeta / f"latencias_{args.mecanismo}_{modo}.csv").open(
                        "x", encoding="utf-8", newline=""
                    ) as archivo:
                        escritor = csv.writer(archivo)
                        escritor.writerow(CAMPOS)
                        escritor.writerows(filas)
            finally:
                if servidor.poll() is None:
                    if os.name == "nt":
                        subprocess.run(
                            ["taskkill", "/PID", str(servidor.pid), "/T", "/F"],
                            check=True, stdout=subprocess.DEVNULL,
                        )
                    else:
                        servidor.terminate()
                    servidor.wait(timeout=10)
        metadata = {
            "mecanismo": args.mecanismo, "equipo": platform.node(),
            "python": platform.python_version(), "inicio": inicio,
            "fin": datetime.now().astimezone().isoformat(),
            "repeticiones_validas": args.repeticiones, "calentamiento_por_condicion": 1,
            "fuente": str(fuente.relative_to(raiz)),
            "sha256_fuente": hashlib.sha256(fuente.read_bytes()).hexdigest(),
            "duracion_corrida": "Desde antes de crear los clientes hasta finalizar sus conexiones; incluye el grupo de hilos en concurrencia",
            "latencia_individual": "Según los límites del cliente original; JSON se prepara antes del cronómetro y gRPC serializa durante la llamada",
        }
        (carpeta / "sesion.json").write_text(
            json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        carpeta.rename(args.salida)
    finally:
        if (temporal / "resultados").exists():
            print(f"Registros de la corrida incompleta conservados en {temporal}", flush=True)
        else:
            temporal.rmdir()
    print(f"Archivos guardados en {args.salida}", flush=True)


if __name__ == "__main__":
    main()
