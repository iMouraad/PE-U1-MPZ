"""Mide latencia de ida y vuelta con gRPC y genera los CSV originales.

Uso desde la raíz del repositorio, en dos terminales:
    python src/grpc/latencia.py servidor
    python src/grpc/latencia.py cliente
    python src/grpc/latencia.py concurrente
"""

import argparse
import csv
import platform
import sys
import threading
import time
from concurrent import futures
from datetime import datetime
from pathlib import Path

import grpc


CARPETA_GENERADA = Path(__file__).resolve().parent / "generated"
sys.path.insert(0, str(CARPETA_GENERADA))
import communication_pb2  # noqa: E402
import communication_pb2_grpc  # noqa: E402


HOST = "127.0.0.1"
PUERTO = 50054
ENVIOS = 100
CORRIDAS = 5
TAMANOS = (100, 10_000)
CLIENTES = ("nodo-A", "nodo-B", "nodo-C")
CARPETA_DATA = Path(__file__).resolve().parents[2] / "data"
CAMPOS = [
    "equipo",
    "corrida",
    "modo",
    "bytes_mensaje",
    "id_mensaje",
    "latencia_ms",
    "duracion_corrida_s",
    "calentamiento",
    "cliente",
]


class EcoGrpc(communication_pb2_grpc.CommunicationServiceServicer):
    """Devuelve el mismo contenido recibido para medir una ida y vuelta completa."""

    def ExchangeMessage(self, request, context):
        return communication_pb2.MessageResponse(
            sender=request.sender,
            timestamp=request.timestamp,
            message=request.message,
            lamport_clock=request.lamport_clock,
        )


def armar_solicitud(cliente, identificador, numero, tamano):
    """Construye una solicitud cuyo tamaño protobuf serializado es exacto."""
    solicitud = communication_pb2.MessageRequest(
        sender=cliente,
        timestamp=datetime.now().astimezone().isoformat(timespec="microseconds"),
        message=f"{identificador}|",
        lamport_clock=numero,
    )
    diferencia = tamano - solicitud.ByteSize()
    if diferencia < 0:
        raise ValueError(f"Los metadatos no caben en un mensaje de {tamano} bytes")
    solicitud.message += "x" * diferencia

    while solicitud.ByteSize() != tamano:
        diferencia = tamano - solicitud.ByteSize()
        if diferencia > 0:
            solicitud.message += "x" * diferencia
        else:
            solicitud.message = solicitud.message[:diferencia]
    return solicitud


def medir_cliente(cliente, tamano, corrida, modo, inicio_sincronizado=None):
    """Realiza 100 RPC sobre un canal y devuelve identificadores y latencias."""
    direccion = f"{HOST}:{PUERTO}"
    resultados = []
    with grpc.insecure_channel(direccion) as canal:
        grpc.channel_ready_future(canal).result(timeout=10)
        stub = communication_pb2_grpc.CommunicationServiceStub(canal)
        if inicio_sincronizado is not None:
            inicio_sincronizado.wait(timeout=15)
        for numero in range(1, ENVIOS + 1):
            identificador = (
                f"grpc-{modo}-{tamano}-c{corrida}-{cliente}-{numero:03d}"
            )
            solicitud = armar_solicitud(cliente, identificador, numero, tamano)
            inicio = time.perf_counter_ns()
            respuesta = stub.ExchangeMessage(solicitud, timeout=10)
            fin = time.perf_counter_ns()
            if respuesta.message != solicitud.message or respuesta.ByteSize() != tamano:
                raise RuntimeError("El servidor no devolvió el mensaje protobuf completo")
            resultados.append((identificador, (fin - inicio) / 1_000_000, cliente))
    return resultados


def filas_corrida_secuencial(equipo, tamano, corrida, calentamiento):
    inicio = time.perf_counter()
    resultados = medir_cliente("nodo-B", tamano, corrida, "secuencial")
    duracion = time.perf_counter() - inicio
    return [
        [
            equipo,
            corrida,
            "secuencial",
            tamano,
            identificador,
            f"{latencia:.6f}",
            f"{duracion:.6f}",
            calentamiento,
            cliente,
        ]
        for identificador, latencia, cliente in resultados
    ]


def filas_corrida_concurrente(equipo, tamano, corrida, calentamiento):
    inicio_sincronizado = threading.Barrier(len(CLIENTES) + 1)
    with futures.ThreadPoolExecutor(max_workers=len(CLIENTES)) as ejecutor:
        trabajos = [
            ejecutor.submit(
                medir_cliente,
                cliente,
                tamano,
                corrida,
                "concurrente",
                inicio_sincronizado,
            )
            for cliente in CLIENTES
        ]
        inicio = time.perf_counter()
        inicio_sincronizado.wait(timeout=15)
        resultados = [resultado for trabajo in trabajos for resultado in trabajo.result()]
        duracion = time.perf_counter() - inicio
    return [
        [
            equipo,
            corrida,
            "concurrente",
            tamano,
            identificador,
            f"{latencia:.6f}",
            f"{duracion:.6f}",
            calentamiento,
            cliente,
        ]
        for identificador, latencia, cliente in resultados
    ]


def guardar(nombre, filas):
    CARPETA_DATA.mkdir(exist_ok=True)
    ruta = CARPETA_DATA / nombre
    with ruta.open("w", newline="", encoding="utf-8") as archivo:
        escritor = csv.writer(archivo)
        escritor.writerow(CAMPOS)
        escritor.writerows(filas)
    print(f"Guardado: {ruta} ({len(filas)} filas)")


def servidor():
    servidor_grpc = grpc.server(futures.ThreadPoolExecutor(max_workers=20))
    communication_pb2_grpc.add_CommunicationServiceServicer_to_server(
        EcoGrpc(), servidor_grpc
    )
    puerto = servidor_grpc.add_insecure_port(f"{HOST}:{PUERTO}")
    if puerto == 0:
        raise RuntimeError(f"No se pudo abrir {HOST}:{PUERTO}")
    servidor_grpc.start()
    print(f"Servidor de eco gRPC en {HOST}:{puerto}. Ctrl+C para terminar.")
    try:
        servidor_grpc.wait_for_termination()
    except KeyboardInterrupt:
        servidor_grpc.stop(grace=2).wait()


def cliente():
    equipo = platform.node()
    filas = []
    for tamano in TAMANOS:
        filas.extend(filas_corrida_secuencial(equipo, tamano, 0, 1))
        print(f"secuencial {tamano} B, calentamiento: listo")
        for corrida in range(1, CORRIDAS + 1):
            filas.extend(filas_corrida_secuencial(equipo, tamano, corrida, 0))
            print(f"secuencial {tamano} B, corrida {corrida}: listo")
    guardar("latencias_grpc.csv", filas)


def concurrente():
    equipo = platform.node()
    filas = []
    for tamano in TAMANOS:
        filas.extend(filas_corrida_concurrente(equipo, tamano, 0, 1))
        print(f"concurrente {tamano} B, calentamiento: listo")
        filas.extend(filas_corrida_concurrente(equipo, tamano, 1, 0))
        print(f"concurrente {tamano} B, corrida 1: listo")
    guardar("latencias_grpc_concurrente.csv", filas)


def argumentos():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("modo", choices=("servidor", "cliente", "concurrente"))
    return parser.parse_args()


if __name__ == "__main__":
    modo_elegido = argumentos().modo
    if modo_elegido == "servidor":
        servidor()
    elif modo_elegido == "cliente":
        cliente()
    else:
        concurrente()
