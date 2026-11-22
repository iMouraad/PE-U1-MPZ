"""Nodo gRPC con reloj de Lamport y registro de eventos en CSV.

Ejecutar una instancia por terminal desde la raíz del repositorio:
    python src/grpc/nodo.py nodo-A
    python src/grpc/nodo.py nodo-B
    python src/grpc/nodo.py nodo-C
"""

import argparse
import csv
import random
import sys
import threading
import time
import uuid
from concurrent import futures
from datetime import datetime
from pathlib import Path

import grpc


CARPETA_GENERADA = Path(__file__).resolve().parent / "generated"
sys.path.insert(0, str(CARPETA_GENERADA))
import communication_pb2  # noqa: E402
import communication_pb2_grpc  # noqa: E402


NODOS = {"nodo-A": 50051, "nodo-B": 50052, "nodo-C": 50053}
CARPETA_DATA = Path(__file__).resolve().parents[2] / "data"


class NodoGrpc(communication_pb2_grpc.CommunicationServiceServicer):
    def __init__(self, nombre, carpeta_data=CARPETA_DATA):
        self.nombre = nombre
        self.reloj = 0
        self.candado = threading.Lock()
        carpeta_data.mkdir(parents=True, exist_ok=True)
        ruta = carpeta_data / f"eventos_grpc_{nombre}.csv"
        self.archivo = ruta.open("w", newline="", encoding="utf-8")
        self.escritor = csv.writer(self.archivo)
        self.escritor.writerow(
            ["nodo", "tipo_evento", "reloj", "hora_real", "id_mensaje", "contraparte"]
        )

    def registrar(self, tipo, identificador, contraparte):
        """Registra un evento mientras el llamador conserva el candado."""
        self.escritor.writerow(
            [
                self.nombre,
                tipo,
                self.reloj,
                datetime.now().isoformat(sep=" "),
                identificador,
                contraparte,
            ]
        )
        self.archivo.flush()
        print(
            f"[{self.nombre}] {tipo:9} reloj={self.reloj:3}  "
            f"{contraparte}  ({identificador})",
            flush=True,
        )

    def ExchangeMessage(self, request, context):
        """Recibe un mensaje y aplica max(reloj local, reloj recibido) + 1."""
        if request.sender not in NODOS or "|" not in request.message:
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, "Mensaje o emisor no válido")
        identificador = request.message.split("|", 1)[0]
        identificador_ack = f"{identificador}-ack"
        with self.candado:
            self.reloj = max(self.reloj, request.lamport_clock) + 1
            self.registrar("recepcion", identificador, request.sender)
            self.reloj += 1
            self.registrar("envio", identificador_ack, request.sender)
            reloj_respuesta = self.reloj
        return communication_pb2.MessageResponse(
            sender=self.nombre,
            timestamp=datetime.now().isoformat(),
            message=f"ack|{identificador}",
            lamport_clock=reloj_respuesta,
        )

    def enviar(self, destino):
        """Espera al nodo remoto, incrementa el reloj y envía un mensaje."""
        direccion = f"127.0.0.1:{NODOS[destino]}"
        with grpc.insecure_channel(direccion) as canal:
            grpc.channel_ready_future(canal).result(timeout=10)
            identificador = uuid.uuid4().hex[:8]
            with self.candado:
                self.reloj += 1
                reloj_envio = self.reloj
                self.registrar("envio", identificador, destino)
            solicitud = communication_pb2.MessageRequest(
                sender=self.nombre,
                timestamp=datetime.now().isoformat(),
                message=f"{identificador}|hola {destino}",
                lamport_clock=reloj_envio,
            )
            stub = communication_pb2_grpc.CommunicationServiceStub(canal)
            respuesta = stub.ExchangeMessage(solicitud, timeout=5)
            if (
                respuesta.sender != destino
                or respuesta.message != f"ack|{identificador}"
            ):
                raise RuntimeError(f"Respuesta inesperada de {destino}")
            with self.candado:
                self.reloj = max(self.reloj, respuesta.lamport_clock) + 1
                self.registrar("recepcion", f"{identificador}-ack", destino)

    def cerrar(self):
        self.archivo.close()


def argumentos():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("nombre", choices=NODOS)
    parser.add_argument("envios", nargs="?", type=int, default=7)
    parser.add_argument("--espera-inicio", type=float, default=5)
    parser.add_argument("--espera-final", type=float, default=10)
    parser.add_argument("--semilla", type=int)
    parser.add_argument(
        "--salida",
        type=Path,
        default=CARPETA_DATA,
        help="Carpeta de los CSV de eventos",
    )
    args = parser.parse_args()
    if args.envios <= 0 or args.espera_inicio < 0 or args.espera_final < 0:
        parser.error("Los envíos deben ser positivos y las esperas no pueden ser negativas")
    return args


def main():
    args = argumentos()
    aleatorio = random.Random(args.semilla)
    nodo = NodoGrpc(args.nombre, args.salida)
    servidor = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    communication_pb2_grpc.add_CommunicationServiceServicer_to_server(nodo, servidor)
    puerto = servidor.add_insecure_port(f"127.0.0.1:{NODOS[args.nombre]}")
    if puerto == 0:
        nodo.cerrar()
        raise RuntimeError(f"No se pudo abrir el puerto de {args.nombre}")
    servidor.start()
    print(f"[{args.nombre}] escuchando en el puerto {puerto}", flush=True)

    try:
        time.sleep(args.espera_inicio)
        destinos = [nombre for nombre in NODOS if nombre != args.nombre]
        for _ in range(args.envios):
            nodo.enviar(aleatorio.choice(destinos))
            time.sleep(aleatorio.uniform(0.2, 0.6))
        print(
            f"[{args.nombre}] terminé mis envíos; sigo recibiendo "
            f"{args.espera_final:g} segundos más",
            flush=True,
        )
        time.sleep(args.espera_final)
    finally:
        servidor.stop(grace=2).wait()
        nodo.cerrar()


if __name__ == "__main__":
    main()
