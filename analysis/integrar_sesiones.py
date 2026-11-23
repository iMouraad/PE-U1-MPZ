"""Regenera las tablas y figuras finales sin modificar los CSV originales.

Desde la raíz: python analysis/integrar_sesiones.py --salida analysis/resultados-finales-revision
La carpeta de salida debe ser nueva. Las series se conservan separadas por equipo.
"""

import argparse
import csv
import hashlib
import json
from pathlib import Path

import pandas as pd

import analizar
import verificar_lamport as lamport


RAIZ = Path(__file__).resolve().parents[1]
SESIONES = {
    "angel": {"equipo": "Mourad", "fecha": "22/11/2026", "base": "data/angel/2026-11-22"},
    "steven": {"equipo": "DESKTOP-5MJCPHU", "fecha": "19, 21 y 22/11/2026", "base": "data/steven/2026-11-21"},
    "melanie": {"equipo": "Melanir", "fecha": "19/11/2026", "base": "data/melanie/2026-11-19"},
}


def entradas(persona, sesion):
    base = Path(sesion["base"])
    return [
        (base / "mediciones_sockets/latencias_sockets_secuencial.csv", "sockets"),
        (base / "mediciones_sockets/latencias_sockets_concurrente.csv", "sockets"),
        (Path("data/latencias_grpc.csv") if persona == "steven" else base / "mediciones_grpc/latencias_grpc_secuencial.csv", "grpc"),
        (Path("data/steven/2026-11-22/mediciones_grpc_concurrente_1000/latencias_grpc_concurrente.csv") if persona == "steven" else base / "mediciones_grpc/latencias_grpc_concurrente.csv", "grpc"),
    ]


def guardar_csv(ruta, filas):
    with ruta.open("x", newline="", encoding="utf-8") as archivo:
        escritor = csv.DictWriter(archivo, fieldnames=list(filas[0]))
        escritor.writeheader()
        escritor.writerows(filas)


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--salida", type=Path, required=True)
    args = parser.parse_args()
    salida = args.salida.resolve()
    if salida.exists():
        parser.error("La carpeta de salida debe ser nueva")
    for linea in (RAIZ / "data/SHA256SUMS").read_text(encoding="utf-8").splitlines():
        esperado, nombre = linea.split("  ", 1)
        actual = hashlib.sha256((RAIZ / "data" / nombre).read_bytes()).hexdigest()
        if esperado != actual:
            raise ValueError(f"Hash distinto: {nombre}")
    salida.mkdir(parents=True)
    inventario = []
    origenes = {}
    for persona, sesion in SESIONES.items():
        partes = []
        origenes[persona] = []
        for archivo, mecanismo in entradas(persona, sesion):
            datos = analizar.leer_csv(RAIZ / archivo, mecanismo)
            if set(datos.equipo) != {sesion["equipo"]}:
                raise ValueError(f"Equipo inesperado en {archivo}")
            partes.append(datos)
            origenes[persona].append(archivo.as_posix())
        datos = pd.concat(partes, ignore_index=True)
        validos = datos.loc[datos.calentamiento.eq("0")]
        resumen = analizar.resumir(datos)
        analizar.exportar_informe(datos, resumen, salida / persona, False)
        inventario.append({
            "integrante": persona, "equipo": sesion["equipo"], "fecha": sesion["fecha"],
            "filas_originales": len(datos), "calentamiento": int(datos.calentamiento.eq("1").sum()),
            "validas": len(validos), "condiciones": len(resumen), "corridas_validas": int(resumen.corridas.sum()),
        })
    guardar_csv(salida / "inventario.csv", inventario)
    with (salida / "sesiones.json").open("x", encoding="utf-8") as f:
        json.dump(origenes, f, ensure_ascii=False, indent=2)
        f.write("\n")
    filas = []
    series = [
        ("TCP inicial", "18/11", "data/eventos_sockets_*.csv"),
        ("gRPC inicial", "18/11", "data/eventos_grpc_*.csv"),
        ("TCP Melanir", "19/11", "data/melanie/2026-11-19/eventos_sockets_*.csv"),
        ("gRPC Melanir", "19/11", "data/melanie/2026-11-19/eventos_grpc_*.csv"),
        ("gRPC con acuses", "21/11", "data/steven/2026-11-21/eventos_grpc_ack/eventos_grpc_*.csv"),
    ]
    concurrentes = []
    for nombre, fecha, patron in series:
        rutas = sorted(RAIZ.glob(patron))
        if len(rutas) != 3:
            raise ValueError(f"Se esperaban tres archivos: {patron}")
        eventos = lamport.leer_eventos(rutas)
        mensajes, locales, enlaces, errores = lamport.verificar(eventos)
        if errores:
            raise ValueError(str(errores))
        filas.append({"serie": nombre, "fecha": fecha, "relaciones": len(mensajes), "eventos": len(eventos), "actualizaciones_correctas": len(eventos)})
        par = lamport.buscar_concurrentes(eventos, enlaces)
        if par is not None:
            for indice in par:
                concurrentes.append({"serie": nombre, **eventos[indice]})
    guardar_csv(salida / "lamport.csv", filas)
    guardar_csv(salida / "concurrentes.csv", concurrentes)
    def tabla(ruta, titulo, cabecera, alineacion, cuerpo):
        contenido = [r"\begin{table}[htbp]\centering\small", r"\caption{" + titulo + "}",
                     r"\begin{tabular}{" + alineacion + "}", r"\toprule", cabecera + r" \\", r"\midrule"]
        contenido.extend(" & ".join(str(v) for v in fila) + r" \\" for fila in cuerpo)
        contenido.extend([r"\bottomrule", r"\end{tabular}", r"\end{table}"])
        ruta.write_text("\n".join(contenido) + "\n", encoding="utf-8")
    tabla(salida / "tabla_inventario.tex", "Series de latencia incluidas en la integración final.",
          "Equipo & Filas & Calentamiento & Válidas & Corridas", "lrrrr",
          [(i["equipo"], i["filas_originales"], i["calentamiento"], i["validas"], i["corridas_validas"]) for i in inventario])
    tabla(salida / "tabla_lamport.tex", "Verificación de cada corrida de eventos, sin mezclar sesiones.",
          "Serie & Fecha & Relaciones & Eventos & Reglas correctas", "llrrr",
          [(i["serie"], i["fecha"], i["relaciones"], i["eventos"], i["actualizaciones_correctas"]) for i in filas])
    print(pd.DataFrame(inventario).to_string(index=False))
    print("Totales:", {c: sum(i[c] for i in inventario) for c in ["filas_originales", "calentamiento", "validas", "condiciones", "corridas_validas"]})


if __name__ == "__main__":
    main()
