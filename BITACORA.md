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

### Martes 17/11/2026 — Sesión de Melanie

- **Integrante:** Melanie Muñoz.
- **Qué hicimos:** definí las dependencias en `requirements.txt`, redacté el objetivo y la hipótesis en `docs/hipotesis.tex` y estructuré `analysis/analizar.py` para calcular métricas de latencia y rendimiento, descartando el calentamiento y agrupando por mecanismo, equipo, tamaño y modo. Comprobé el entorno en Python 3.14 y la compilación del fragmento.
- **Verificación:** probé el script con datos sintéticos temporales para validar los cálculos antes de contar con las mediciones reales.
- **Aportes publicados:** dependencias, hipótesis y script de análisis.
- **Problemas encontrados y solución:** aún no estaban disponibles los CSV experimentales, por lo que trabajé con un formato provisional sujeto a ajuste con los datos reales de sockets y gRPC.

## Miércoles 18/11/2026 — Sesión de Steven

- Integrante: Steven Pozo.
- Qué hicimos: implementamos un único programa para ejecutar nodo-A, nodo-B y nodo-C mediante gRPC en los puertos 50051, 50052 y 50053. Cada nodo funciona como servidor y cliente, incrementa su reloj de Lamport antes de enviar y al recibir aplica max(local, recibido) + 1.
- Corrida: ejecutamos los tres nodos con 7 envíos cada uno y registramos automáticamente los eventos en data/eventos_grpc_nodo-A.csv, nodo-B.csv y nodo-C.csv, usando el mismo formato de los registros de sockets.
- Verificación: comprobamos los CSV con analysis/verificar_lamport.py para emparejar cada envío con su recepción y validar las actualizaciones del reloj lógico.
- Entorno: registramos en data/readme.md el sistema operativo, procesador, RAM, versiones de Python y gRPC, y los comandos utilizados.
- Pendiente: realizar las corridas de latencia de 100 bytes y 10 KB, incluida la prueba concurrente, según el protocolo experimental.

### Miércoles 18/11/2026 — Sesión de Melanie
- **Integrante:** Melanie Muñoz.
- **Qué hicimos:** revisé los archivos del equipo y desarrollé `analysis/verificar_lamport.py` para validar los CSV reales de sockets emparejando envíos y recepciones por `id_mensaje`, contrapartes y reglas del reloj de Lamport.
- **Resultados:** los tres archivos contienen 42 eventos y 21 mensajes completos. Los 21 mensajes cumplen reloj de recepción mayor que reloj de envío y las 42 actualizaciones cumplen las reglas de Lamport.
- **Concurrencia:** identifiqué el envío de `cf648d87` en `nodo-A` y la recepción de `a5cbb3c7` en `nodo-B`, ambos con reloj 2, sin camino causal entre ellos en esta corrida.
- **Verificación:** comprobé el verificador con los registros reales y con copias temporales alteradas para detectar fallos sin alterar los originales ni sus hashes SHA-256.
- **Evidencia:** ejecuté el verificador en PowerShell en mi equipo Melanir y obtuve la captura original (usuario `melanir\melanie`, fecha y hora del sistema y resultados completos). Se incorporan el verificador, la captura y esta bitácora.
- **Pendiente:** recibir las mediciones de latencia de sockets y gRPC, adaptar el análisis al formato definitivo y generar tablas y gráficos.
- **Avance posterior de Melanie:** actualicé `analysis/analizar.py` para exportar resumen y resultados por corrida en CSV, tablas en LaTeX y gráficos de cajas y barras en PNG/PDF (medias de las medias por corrida con desviación estándar muestral).
- **Comprobaciones del análisis:** validé con datos sintéticos temporales de ocho condiciones (cinco corridas válidas de 100 mensajes y una de calentamiento descartada por condición), contrastando resultados con NumPy y revisando tablas y figuras en local.
- **Próximo paso:** adaptar el lector a los CSV reales de latencia de sockets y gRPC y generar las tablas y figuras experimentales.
- **Para revisión del grupo:** preparé `docs/lamport.tex` y su vista `docs/verificacion-lamport.pdf` con los resultados reales de sockets, el ejemplo de concurrencia y la captura. Para compilar desde `docs/` con Biber: `pdflatex verificacion-lamport.tex`, `biber verificacion-lamport` y dos pasadas de `pdflatex verificacion-lamport.tex`. Queda pendiente verificar los CSV de eventos de gRPC y los de latencia cuando estén listos.
- **Protocolo e integración:** redacté `docs/protocolo.tex` y compilé `docs/protocolo-experimental.pdf` con el diseño experimental, entorno, mediciones y tratamiento estadístico, dejando marcadas las confirmaciones pendientes.
- **Documento del grupo:** integré hipótesis, protocolo y verificación de Lamport de sockets en `docs/informe.tex` y compilé `docs/informe.pdf` (5 páginas) para continuar sumando secciones.
- **Referencias e integración bibliográfica:** incorporé cinco fuentes (2022–2026) en `docs/referencias.bib` (dos artículos indexados, un libro y especificaciones RFC de TCP y HTTP/2), contrastando DOI, metadatos y el PDF institucional de UKAEA para IEEE Access, y citándolas en hipótesis, protocolo y Lamport.
- **Compilación y revisión:** regeneré el informe integrado y las vistas independientes con pdfLaTeX y Biber, revisando formato, citas IEEE, enlaces y comandos en el README.
- **Documentación del análisis:** redacté `docs/analisis.tex` sobre lectura/validación de CSV, descarte de calentamiento, agrupaciones, estadísticas, rendimiento y gráficos, incluyendo fragmentos de `analysis/analizar.py` mediante `listings`. Integré la sección (7 páginas), compilé y revisé el PDF, y actualicé el README y dependencias.
- **Arquitectura:** redacté `docs/arquitectura.tex` y el diagrama en TikZ `docs/figuras/arquitectura-nodos.tex` según el código TCP (procesos en localhost, puertos 5000–5002, relojes y logs), incluyendo `proto/communication.proto` y dejando anotadas las confirmaciones pendientes de gRPC.
- **Revisión e integración:** compilé el informe de 8 páginas, revisé el diagrama, el contrato y el PDF, y actualicé el README con TikZ y rutas de compilación.

## Jueves 19/11/2026

- Integrantes presentes: Angel Zambrano
- Qué hicimos: latencia.py para medir la latencia de ida y vuelta con sockets. El nodo-A funciona como servidor de eco en el puerto 5000 y el cliente envía mensajes JSON por una misma conexión, midiendo cada ida y vuelta con time.perf_counter(). Hicimos una corrida de calentamiento (descartada) y 5 corridas de 100 envíos con mensajes de unos 100 bytes y de unos 10 KB, en total 1000 mediciones en data/latencias_sockets.csv. También corrimos la prueba con nodo-A, nodo-B y nodo-C enviando a la vez (600 mediciones en data/latencias_sockets_concurrente.csv).
- Problemas encontrados: ninguno en esta sesión.

## Jueves 19/11/2026 — Sesión de Steven

- Integrante: Steven Pozo.
- Qué hicimos: implementamos src/grpc/latencia.py con un servidor de eco y clientes gRPC que reutilizan el canal durante cada corrida y miden cada ida y vuelta con time.perf_counter_ns(). El relleno se ajusta con ByteSize() para que cada solicitud protobuf serializada mida exactamente 100 o 10 000 bytes.
- Prueba secuencial: ejecutamos una corrida de calentamiento y cinco corridas válidas de 100 mensajes por tamaño. data/latencias_grpc.csv conserva las 1200 mediciones originales e identifica las 200 de calentamiento para descartarlas durante el análisis.
- Prueba concurrente: ejecutamos nodo-A, nodo-B y nodo-C simultáneamente, cada uno con un canal independiente y 100 mensajes. Se hizo una corrida de calentamiento y una válida por tamaño. data/latencias_grpc_concurrente.csv contiene 1200 filas y repite en cada fila la duración completa de su corrida.
- Verificación: comprobamos las columnas requeridas por analysis/analizar.py, los tamaños, las cantidades por corrida y cliente, los tiempos positivos, una sola duración por corrida y la ausencia de identificadores duplicados.
- Resultados preliminares: en las corridas válidas, la latencia media secuencial fue 0.29 ms para 100 bytes y 0.33 ms para 10 000 bytes; en modo concurrente fue 0.50 ms y 0.56 ms, respectivamente. Melanie realizará el tratamiento estadístico final con los CSV originales.
- Problemas encontrados: ninguno durante las corridas definitivas.

### Jueves 19/11/2026 — Sesión de Melanie
- **Integrante:** Melanie Muñoz.
- **Qué hicimos:** revisé los cuatro CSV reales de latencia y adapté `analysis/analizar.py` al formato de seis columnas de sockets, pasando el modo por argumento y manteniendo la duración ausente como N/D en rendimiento.
- **Resultados del análisis:** procesé 4000 filas (excluyendo 800 de calentamiento de gRPC) y generé tablas y gráficos con 3200 mensajes válidos en ocho condiciones (cinco corridas secuenciales y una concurrente por tamaño en cada mecanismo).
- **Verificación:** contrasté estadísticas con NumPy, verifiqué compatibilidad con el formato previo y comprobé la integridad de los CSV originales mediante hashes SHA-256, creando `data/SHA256SUMS` para los diez CSV de la sesión.
- **Lamport de gRPC:** comprobé 21 mensajes emparejados y 42 eventos registrados, documentando el alcance y la revisión pendiente de acuses RPC en reloj y logs.
- **Informe:** redacté resultados preliminares, sincronicé snippets del análisis, actualicé puertos y estado de gRPC, añadí amenazas a la validez, registré mi entorno en `data/entorno_melanie.json` y compilé/revisé el informe de 13 páginas antes de publicarlo.
- **Pendientes del grupo:** registrar entorno y duración total de sockets; revisar calentamiento concurrente y límites de medición de ambos mecanismos; ejecutar ambos mecanismos en cada equipo y comparar resultados en condiciones equivalentes.
- **Estado:** script, salidas de CSV reales, fuentes LaTeX, PDF, README, registro de integridad y bitácora publicados juntos en un commit.

### Estado de entrega confirmado por Melanie
- PDF de una página para el SGA entregado (sin verificar envío en plataforma).
- Carátula local con diseño de referencia y título `GA-SUM-02 / PE-U1` sin fecha, distinta del informe completo.
- Estado durante la revisión: pruebas propias, integración, discusión y conclusiones conservadas en local antes de su publicación.

### Jueves 19/11/2026 — Pruebas propias e integración de Melanie
- **Integrante:** Melanie Muñoz. Ejecuté y validé las pruebas, el script de medición, el análisis y la redacción/integración del informe en mi equipo. Tomé y compartí las capturas de la sesión y revisé las vistas del PDF.
- **Ejecución:** reutilicé los clientes del commit `cd8f1564ffd1` y ejecuté sockets y gRPC en Melanir (localhost), actualizando `data/entorno_melanie.json` y guardando eventos y mediciones propias en `data/melanie/2026-11-19/` para no mezclar con los datos previos.
- **Intercambios y Lamport:** tres CSV por mecanismo con 42 eventos y 21 mensajes emparejados; el verificador validó 21/21 envíos–recepciones y 42/42 actualizaciones locales. Sin camino causal entre `42dd864c` (`nodo-A`) y `fe53befd` (`nodo-B`) con reloj 1 en sockets, y entre `1c1cbfe3` y `93224eb9` en gRPC. Los acuses de gRPC no quedan registrados ni aplicados al reloj del cliente en la implementación actual.
- **Medición:** implementé `analysis/medir_equipo.py` reutilizando funciones base, registrando equipo y duración total, con 1 corrida de calentamiento y 5 válidas por tamaño (100 y 10 000 bytes serializados) y modo (secuencial y 3 clientes concurrentes, 100 envíos/cliente): 9600 filas en total (1600 calentamiento y 8000 válidas en 8 condiciones y 40 corridas válidas).
- **Problema encontrado:** el primer arranque del servidor TCP agotó la espera antes de medir; corregí la espera para reintentar ante `TimeoutError` y volví a ejecutar (el intento fallido quedó en la sesión temporal local sin filas en los CSV finales).
- **Análisis:** generé `resumen.csv`, `por_corrida.csv`, dos tablas LaTeX y dos gráficos (PNG/PDF) en `analysis/resultados-melanie-2026-11-19/`, contrastando estadísticas con NumPy. Los `resumen_captura.csv` en `data/` son salidas derivadas de presentación, no datos crudos extra.
- **Resultados:** en secuencial de 100 bytes, medianas de 0,0901 ms (sockets) vs. 1,28585 ms (gRPC) —sockets un 92,99 % menor—; en 10 000 bytes con 3 clientes, medias de 0,3553 ms vs. 1,8018 ms. Reflejan estas implementaciones en este equipo sin aislar transporte ni serialización.
- **Límites registrados:** sockets arma JSON fuera del cronómetro individual y gRPC incluye serialización interna; la duración total incluye creación/cierre de clientes/conexiones e hilos concurrentes. Se corrió primero sockets y luego gRPC sin alternar orden ni medir carga de fondo continua.
- **Evidencias:** conservé 6 capturas originales en `evidencias/melanie/2026-11-19/` sin editar (01 y 02 de apoyo con encuadre parcial; 03–06 con usuario, equipo, fecha y hora; 06 del análisis conjunto).
- **Informe:** integré resultados propios, capturas (01 y 02 en páginas completas), discusión vinculada a la hipótesis y conclusiones cuantificadas, además de la carátula con título `GA-SUM-02 / PE-U1`. Compilé y revisé el PDF de 27 páginas y sus enlaces internos.
- **Documentación e integridad:** actualicé el README con comandos de ejecución, verificación y compilación y el estado de pendientes. Validé los 10 hashes previos antes de ampliar `data/SHA256SUMS` a los subdirectorios y contrasté las copias locales con los originales.
- **Pendientes:** concretar escenario del PFC, revisar aportes y mediciones de los compañeros, completar declaración de IA y tabla de aportes, preparar video y demostración y revisar capturas obligatorias. Consta entrega de PDF de 1 página para el SGA.
- **Estado durante la revisión:** guardado en local, sin commit ni push en ese momento; posteriormente publicado en el avance indicado al final de esta sesión.
- **Aportes y declaración:** añadí `docs/aportes.tex` y `docs/uso-ia.tex` al informe, vinculando mis commits de los días 17–19 y separando las pruebas locales; los demás integrantes deben completar sus filas y declaraciones. Preparado inicialmente en local.
- **Publicación autorizada:** integré los avances locales en un solo commit tras actualizar README y tabla de aportes, recompilar informe y protocolo y reunir scripts, pruebas, capturas, resultados y documentación.
- **Integridad al clonar:** añadí `.gitattributes` para evitar que Git altere los CSV; restauré los 10 CSV previos de `data/` a su versión original en Git (solo diferían en finales de línea de Windows) y ajusté sus hashes, manteniendo los 12 CSV propios contrastados con la sesión y verificando el conjunto en una copia limpia antes de publicar.
- **Estado publicado:** los avances se incorporaron en el commit [f0ddec0 — Agrega mis pruebas y actualiza el informe](https://github.com/iMouraad/PE-U1-MPZ/commit/f0ddec0b69d21c72c7e9d70fdaba6014d062dcf6). El PDF publicado tiene 28 páginas.

## Viernes 20/11/2026 — Sesión de Steven

- Integrante: Steven Pozo.
- Revisión final de gRPC: conservamos sin cambios los CSV originales del 18 y 19 de noviembre para no invalidar el análisis ya integrado. Revisamos los resultados publicados y confirmamos que corresponden a 21 mensajes de Lamport, 1000 mediciones secuenciales válidas y 600 concurrentes válidas, además de sus calentamientos identificados.
- Integridad: comprobamos que los cinco CSV de eventos y latencia de Steven almacenados en Git coinciden con sus entradas en data/SHA256SUMS. En Windows, la copia de trabajo puede representar finales de línea distintos; la comprobación se hizo sobre los bytes publicados en los objetos de Git, que son los registrados por el equipo.
- Documentación: completamos la fila de Steven en docs/aportes.tex con sus commits de los días 17, 18 y 19, y añadimos en docs/uso-ia.tex una declaración del alcance de Codex, las verificaciones realizadas y la responsabilidad del estudiante.
- Pendiente: tomar la captura propia con usuario, equipo, fecha y hora visibles; preparar el video grupal y revisar la explicación del código para la demostración.

## Sábado 21/11/2026 — Sesión de Steven

- Integrante: Steven Pozo.
- Pruebas de sockets: ejecuté en `DESKTOP-5MJCPHU`, con Python 3.12.10, una corrida de calentamiento y cinco corridas válidas de 100 envíos para 100 y 10 000 bytes, tanto en modo secuencial como con tres clientes concurrentes. Los CSV originales, la duración total, el entorno y los comandos quedaron en `data/steven/2026-11-21/mediciones_sockets/`.
- Acuses gRPC: actualicé el nodo para registrar el envío y la recepción de cada acuse y para aplicar en el cliente la regla `max(reloj_local, reloj_recibido) + 1`. Conservé una nueva sesión de tres nodos con 21 solicitudes y 21 acuses.
- Verificación: el script comprobó 84 eventos, 42/42 relaciones con envío anterior a recepción y 84/84 reglas locales de Lamport correctas. Los cinco CSV nuevos se incorporaron al registro SHA-256 sin edición manual.
- Evidencia: tomé una captura directa de PowerShell con usuario, equipo, fecha, versión de Python, comando ejecutado y resultados de la verificación visibles.
- Pendiente grupal: concretar el uso de sockets y gRPC en el PFC, grabar y enlazar el video de 3 a 5 minutos y preparar la demostración.

## Domingo 22/11/2026 — Sesión de Angel

- Integrante: Angel Zambrano.
- Pruebas propias: ejecuté `analysis/medir_equipo.py` para sockets y gRPC en el equipo `Mourad` (Windows 11 Pro, i7-10700, 15,8 GiB de RAM, Python 3.14.2). En cada tamaño y modo hubo una corrida de calentamiento y cinco válidas. Los CSV, los `sesion.json` y los registros del servidor quedaron en `data/angel/2026-11-22/`, y el entorno en `data/entorno_angel.json`.
- Resultados: la mediana de sockets estuvo entre 0,048 y 0,154 ms y la de gRPC entre 0,335 y 0,576 ms. En secuencial con 100 B, sockets dio 0,048 ms, casi igual que en mi corrida del 19 (0,047 ms).
- Integridad y evidencia: agregué los hashes de mis cuatro CSV a `data/SHA256SUMS` y las capturas 00 a 03 en `evidencias/`, con usuario, equipo, fecha y hora.
- Documentación: completé mi fila en `docs/aportes.tex`, mi declaración en `docs/uso-ia.tex` y la aplicación al PFC (SGIRI) en `docs/discusion.tex`.
- Problemas encontrados: en las primeras capturas no se veía el `whoami` porque la salida había subido; repetí el comando al final para que quedara visible.
- Pendiente grupal: grabar y enlazar el video y actualizar el estado del README.
