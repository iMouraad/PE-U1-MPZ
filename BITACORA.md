# Bitácora del equipo MPZ: PE-U1

## Lunes 16/11/2026

- Integrantes presentes: Angel Zambrano
- Qué hicimos: leímos el enunciado de la PE-U1, repartimos las tareas y creamos el repositorio con el README.
- Problemas encontrados: ninguno.

## Martes 17/11/2026

- Integrantes presentes: Angel Zambrano y Steven Pozo
- Qué hicimos: Angel implementó el servidor (nodo-A, puerto 5000) y el cliente (nodo-B) con sockets TCP que se envían un mensaje JSON {sender, timestamp, message} delimitado por salto de línea, y subió el plan de trabajo. Steven definió el servicio gRPC, los mensajes con los campos sender, timestamp, message y lamport_clock, y generó el código Python con grpcio-tools.
- Problemas encontrados: Angel pegó al principio el código Python directamente en cmd y lo resolvió guardándolo en archivos .py. Steven no encontró problemas al definir y generar el contrato gRPC.

## Miércoles 18/11/2026

- Integrantes presentes: Angel Zambrano
- Qué hicimos: nodo.py, un solo programa para los tres nodos (nodo-A en el puerto 5000, nodo-B en el 5001 y nodo-C en el 5002). Cada nodo escucha en un hilo y al mismo tiempo envía mensajes a los otros dos. Agregamos el reloj de Lamport: sube en 1 antes de cada envío y al recibir toma max(local, recibido) + 1. Corrimos los tres nodos con 7 envíos cada uno (21 mensajes) y guardamos los eventos en data/eventos_sockets_nodo-A.csv, nodo-B.csv y nodo-C.csv, con las columnas nodo, tipo_evento, reloj, hora_real, id_mensaje y contraparte.
- Problemas encontrados:
  - En la primera corrida el nodo-C se cayó con ConnectionRefusedError porque el nodo-A ya había terminado y cerrado su puerto. Lo resolvimos con 3 reintentos por envío y 20 segundos de espera antes de cerrar cada nodo.
  - En la segunda corrida al nodo-A no se le dio Enter y solo hubo 14 mensajes. Repetimos la corrida presionando Enter en los tres nodos.
  - En PowerShell el comando whoami & hostname daba error porque ahí se separa con punto y coma. En cmd se usa &.
