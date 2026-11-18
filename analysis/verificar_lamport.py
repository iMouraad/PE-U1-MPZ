"""Verifica una corrida completa de eventos, con un CSV ordenado por nodo.

Uso desde la raíz del repositorio:
    python analysis/verificar_lamport.py data/eventos_sockets_*.csv

Cada nodo debe empezar con reloj cero. El orden de las filas representa el
orden local de los eventos. Los identificadores de mensaje deben ser únicos
en la corrida. Los archivos originales se abren únicamente para lectura.
"""

import argparse
import csv
from collections import defaultdict
from glob import glob
from itertools import combinations
from pathlib import Path


CAMPOS = {"nodo", "tipo_evento", "reloj", "hora_real", "id_mensaje", "contraparte"}


def leer_eventos(rutas):
    eventos = []
    nodos = set()
    for ruta in rutas:
        with ruta.open(encoding="utf-8-sig", newline="") as archivo:
            lector = csv.DictReader(archivo)
            if not CAMPOS.issubset(lector.fieldnames or []):
                raise ValueError(f"{ruta}: faltan columnas requeridas")
            filas = list(lector)
        if not filas:
            raise ValueError(f"{ruta}: archivo sin eventos")
        nodo = filas[0]["nodo"]
        if nodo in nodos:
            raise ValueError(f"{ruta}: se esperaba un solo archivo por nodo")
        nodos.add(nodo)
        for linea, fila in enumerate(filas, start=2):
            lugar = f"{ruta.name}:{linea}"
            if any(not fila[campo] or not fila[campo].strip() for campo in CAMPOS):
                raise ValueError(f"{lugar}: hay campos vacíos")
            if fila["nodo"] != nodo:
                raise ValueError(f"{lugar}: el archivo contiene varios nodos")
            if fila["tipo_evento"] not in {"envio", "recepcion"}:
                raise ValueError(f"{lugar}: tipo de evento desconocido")
            fila["reloj"] = int(fila["reloj"])
            if fila["reloj"] <= 0:
                raise ValueError(f"{lugar}: el reloj debe ser positivo")
            eventos.append(fila)
    return eventos


def verificar(eventos):
    mensajes = defaultdict(dict)
    locales = defaultdict(list)
    for indice, evento in enumerate(eventos):
        identificador = evento["id_mensaje"]
        tipo = evento["tipo_evento"]
        if tipo in mensajes[identificador]:
            raise ValueError(f"Mensaje {identificador}: {tipo} duplicado")
        mensajes[identificador][tipo] = indice
        locales[evento["nodo"]].append(indice)

    errores = []
    enlaces = defaultdict(set)
    for indices in locales.values():
        for anterior, siguiente in zip(indices, indices[1:]):
            enlaces[anterior].add(siguiente)

    for identificador, pareja in mensajes.items():
        if set(pareja) != {"envio", "recepcion"}:
            errores.append(f"{identificador}: falta envío o recepción")
            continue
        envio = eventos[pareja["envio"]]
        recepcion = eventos[pareja["recepcion"]]
        enlaces[pareja["envio"]].add(pareja["recepcion"])
        if envio["nodo"] != recepcion["contraparte"] or envio["contraparte"] != recepcion["nodo"]:
            errores.append(f"{identificador}: los nodos de envío y recepción no corresponden")
        if recepcion["reloj"] <= envio["reloj"]:
            errores.append(f"{identificador}: reloj de recepción <= reloj de envío")

    for nodo, indices in locales.items():
        local = 0
        for indice in indices:
            evento = eventos[indice]
            esperado = local + 1
            pareja = mensajes[evento["id_mensaje"]]
            if evento["tipo_evento"] == "recepcion":
                if "envio" not in pareja:
                    local = evento["reloj"]
                    continue
                remoto = eventos[pareja["envio"]]["reloj"]
                esperado = max(local, remoto) + 1
            if evento["reloj"] != esperado:
                errores.append(
                    f"{nodo}, {evento['id_mensaje']}, {evento['tipo_evento']}: "
                    f"reloj {evento['reloj']}, esperado {esperado}"
                )
            local = evento["reloj"]
    return mensajes, locales, enlaces, errores


def hay_camino(origen, destino, enlaces):
    pendientes = [origen]
    visitados = set()
    while pendientes:
        actual = pendientes.pop()
        if actual == destino:
            return True
        if actual not in visitados:
            visitados.add(actual)
            pendientes.extend(enlaces[actual])
    return False


def buscar_concurrentes(eventos, enlaces):
    por_reloj = defaultdict(list)
    for indice, evento in enumerate(eventos):
        por_reloj[evento["reloj"]].append(indice)
    for indices in por_reloj.values():
        for primero, segundo in combinations(indices, 2):
            if eventos[primero]["nodo"] == eventos[segundo]["nodo"]:
                continue
            if not hay_camino(primero, segundo, enlaces) and not hay_camino(segundo, primero, enlaces):
                return primero, segundo
    return None


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("csv", nargs="+", help="Archivos o patrones de una misma corrida")
    args = parser.parse_args()
    try:
        rutas = []
        for patron in args.csv:
            coincidencias = sorted(glob(patron))
            if not coincidencias:
                raise ValueError(f"No se encontraron archivos para {patron}")
            rutas.extend(Path(ruta).resolve() for ruta in coincidencias)
        if len(set(rutas)) != len(rutas):
            raise ValueError("Se seleccionó un archivo más de una vez")
        eventos = leer_eventos(rutas)
        mensajes, locales, enlaces, errores = verificar(eventos)
    except (OSError, ValueError, csv.Error) as error:
        parser.exit(1, f"Error: {error}\n")

    print(f"Archivos: {len(rutas)} | Nodos: {len(locales)} | Eventos: {len(eventos)}")
    print(f"Identificadores de mensaje: {len(mensajes)}")
    if errores:
        for error in errores:
            print(f"FALLO: {error}")
        parser.exit(1, f"Verificación fallida: {len(errores)} problema(s).\n")

    print(f"Envío < recepción: {len(mensajes)}/{len(mensajes)}")
    print(f"Reglas locales de Lamport correctas: {len(eventos)}/{len(eventos)}")
    print("id_mensaje | emisor (reloj) -> receptor (reloj)")
    for identificador, pareja in mensajes.items():
        envio = eventos[pareja["envio"]]
        recepcion = eventos[pareja["recepcion"]]
        print(f"{identificador} | {envio['nodo']} ({envio['reloj']}) -> "
              f"{recepcion['nodo']} ({recepcion['reloj']})")

    concurrentes = buscar_concurrentes(eventos, enlaces)
    if concurrentes is None:
        print("Caso concurrente con igual reloj: no encontrado en estos registros.")
    else:
        print("Caso concurrente con igual reloj, según las relaciones registradas:")
        for indice in concurrentes:
            evento = eventos[indice]
            print(f"  {evento['nodo']} | {evento['tipo_evento']} | "
                  f"reloj={evento['reloj']} | {evento['id_mensaje']} | {evento['hora_real']}")
        print("No hay un camino causal entre ambos usando el orden local y los mensajes registrados.")
    print("Verificación completada.")


if __name__ == "__main__":
    main()
