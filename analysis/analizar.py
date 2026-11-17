"""Resume mediciones de sockets TCP y gRPC sin modificar los CSV originales.

Cada fila representa un mensaje completado. Columnas requeridas:
equipo,corrida,modo,bytes_mensaje,id_mensaje,latencia_ms,duracion_corrida_s,calentamiento

modo: secuencial o concurrente. calentamiento: 0 o 1.
duracion_corrida_s: tiempo total de la corrida, repetido en sus filas.
En una corrida concurrente, medirlo desde antes de lanzar los envíos hasta
que finalice el último cliente, una sola vez para los tres clientes.
El id_mensaje debe ser único dentro de la corrida, incluso entre clientes.
"""

import argparse
from pathlib import Path

import numpy as np
import pandas as pd


GRUPO = ["mecanismo", "equipo", "modo", "bytes_mensaje"]
CORRIDA = [*GRUPO, "corrida"]
COLUMNAS = [
    "equipo", "corrida", "modo", "bytes_mensaje", "id_mensaje",
    "latencia_ms", "duracion_corrida_s", "calentamiento",
]


def leer_csv(ruta, mecanismo):
    """Carga un CSV y verifica que las unidades y etiquetas sean utilizables."""
    datos = pd.read_csv(ruta, dtype="string", encoding="utf-8-sig")
    faltantes = sorted(set(COLUMNAS) - set(datos.columns))
    if faltantes:
        raise ValueError(f"{ruta}: faltan columnas: {', '.join(faltantes)}")

    datos = datos.loc[:, COLUMNAS].apply(lambda columna: columna.str.strip())
    if datos.empty or datos.isna().any().any() or datos.eq("").any().any():
        raise ValueError(f"{ruta}: el CSV está vacío o tiene campos vacíos")
    if not datos["modo"].isin(["secuencial", "concurrente"]).all():
        raise ValueError(f"{ruta}: modo debe ser secuencial o concurrente")
    if not datos["calentamiento"].isin(["0", "1"]).all():
        raise ValueError(f"{ruta}: calentamiento debe ser 0 o 1")

    for columna in ("bytes_mensaje", "latencia_ms", "duracion_corrida_s"):
        valores = pd.to_numeric(datos[columna], errors="coerce").astype(float)
        if not np.isfinite(valores).all() or not (valores > 0).all():
            raise ValueError(f"{ruta}: {columna} debe contener números positivos y finitos")
        datos[columna] = valores

    tamanos = datos["bytes_mensaje"]
    if not tamanos.mod(1).eq(0).all():
        raise ValueError(f"{ruta}: bytes_mensaje debe contener números enteros")
    datos["bytes_mensaje"] = tamanos.astype("int64")
    return datos.assign(mecanismo=mecanismo)


def resumir(datos):
    """Calcula la latencia por mensaje y el rendimiento por tiempo de corrida."""
    if datos.duplicated([*CORRIDA, "id_mensaje"]).any():
        raise ValueError("Hay identificadores de mensaje duplicados en una corrida")

    metadatos = datos.groupby(CORRIDA)[["duracion_corrida_s", "calentamiento"]]
    if metadatos.nunique().gt(1).any().any():
        raise ValueError("Hay corridas con duración o etiqueta de calentamiento inconsistente")
    mediciones = datos.loc[datos["calentamiento"].eq("0")]
    if set(mediciones["mecanismo"]) != {"sockets", "grpc"}:
        raise ValueError("Se necesitan mediciones válidas de sockets y gRPC tras el calentamiento")

    latencias = mediciones.groupby(GRUPO)["latencia_ms"].agg(
        mensajes="size",
        media_ms="mean",
        mediana_ms="median",
        desviacion_ms="std",
        p95_ms=lambda valores: valores.quantile(0.95),
    )
    corridas = (
        mediciones.groupby(CORRIDA)["duracion_corrida_s"]
        .first()
        .groupby(level=GRUPO)
        .agg(corridas="size", duracion_total_s="sum")
    )
    resumen = latencias.join(corridas)
    resumen["mensajes_por_segundo"] = resumen["mensajes"] / resumen["duracion_total_s"]
    return resumen.reset_index()


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--sockets", nargs="+", type=Path, required=True)
    parser.add_argument("--grpc", nargs="+", type=Path, required=True)
    parser.add_argument("--salida", type=Path, help="Ruta opcional para un CSV nuevo con el resumen")
    args = parser.parse_args()

    entradas = [(ruta, "sockets") for ruta in args.sockets]
    entradas += [(ruta, "grpc") for ruta in args.grpc]
    try:
        mediciones = pd.concat(
            [leer_csv(ruta, mecanismo) for ruta, mecanismo in entradas], ignore_index=True
        )
        resumen = resumir(mediciones)
        if args.salida is not None:
            with args.salida.open("x", encoding="utf-8", newline="") as archivo:
                resumen.to_csv(archivo, index=False)
    except (OSError, ValueError) as error:
        parser.exit(1, f"Error: {error}\n")

    print(resumen.to_string(index=False, float_format=lambda valor: f"{valor:.4f}", na_rep="N/D"))


if __name__ == "__main__":
    main()
