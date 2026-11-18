# Bitácora del equipo MPZ: PE-U1

## Lunes 16/11/2026

- Integrantes presentes: Angel Zambrano
- Qué hicimos: leímos el enunciado de la PE-U1, repartimos las tareas y creamos el repositorio con el README.
- Problemas encontrados: ninguno.

## Martes 17/11/2026

- Integrantes presentes: Angel Zambrano y Steven Pozo
- Qué hicimos: Angel implementó el servidor (nodo-A, puerto 5000) y el cliente (nodo-B) con sockets TCP que se envían un mensaje JSON {sender, timestamp, message} delimitado por salto de línea, y subió el plan de trabajo. Steven definió el servicio gRPC, los mensajes con los campos sender, timestamp, message y lamport_clock, y generó el código Python con grpcio-tools.
- Problemas encontrados: Angel pegó al principio el código Python directamente en cmd y lo resolvió guardándolo en archivos .py. Steven no encontró problemas al definir y generar el contrato gRPC.
