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

Informe integrado para revisión final del equipo. Incluye los resultados finales de las pruebas de Melanie, Angel y Steven, con tablas y gráficos separados por máquina, verificación de Lamport, capturas, discusión y conclusiones. Las series preliminares se conservan como antecedentes, separadas de los resultados finales.

El PDF de una página del SGA ya fue entregado, según confirmación de Melanie. El informe incluye las filas de aportes y las declaraciones de uso de IA de los tres integrantes, la aplicación de cada mecanismo al PFC (SGIRI) y las pruebas propias de Melanie (19/11), Steven (21/11) y Angel (22/11). Los datos de Melanie del 19 de noviembre conservan el alcance original sin acuses; la sesión posterior de Steven del 21 de noviembre registra y verifica también cada acuse RPC.

## Video de sustentación

**Enlace al video:**
https://drive.google.com/drive/folders/1GMx0f-AoJvSjrPDstH1bmTkzQ7nI8UI1?usp=drive_link

## Informe del grupo

El documento integrado está en [docs/informe.pdf](docs/informe.pdf). Su archivo principal es [docs/informe.tex](docs/informe.tex), que incorpora la carátula, hipótesis, arquitectura, implementación del análisis, protocolo, verificación de Lamport de ambos mecanismos, resultados finales por equipo, las pruebas propias de Melanie, las nuevas capturas de Angel y Steven, amenazas a la validez, discusión y conclusiones. Se distinguen las series históricas sin acuses de la sesión gRPC actualizada y se documentan las diferencias del protocolo realmente ejecutado.

## Iniciar los tres nodos

En PowerShell, desde la raíz del repositorio, preparar el entorno una vez:

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Abrir tres terminales en esa misma raíz. Cada comando de las tablas siguientes se ejecuta en una terminal distinta. Se realizan siete envíos por nodo: 21 solicitudes en total.

**Sockets TCP.** El programa original guarda sus CSV directamente en `data/`. Para que la demostración no reemplace los registros conservados, copiarlo a una carpeta de sesión nueva antes de iniciarlo:

```powershell
if (Test-Path .sesiones/demo-tcp) { throw 'Usa otro nombre de sesión para conservar los registros anteriores.' }
New-Item -ItemType Directory -Path .sesiones/demo-tcp/src/sockets | Out-Null
Copy-Item src/sockets/nodo.py .sesiones/demo-tcp/src/sockets/nodo.py
```

| Terminal | Comando |
|---|---|
| A | `.venv\Scripts\python.exe -u .sesiones/demo-tcp/src/sockets/nodo.py nodo-A 7` |
| B | `.venv\Scripts\python.exe -u .sesiones/demo-tcp/src/sockets/nodo.py nodo-B 7` |
| C | `.venv\Scripts\python.exe -u .sesiones/demo-tcp/src/sockets/nodo.py nodo-C 7` |

Los puertos 5000, 5001 y 5002 deben estar libres. Esperar a que los tres nodos indiquen que están escuchando y pulsar Enter en las tres terminales, una tras otra. Los nuevos CSV quedan en `.sesiones/demo-tcp/data/`. El proceso conserva cinco segundos de recepción tras sus envíos.

**gRPC.** Los módulos generados de Protocol Buffers ya están incluidos en `src/grpc/generated/`. Preparar una carpeta distinta para sus registros:

```powershell
if (Test-Path .sesiones/demo-grpc) { throw 'Usa otro nombre de sesión para conservar los registros anteriores.' }
New-Item -ItemType Directory -Path .sesiones/demo-grpc | Out-Null
```

| Terminal | Comando |
|---|---|
| A | `.venv\Scripts\python.exe -u src/grpc/nodo.py nodo-A 7 --espera-inicio 30 --espera-final 15 --salida .sesiones/demo-grpc` |
| B | `.venv\Scripts\python.exe -u src/grpc/nodo.py nodo-B 7 --espera-inicio 30 --espera-final 15 --salida .sesiones/demo-grpc` |
| C | `.venv\Scripts\python.exe -u src/grpc/nodo.py nodo-C 7 --espera-inicio 30 --espera-final 15 --salida .sesiones/demo-grpc` |

Iniciar las tres terminales dentro de los primeros 30 segundos para que todos estén escuchando antes de los envíos automáticos. gRPC usa los puertos 50051, 50052 y 50053. Los CSV quedan en `.sesiones/demo-grpc/` y registran tanto las solicitudes como sus acuses. Estos comandos ejecutan los intercambios de Lamport; las mediciones de latencia se realizan con `analysis/medir_equipo.py`, como se indica más abajo.

En Linux o macOS se utiliza `.venv/bin/python` y las operaciones equivalentes de creación y copia de carpetas. Para repetir la demostración, cambiar los nombres de ambas carpetas de sesión en todos los comandos.

## Análisis de las mediciones recibidas

La integración final de los tres equipos está en `analysis/resultados-finales-2026-11-22/`, con subcarpetas por integrante. Reúne 61 200 filas originales, 10 200 de calentamiento excluidas y 51 000 mediciones válidas en 120 corridas. No se promedian máquinas distintas. Los CSV fuente se enumeran en `sesiones.json`, las cantidades en `inventario.csv` y la verificación de las cinco sesiones de eventos en `lamport.csv`. Los originales se conservan sin editar.

Para regenerar todas las tablas y figuras finales desde la raíz, usando una carpeta de salida nueva:

```text
python analysis/integrar_sesiones.py --salida analysis/resultados-finales-revision
```

Este programa comprueba los hashes, reutiliza `analizar.py` y `verificar_lamport.py` y genera el inventario, los resultados por equipo y las tablas de Lamport. Todas las condiciones tienen cinco corridas válidas. Para gRPC concurrente de Steven selecciona la sesión del 22/11: 1 000 envíos por cliente y corrida frente a 100 en el resto, con preparación y cierre de clientes incluidos. Las figuras identifican las cargas distintas y el informe no atribuye sus diferencias de rendimiento solo al transporte. La serie anterior de una corrida por tamaño se conserva como antecedente y no se suma al conjunto final. La serie gRPC con acuses del 21/11 verifica 42 relaciones y 84 eventos; las series históricas mantienen su alcance original.

### Series preliminares conservadas

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

En cada mecanismo se emparejaron 21 mensajes, con 21/21 relaciones envío–recepción y 42/42 actualizaciones locales correctas. El alcance es el de los CSV históricos de Melanie: la versión gRPC usada el 19/11 no registraba el acuse como evento adicional ni actualizaba el reloj del cliente al recibirlo; la sesión posterior de Steven sí cubre ambos eventos.

Las capturas 01 y 02 son de apoyo porque su encuadre no muestra toda la identificación. Las capturas 03–06 incluyen usuario, máquina, fecha y hora. Se mantienen los archivos originales sin editar.

## Pruebas propias de Steven — 21 de noviembre de 2026

Steven ejecutó en `DESKTOP-5MJCPHU`, con Python 3.12.10, las mediciones de sockets y una nueva sesión de eventos gRPC. El entorno, las horas, los parámetros y el hash del código de medición constan en `data/steven/2026-11-21/mediciones_sockets/sesion.json`.

| Ruta | Contenido |
|---|---|
| `data/steven/2026-11-21/mediciones_sockets/` | CSV originales secuencial y concurrente, metadatos y log del servidor |
| `data/steven/2026-11-21/eventos_grpc_ack/` | Tres CSV de eventos gRPC con solicitudes y acuses registrados |
| `evidencias/steven/2026-11-21/terminal-lamport.png` | Captura directa de PowerShell con identificación y verificación |

Sockets contiene 1 200 filas secuenciales (1 000 válidas y 200 de calentamiento) y 3 600 concurrentes (3 000 válidas y 600 de calentamiento). Para cada tamaño serializado, 100 y 10 000 bytes, se ejecutó una corrida de calentamiento descartada y cinco corridas válidas de 100 envíos; en modo concurrente participaron tres clientes con 100 envíos cada uno por corrida.

La implementación gRPC registra el envío y la recepción del acuse con un identificador terminado en `-ack`; el cliente aplica `max(reloj_local, reloj_recibido) + 1`. En la sesión conservada, tres nodos realizaron siete solicitudes cada uno. El verificador comprobó 84 eventos, 42 relaciones causales —21 solicitudes y 21 acuses—, 42/42 casos de envío anterior a recepción y 84/84 reglas locales de Lamport.

Para repetir la verificación desde la raíz:

```text
python analysis/verificar_lamport.py "data/steven/2026-11-21/eventos_grpc_ack/eventos_grpc_*.csv"
```

### Nueva prueba gRPC concurrente de Steven — 22 de noviembre de 2026

La carpeta `data/steven/2026-11-22/mediciones_grpc_concurrente_1000/`
conserva una sesión nueva con tres clientes simultáneos. Para cada tamaño
serializado, 100 y 10 000 bytes, se descartó una corrida de calentamiento y
se realizaron cinco corridas válidas de 1 000 envíos por cliente. El CSV
contiene 36 000 filas: 30 000 válidas y 6 000 de calentamiento. `sesion.json`
registra el equipo, Python, horas, parámetros, comando y hash de la fuente;
`servidor.log` conserva la salida original del servidor. La captura directa
`evidencias/steven/2026-11-22/grpc-concurrente-1000.png` muestra usuario,
equipo, fecha, hora, conteos por cliente y el SHA-256 del CSV.

La sesión se ejecutó con:

```text
python analysis/medir_equipo.py grpc --salida data/steven/2026-11-22/mediciones_grpc_concurrente_1000 --repeticiones 5 --envios 1000 --modos concurrente
```

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
