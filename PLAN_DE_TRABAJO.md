# Plan de trabajo: PE-U1 (GA-SUM-01)

Práctica Experimental de la Unidad 1: comunicación entre procesos con sockets TCP y gRPC.
Equipo MPZ · Aplicaciones Distribuidas · 7mo nivel, paralelo B · Cierre: domingo 22 de noviembre de 2026, 23:55.

## Reparto de tareas

| Integrante | Responsable de | Carpeta principal |
|---|---|---|
| Zambrano Yong Angel Daniel | Nodos con sockets TCP: servidor y clientes, mensajes JSON `{sender, timestamp, message}`, reloj de Lamport, 20 intercambios y 100 mediciones de latencia | `src/sockets/` |
| Pozo Castillo Steven Fernando | Nodos con gRPC: archivo `.proto`, código generado con grpcio-tools, reloj de Lamport, los mismos 20 intercambios y 100 mediciones | `proto/`, `src/grpc/` |
| Muñoz Vera Melanie Michelle | Script de análisis (media, mediana, desviación, percentil 95, mensajes por segundo), gráficos, verificación del reloj de Lamport e integración del informe en LaTeX | `analysis/`, `docs/` |

Tareas de los tres:

- Correr el protocolo experimental en su propio equipo: 5 repeticiones de 100 envíos por mecanismo, una corrida de calentamiento descartada, mensajes de 100 bytes y de 10 KB, y una prueba con los tres clientes a la vez.
- Tomar al menos una captura en su propio equipo con usuario, nombre de la máquina, fecha y hora visibles.
- Hacer como mínimo 3 commits significativos de código o de análisis, en días distintos.
- Redactar en el informe la parte que le corresponde y escribir su fila en la tabla de aportes.
- Aparecer en el video de 3 a 5 minutos.
- Poder explicar y modificar cualquier parte del código en la demostración en clase.

## Calendario

| Día | Angel | Steven | Melanie |
|---|---|---|---|
| Lunes 16 | Estructura del repositorio, plan, README, bitácora | | |
| Martes 17 | Servidor y cliente TCP que se envían un mensaje JSON | Archivo `.proto` y código generado | `requirements.txt` con versiones fijas y la hipótesis del informe |
| Miércoles 18 | Tres nodos con reloj de Lamport y registro de eventos en CSV | Tres nodos gRPC con reloj de Lamport y CSV | Lectura de los CSV y cálculo de estadísticas |
| Jueves 19 | Medición de latencia: 100 envíos, 5 repeticiones, dos tamaños, prueba concurrente | Lo mismo con gRPC | Gráficos y verificación de Lamport con los datos reales |
| Viernes 20 | Corrida final y `SHA256SUMS` | Corrida final | Tablas generadas por el script e informe |
| Sábado 21 | Capturas, video y secciones del informe | Capturas, video y secciones del informe | Integración del informe y compilación |
| Domingo 22 | Revisión final del repositorio, README y PDF de una página para el SGA | | |

## Reglas que acordamos

- Cada uno sube su propio trabajo desde su cuenta de GitHub, con mensajes de commit escritos por él.
- Nadie edita a mano los CSV ni los resultados. Si una corrida sale mal, se repite.
- Todo lo del día se sube ese mismo día y se anota en `BITACORA.md`.
