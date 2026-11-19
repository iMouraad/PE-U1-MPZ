# PE-U1: Comunicación entre procesos con sockets TCP y gRPC

Universidad Técnica Estatal de Quevedo · Carrera de Software · Aplicaciones Distribuidas · 7mo nivel, paralelo B

Docente: Ing. Gleiston Cicerón Guerrero Ulloa

Actividad: GA-SUM-02 — PE-U1 — Práctica Experimental Unidad 1: Comunicación entre Procesos Distribuidos con gRPC y Sockets TCP

## Integrantes (equipo MPZ)

- Muñoz Vera Melanie Michelle
- Pozo Castillo Steven Fernando
- Zambrano Yong Angel Daniel

El reparto de tareas está en `PLAN_DE_TRABAJO.md`.

## Estructura del repositorio

| Carpeta | Contenido |
|---|---|
| `src/sockets/` | Nodos con sockets TCP |
| `src/grpc/` | Nodos con gRPC |
| `proto/` | Contrato `.proto` |
| `data/` | CSV de las corridas y `SHA256SUMS` |
| `analysis/` | Script de análisis y gráficos |
| `docs/` | Informe en LaTeX (`.tex`, `.bib` y PDF) |
| `evidencias/` | Capturas originales de las ejecuciones |

## Estado

En revisión. Esta actualización incorpora las pruebas propias de Melanie del 19 de noviembre de 2026, su análisis y la integración al informe. Se conservan separados los resultados preliminares recibidos de los otros equipos de ejecución.

El PDF de una página del SGA ya fue entregado, según confirmación de Melanie. El informe incluye su fila de aportes y la declaración del uso de Codex en su trabajo. Siguen pendientes las filas y declaraciones de los otros integrantes, la revisión de los aportes del grupo, la aplicación al escenario concreto del PFC y el video grupal con su enlace. La revisión de Lamport de gRPC sigue limitada a los eventos de aplicación registrados, sin cubrir el acuse RPC.

## Informe del grupo

El documento integrado está en [docs/informe.pdf](docs/informe.pdf). Su archivo principal es [docs/informe.tex](docs/informe.tex), que incorpora la carátula, hipótesis, arquitectura, implementación del análisis, protocolo, verificación de Lamport de ambos mecanismos, resultados preliminares y pruebas propias de Melanie, amenazas a la validez, discusión y conclusiones. El texto distingue las condiciones previstas de las ejecutadas y señala los pendientes del grupo.

## Análisis de las mediciones recibidas

Los resultados preliminares del 19 de noviembre están en analysis/resultados-2026-11-19/. Para regenerarlos en una carpeta nueva desde la raíz:

```text
python analysis/analizar.py --sockets data/latencias_sockets.csv --sockets-concurrente data/latencias_sockets_concurrente.csv --grpc data/latencias_grpc.csv data/latencias_grpc_concurrente.csv --informe analysis/resultados-revision
```

El lector admite el formato completo de gRPC y el formato nativo de sockets. Si se conoce y documenta el nombre del equipo de sockets, puede indicarse con --equipo-sockets. La duración total ausente en los CSV de sockets deja su rendimiento como N/D. Las figuras mantienen separados los equipos y señalan las condiciones sin datos. La carpeta de salida debe ser nueva.

## Pruebas propias de Melanie — 19 de noviembre de 2026

La sesión se ejecutó como procesos en localhost en el equipo `Melanir`, con usuario `melanir\melanie`. El sistema, CPU, RAM, Python y dependencias están registrados en [data/entorno_melanie.json](data/entorno_melanie.json). Los clientes de medición proceden del commit `cd8f1564ffd1`; sus hashes y las horas de ejecución están en los archivos `sesion.json` de cada mecanismo.

| Ruta | Contenido |
|---|---|
| `data/melanie/2026-11-19/eventos_sockets_nodo-*.csv` | Tres registros originales de eventos TCP |
| `data/melanie/2026-11-19/eventos_grpc_nodo-*.csv` | Tres registros originales de eventos gRPC |
| `data/melanie/2026-11-19/mediciones_sockets/` | Dos CSV originales de latencia TCP, metadatos y resumen para la captura |
| `data/melanie/2026-11-19/mediciones_grpc/` | Dos CSV originales de latencia gRPC, metadatos y resumen para la captura |
| `analysis/resultados-melanie-2026-11-19/` | Resumen, estadísticas por corrida, dos tablas LaTeX y dos gráficos en PNG/PDF |
| `evidencias/melanie/2026-11-19/` | Las seis capturas originales de esta sesión |

Cada mecanismo tiene 4 800 filas de latencia: 800 de calentamiento y 4 000 válidas. El conjunto suma **9 600 filas, 1 600 de calentamiento excluidas y 8 000 mediciones válidas**, en ocho condiciones y 40 corridas válidas. Se usaron solicitudes serializadas de 100 y 10 000 bytes, cinco corridas válidas por tamaño y modo y 100 solicitudes por cliente. El modo concurrente utiliza tres clientes.

Los CSV `resumen_captura.csv` son resultados derivados, no observaciones adicionales. Para el análisis se leen solamente los cuatro archivos de latencia indicados abajo.

### Preparar el entorno y realizar nuevas mediciones

Desde la raíz del repositorio, con Python 3.11 o superior:

```text
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe analysis/medir_equipo.py sockets --salida data/nueva-sesion/mediciones_sockets
.venv\Scripts\python.exe analysis/medir_equipo.py grpc --salida data/nueva-sesion/mediciones_grpc
```

En Linux o macOS se utiliza `.venv/bin/python` en lugar de `.venv\Scripts\python.exe`. Los nombres de salida deben ser nuevos para cada ejecución. El programa rechaza carpetas ya existentes, inicia y cierra su propio servidor de eco y reutiliza las funciones de los clientes originales. Los puertos 5000 (TCP) y 50054 (gRPC) deben estar libres. Las nuevas corridas producirán tiempos diferentes de los de la sesión conservada.

La duración total incluye creación y cierre de conexiones y, en concurrencia, el grupo de hilos. Las latencias individuales mantienen los límites originales: el JSON se prepara antes del cronómetro de sockets y la llamada gRPC incluye la serialización interna. Los mecanismos se ejecutaron en orden sockets–gRPC, sin alternancia. Estas diferencias limitan la atribución de los resultados exclusivamente al transporte.

### Analizar los CSV conservados

Con el entorno Python preparado, ejecutar desde la raíz en una carpeta de salida nueva:

```text
.venv\Scripts\python.exe analysis/analizar.py --sockets data/melanie/2026-11-19/mediciones_sockets/latencias_sockets_secuencial.csv data/melanie/2026-11-19/mediciones_sockets/latencias_sockets_concurrente.csv --grpc data/melanie/2026-11-19/mediciones_grpc/latencias_grpc_secuencial.csv data/melanie/2026-11-19/mediciones_grpc/latencias_grpc_concurrente.csv --informe analysis/resultados-melanie-revision
```

Los cuatro CSV ya identifican su modo, equipo y duración. Se excluye el calentamiento y se calculan media, mediana, desviación estándar muestral y P95 por mensaje. El rendimiento divide los mensajes válidos entre la suma de duraciones, contando cada corrida una sola vez. Las barras muestran la media de las medias de corrida ± una desviación estándar entre corridas; no representan intervalos de confianza.

### Verificar los eventos de Lamport conservados

```text
.venv\Scripts\python.exe analysis/verificar_lamport.py "data/melanie/2026-11-19/eventos_sockets_*.csv"
.venv\Scripts\python.exe analysis/verificar_lamport.py "data/melanie/2026-11-19/eventos_grpc_*.csv"
```

En cada mecanismo se emparejaron 21 mensajes, con 21/21 relaciones envío–recepción y 42/42 actualizaciones locales correctas. El alcance es el de los CSV registrados: la implementación gRPC aún no registra el acuse como evento adicional ni actualiza el reloj del cliente al recibirlo.

Las capturas 01 y 02 son de apoyo porque su encuadre no muestra toda la identificación. Las capturas 03–06 incluyen usuario, máquina, fecha y hora. Se mantienen los archivos originales sin editar.

## Integridad de los CSV

[data/SHA256SUMS](data/SHA256SUMS) contiene los SHA-256 de todos los CSV de `data/`, incluidos sus subdirectorios. Sus rutas se interpretan desde `data/`. Los diez hashes anteriores se comprobaron antes de ampliar el archivo. También se contrastaron los doce CSV de la carpeta de Melanie con las copias originales de su sesión local. Dos de esos doce son los resúmenes derivados para capturas.

`.gitattributes` evita que Git cambie los saltos de línea de los CSV. Los diez archivos anteriores de la raíz de `data/` se conservan con los bytes originales de Git; sus hashes se ajustaron a esa versión, porque Windows había convertido los saltos de línea al descargarlos. Las observaciones no cambian y los CSV nuevos de Melanie conservan exactamente los bytes de la sesión. Se verifica el registro también desde una copia limpia del contenido que se publica.

Para comprobar el registro desde PowerShell, situado en la raíz:

```powershell
Push-Location data
try {
    foreach ($linea in Get-Content -LiteralPath SHA256SUMS) {
        $esperado, $ruta = $linea -split '  ', 2
        $actual = (Get-FileHash -LiteralPath $ruta -Algorithm SHA256).Hash
        if ($actual -ne $esperado) { throw "Hash distinto: $ruta" }
    }
    Write-Host 'Todos los CSV coinciden con SHA256SUMS.'
} finally {
    Pop-Location
}
```

En sistemas con `sha256sum`, ejecutar `sha256sum -c SHA256SUMS` desde `data/`. El registro permite detectar cambios respecto de estos archivos; no reemplaza las capturas y los metadatos de ejecución.

## Compilación del informe

Para compilar la versión actual con pdfLaTeX desde la raíz del repositorio:

```text
cd docs
pdflatex -interaction=nonstopmode -halt-on-error informe.tex
biber informe
pdflatex -interaction=nonstopmode -halt-on-error informe.tex
pdflatex -interaction=nonstopmode -halt-on-error informe.tex
```

Se necesita una distribución LaTeX con fontenc, babel (español), geometry, amsmath, booktabs, tabularx, graphicx, caption, pdflscape, TikZ, listings, csquotes, biblatex con estilo IEEE, Biber e hyperref. La bibliografía se lee desde docs/referencias.bib. La carátula está en docs/caratula.tex; el logo y el diagrama editable, en docs/figuras/. Las capturas se cargan desde evidencias/, las tablas y los gráficos desde las dos carpetas de resultados de analysis/, y los fragmentos de código desde analysis/analizar.py y proto/communication.proto. Debe conservarse toda la estructura de carpetas al compilar.
