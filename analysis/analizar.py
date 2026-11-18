"""Resume mediciones de sockets TCP y gRPC sin modificar los CSV originales.

Cada fila representa un mensaje completado. Columnas requeridas:
equipo,corrida,modo,bytes_mensaje,id_mensaje,latencia_ms,duracion_corrida_s,calentamiento

modo: secuencial o concurrente. calentamiento: 0 o 1.
duracion_corrida_s: tiempo total de la corrida, repetido en sus filas.
En una corrida concurrente, medirlo desde antes de lanzar los envíos hasta
que finalice el último cliente, una sola vez para los tres clientes.
El id_mensaje debe ser único dentro de la corrida, incluso entre clientes.

--informe genera tablas LaTeX (booktabs y graphicx), CSV y figuras PNG/PDF.
Las barras representan la media de las medias por corrida; los intervalos
son ± una desviación estándar muestral entre esas medias.
--ejemplo identifica las salidas visuales de una prueba con datos sintéticos.
"""

import argparse
from pathlib import Path
import re
from tempfile import TemporaryDirectory

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


def resumen_corridas(datos):
    """Separa la variabilidad entre corridas de la variabilidad entre mensajes."""
    mediciones = datos.loc[datos["calentamiento"].eq("0")]
    corridas = mediciones.groupby(CORRIDA).agg(
        mensajes=("latencia_ms", "size"),
        media_ms=("latencia_ms", "mean"),
        duracion_s=("duracion_corrida_s", "first"),
    )
    corridas["mensajes_por_segundo"] = corridas["mensajes"] / corridas["duracion_s"]
    return corridas.reset_index()


def texto_latex(valor):
    caracteres = {
        "\\": r"\textbackslash{}", "&": r"\&", "%": r"\%", "$": r"\$",
        "#": r"\#", "_": r"\_", "{": r"\{", "}": r"\}",
        "~": r"\textasciitilde{}", "^": r"\textasciicircum{}",
    }
    return re.sub(r"[\\&%$#_{}~^]", lambda match: caracteres[match.group()], str(valor))


def escribir_tabla(ruta, datos, columnas, titulo):
    """Escribe un fragmento LaTeX para un informe con booktabs y graphicx."""
    lineas = [
        r"\begin{table}[htbp]", r"\centering", r"\small",
        r"\caption{" + texto_latex(titulo) + "}",
        r"\resizebox{\linewidth}{!}{%",
        r"\begin{tabular}{" + "l" * 4 + "r" * (len(columnas) - 4) + "}",
        r"\toprule",
        " & ".join(texto_latex(etiqueta) for etiqueta in columnas.values()) + r" \\",
        r"\midrule",
    ]
    for fila in datos[list(columnas)].itertuples(index=False, name=None):
        valores = []
        for valor in fila:
            if isinstance(valor, float):
                valores.append(f"{valor:.4f}" if np.isfinite(valor) else "N/D")
            else:
                valores.append(texto_latex(valor))
        lineas.append(" & ".join(valores) + r" \\")
    lineas.extend([r"\bottomrule", r"\end{tabular}", "}", r"\end{table}"])
    ruta.write_text("\n".join(lineas) + "\n", encoding="utf-8")


def exportar_informe(datos, resumen, destino, ejemplo=False):
    """Publica un directorio nuevo cuando todas las tablas y figuras están listas."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    if destino.exists():
        raise ValueError(f"La carpeta de resultados ya existe: {destino}")
    corridas = resumen_corridas(datos)
    condiciones = resumen[["equipo", "modo", "bytes_mensaje"]].drop_duplicates()
    colores = {"sockets": "#2878A0", "grpc": "#D88232"}
    etiqueta = "DATOS SINTÉTICOS DE PRUEBA" if ejemplo else "Mediciones experimentales"

    with TemporaryDirectory(prefix="analisis-", dir=destino.parent) as temporal:
        carpeta = Path(temporal) / "resultados"
        carpeta.mkdir()
        resumen.to_csv(carpeta / "resumen.csv", index=False)
        corridas.to_csv(carpeta / "por_corrida.csv", index=False)
        base = {"equipo": "Equipo", "modo": "Modo", "bytes_mensaje": "Bytes", "mecanismo": "Mecanismo"}
        escribir_tabla(
            carpeta / "tabla_latencias.tex", resumen,
            {**base, "media_ms": "Media", "mediana_ms": "Mediana",
             "desviacion_ms": "Desv.", "p95_ms": "P95"},
            f"{etiqueta}. Latencias en milisegundos; desviación estándar muestral por mensaje.",
        )
        escribir_tabla(
            carpeta / "tabla_rendimiento.tex", resumen,
            {**base, "mensajes": "Mensajes", "corridas": "Corridas",
             "duracion_total_s": "Tiempo (s)", "mensajes_por_segundo": "Mensajes/s"},
            f"{etiqueta}. Rendimiento agregado: mensajes completados / tiempo total de corridas.",
        )
        # Cada panel mantiene separados el equipo, el modo y el tamaño.
        for nombre in ("cajas_latencias", "barras_latencias"):
            columnas = min(2, len(condiciones))
            filas = (len(condiciones) + columnas - 1) // columnas
            fig, ejes = plt.subplots(filas, columnas, figsize=(6 * columnas, 3.8 * filas), squeeze=False)
            for eje, condicion in zip(ejes.flat, condiciones.itertuples(index=False)):
                mascara = (
                    datos["equipo"].eq(condicion.equipo)
                    & datos["modo"].eq(condicion.modo)
                    & datos["bytes_mensaje"].eq(condicion.bytes_mensaje)
                    & datos["calentamiento"].eq("0")
                )
                seleccion = datos.loc[mascara]
                for posicion, mecanismo in enumerate(colores):
                    valores = seleccion.loc[seleccion["mecanismo"].eq(mecanismo), "latencia_ms"]
                    if valores.empty:
                        continue
                    if nombre == "cajas_latencias":
                        caja = eje.boxplot([valores], positions=[posicion], widths=0.5, patch_artist=True)
                        caja["boxes"][0].set_facecolor(colores[mecanismo])
                    else:
                        muestras = corridas.loc[
                            corridas["equipo"].eq(condicion.equipo)
                            & corridas["modo"].eq(condicion.modo)
                            & corridas["bytes_mensaje"].eq(condicion.bytes_mensaje)
                            & corridas["mecanismo"].eq(mecanismo), "media_ms"
                        ]
                        eje.bar(posicion, muestras.mean(), color=colores[mecanismo], width=0.55)
                        if len(muestras) > 1:
                            eje.errorbar(posicion, muestras.mean(), yerr=muestras.std(ddof=1),
                                         color="#263343", capsize=5, fmt="none")
                        eje.text(posicion, muestras.mean(), f"  n={len(muestras)}",
                                 ha="left", va="bottom", fontsize=9)
                eje.set_xticks([0, 1], ["Sockets TCP", "gRPC"])
                eje.set_title(f"{condicion.equipo} · {condicion.modo} · {condicion.bytes_mensaje} B")
                eje.set_ylabel("Latencia RTT (ms)")
                eje.grid(axis="y", alpha=0.2)
                eje.set_axisbelow(True)
                eje.set_ylim(bottom=0)
            for eje in list(ejes.flat)[len(condiciones):]:
                eje.set_visible(False)
            subtitulo = "Distribución por mensaje" if nombre == "cajas_latencias" else "Media por corrida ± 1 desviación estándar entre corridas"
            fig.suptitle(f"{etiqueta}\n{subtitulo}", fontsize=14)
            nota = (
                "Cajas: Q1–Q3; línea: mediana; bigotes: hasta 1,5 × RIQ; puntos: valores atípicos."
                if nombre == "cajas_latencias"
                else "n = corridas válidas; con una sola corrida se omite la barra de error. No es un intervalo de confianza."
            )
            fig.text(0.5, 0.015, nota, ha="center", fontsize=9)
            fig.tight_layout(rect=(0, 0.05, 1, 0.92))
            try:
                fig.savefig(carpeta / f"{nombre}.png", dpi=160)
                fig.savefig(carpeta / f"{nombre}.pdf")
            finally:
                plt.close(fig)
        carpeta.rename(destino)


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--sockets", nargs="+", type=Path, required=True)
    parser.add_argument("--grpc", nargs="+", type=Path, required=True)
    parser.add_argument("--salida", type=Path, help="Ruta opcional para un CSV nuevo con el resumen")
    parser.add_argument("--informe", type=Path, help="Carpeta nueva para tablas, CSV y gráficos")
    parser.add_argument("--ejemplo", action="store_true", help="Marca tablas y figuras como datos sintéticos de prueba")
    args = parser.parse_args()

    entradas = [(ruta, "sockets") for ruta in args.sockets]
    entradas += [(ruta, "grpc") for ruta in args.grpc]
    try:
        mediciones = pd.concat(
            [leer_csv(ruta, mecanismo) for ruta, mecanismo in entradas], ignore_index=True
        )
        resumen = resumir(mediciones)
        if args.informe is not None:
            exportar_informe(mediciones, resumen, args.informe, args.ejemplo)
        if args.salida is not None:
            with args.salida.open("x", encoding="utf-8", newline="") as archivo:
                resumen.to_csv(archivo, index=False)
    except (OSError, ValueError) as error:
        parser.exit(1, f"Error: {error}\n")

    print(resumen.to_string(index=False, float_format=lambda valor: f"{valor:.4f}", na_rep="N/D"))


if __name__ == "__main__":
    main()
