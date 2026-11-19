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

## Martes 17/11/2026 — Sesión de Melanie

- Integrante: Melanie Muñoz.
- Qué hicimos: con apoyo de Codex, preparamos las versiones de las cinco dependencias en requirements.txt y el objetivo e hipótesis en docs/hipotesis.tex. Comprobamos la instalación en un entorno virtual con Python 3.14 y la compilación del fragmento LaTeX. También preparamos analysis/analizar.py para calcular estadísticas de latencia y rendimiento, descartar el calentamiento y agrupar por mecanismo, equipo, tamaño y modo.
- Verificación: el script de análisis se comprobó con datos sintéticos temporales. Esos datos se usaron para verificar los cálculos; las mediciones experimentales siguen pendientes.
- Aportes publicados: [dependencias e hipótesis](https://github.com/iMouraad/PE-U1-MPZ/commit/06b09be470f6cc1f77d8f8b6a40be9c13855f3cc) y [script de análisis](https://github.com/iMouraad/PE-U1-MPZ/commit/f7cb1edbd9493d57c989a1cf0675eb7d19c0a8c7).
- Problemas encontrados y solución: todavía faltaban los CSV de mediciones. Se definió un formato provisional, pendiente de contrastarlo con los archivos que generen sockets y gRPC.

## Miércoles 18/11/2026 — Sesión de Steven

- Integrante: Steven Pozo.
- Qué hicimos: implementamos un único programa para ejecutar nodo-A, nodo-B y nodo-C mediante gRPC en los puertos 50051, 50052 y 50053. Cada nodo funciona como servidor y cliente, incrementa su reloj de Lamport antes de enviar y al recibir aplica max(local, recibido) + 1.
- Corrida: ejecutamos los tres nodos con 7 envíos cada uno y registramos automáticamente los eventos en data/eventos_grpc_nodo-A.csv, nodo-B.csv y nodo-C.csv, usando el mismo formato de los registros de sockets.
- Verificación: comprobamos los CSV con analysis/verificar_lamport.py para emparejar cada envío con su recepción y validar las actualizaciones del reloj lógico.
- Entorno: registramos en data/readme.md el sistema operativo, procesador, RAM, versiones de Python y gRPC, y los comandos utilizados.
- Pendiente: realizar las corridas de latencia de 100 bytes y 10 KB, incluida la prueba concurrente, según el protocolo experimental.

## Miércoles 18/11/2026 — Sesión de Melanie

- Integrante: Melanie Muñoz.
- Qué hicimos: revisamos los archivos nuevos del equipo y, con apoyo de Codex, preparamos analysis/verificar_lamport.py para comprobar los CSV reales de sockets. El script empareja envíos y recepciones por id_mensaje, revisa las contrapartes y comprueba las actualizaciones locales del reloj desde cero.
- Resultados: los tres archivos contienen 42 eventos y 21 mensajes completos. Los 21 mensajes cumplen reloj de recepción mayor que reloj de envío y las 42 actualizaciones cumplen las reglas de Lamport.
- Concurrencia: se identificó el envío de cf648d87 en nodo-A y la recepción de a5cbb3c7 en nodo-B, ambos con reloj 2. No existe un camino causal entre ellos usando el orden local y los mensajes registrados en esta corrida.
- Verificación: comprobamos el verificador con los datos reales y con copias temporales alteradas para detectar registros incompletos o incorrectos. Los CSV originales conservan sus hashes SHA-256.
- Evidencia: Melanie ejecutó el verificador en PowerShell en su equipo Melanir. La captura original muestra el usuario melanir\melanie, la fecha y hora del sistema y los resultados completos: [captura de verificación](evidencias/melanie-verificacion-lamport.png). El verificador, la captura y esta bitácora se incorporan juntos en esta entrega.
- Pendiente: recibir las mediciones de latencia de ambos mecanismos, ajustar el análisis al formato real y generar las tablas y gráficos.
- Avance posterior de Melanie: con apoyo de Codex, ampliamos analysis/analizar.py para exportar el resumen y los resultados por corrida en CSV, las tablas de latencia y rendimiento en LaTeX y los gráficos de cajas y barras en PNG y PDF. Las barras representan la media de las medias por corrida y muestran una desviación estándar muestral entre corridas.
- Comprobaciones del análisis: usamos datos sintéticos temporales de ocho condiciones, con cinco corridas válidas de 100 mensajes cada una y una corrida de calentamiento descartada por condición. Contrastamos las estadísticas con NumPy, compilamos las tablas LaTeX y revisamos los gráficos. Los datos y las salidas de esta prueba se conservaron únicamente en local, identificados como sintéticos.
- Próximo paso: ajustar el lector a los CSV reales de latencia de sockets y gRPC y generar las tablas y figuras experimentales.
- Para revisión del grupo: la sección docs/lamport.tex y el PDF docs/verificacion-lamport.pdf están disponibles en esta entrega con los resultados reales de sockets, el ejemplo de concurrencia y la captura de ejecución. Angel y Steven pueden revisar la explicación para integrarla al informe. Cuando estén los CSV de eventos de gRPC, falta ejecutar su verificación e incorporar los resultados; también siguen pendientes los CSV de latencia para completar el análisis. Para compilar esta sección por separado desde docs/, ejecutar pdflatex verificacion-lamport.tex dos veces. El archivo principal verificacion-lamport.tex incluye lamport.tex y utiliza la captura que ya está en evidencias/.
- Protocolo e integración: con apoyo de Codex, Melanie preparó docs/protocolo.tex y su vista independiente docs/protocolo-experimental.pdf. Se detallaron el diseño de las pruebas, el entorno por registrar, las mediciones y el tratamiento estadístico. Las decisiones pendientes de confirmar con los clientes y los CSV reales están señaladas en el texto.
- Documento del grupo: docs/informe.tex reúne la hipótesis, el protocolo y la verificación real de Lamport de sockets mediante las secciones existentes. Se compiló docs/informe.pdf y se revisó su presentación. Para continuar el informe, el grupo puede añadir las siguientes secciones desde ese archivo principal.
- Referencias e integración bibliográfica: Melanie, con apoyo de Codex, incorporó cinco fuentes de 2022 a 2026 en docs/referencias.bib: dos artículos de revistas indexadas, un libro y las especificaciones RFC de TCP y HTTP/2. Se contrastaron los DOI y metadatos; para el artículo de IEEE Access se consultó también el PDF institucional de UKAEA. Las fuentes se citaron en la hipótesis, el protocolo y la explicación de Lamport.
- Compilación y revisión: se regeneraron el informe integrado y las dos vistas independientes mediante pdfLaTeX, Biber, pdfLaTeX y pdfLaTeX. Se revisaron la presentación, las citas IEEE y los enlaces del PDF. El informe integrado tiene cinco páginas. El README contiene el orden de comandos y las dependencias actualizadas.
- Aviso para el grupo: las vistas independientes también requieren Biber desde esta actualización. Para verificacion-lamport.tex, ejecutar pdflatex verificacion-lamport.tex, biber verificacion-lamport, pdflatex verificacion-lamport.tex y pdflatex verificacion-lamport.tex. El documento principal para continuar el trabajo conjunto sigue siendo docs/informe.tex.
- Documentación del análisis: Melanie, con apoyo de Codex, preparó docs/analisis.tex para explicar la lectura y validación de CSV, el descarte del calentamiento, las agrupaciones, las estadísticas, el rendimiento y las salidas gráficas. Los fragmentos se leen directamente de analysis/analizar.py mediante listings. La sección se integró al informe de siete páginas, se compiló y revisó el PDF, y se actualizaron el README y las dependencias LaTeX. Este avance se publica en un solo commit.
- Arquitectura: Melanie, con apoyo de Codex, preparó docs/arquitectura.tex y el diagrama editable en TikZ docs/figuras/arquitectura-nodos.tex a partir del código TCP publicado. Se documentaron los tres procesos en localhost, los puertos 5000, 5001 y 5002, sus relojes y los registros de eventos. El contrato gRPC se incluye directamente desde proto/communication.proto.
- Revisión e integración: se recompiló el informe de ocho páginas y se revisaron el diagrama, el contrato y la presentación del PDF. El README incluye TikZ y las rutas necesarias para compilar. La sección señala que aún falta confirmar los puertos, las conexiones y el uso de los campos timestamp y lamport_clock cuando se incorpore la implementación ejecutable de gRPC.

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

## Jueves 19/11/2026 — Sesión de Melanie

- Integrante: Melanie Muñoz.
- Trabajo realizado con apoyo de Codex: revisamos los cuatro CSV reales de latencia y adaptamos analysis/analizar.py al formato nativo de seis columnas de sockets. El modo se indica por argumento y la duración ausente se mantiene como dato desconocido, por lo que su rendimiento aparece como N/D.
- Resultados del análisis: se leyeron 4000 filas y se excluyeron las 800 de calentamiento de gRPC. Las tablas y gráficos se generaron con 3200 mensajes válidos en ocho condiciones. Ambos mecanismos tienen cinco corridas secuenciales y una concurrente por tamaño.
- Verificación: contrastamos las estadísticas con NumPy, comprobamos la compatibilidad con el formato completo anterior y verificamos que los CSV originales conservaran sus hashes SHA-256. Se creó data/SHA256SUMS como registro de integridad de los diez CSV disponibles en esta sesión.
- Lamport de gRPC: el verificador emparejó 21 mensajes y comprobó 42 eventos registrados. Se documentó el alcance de esos registros y que los acuses RPC todavía requieren revisión del reloj y del registro de eventos.
- Informe: se preparó la sección de resultados preliminares, se sincronizaron los fragmentos de código del análisis y se actualizaron los puertos y el estado de la implementación gRPC. Se incorporó la sección de amenazas a la validez. Se registró el entorno del equipo de Melanie para el análisis en data/entorno_melanie.json. El informe de trece páginas se compiló y revisó antes de publicarlo.
- Pendientes del grupo: registrar el entorno y la duración total de sockets; revisar el calentamiento concurrente y los límites de medición de ambos mecanismos; ejecutar los dos mecanismos en cada equipo. Los resultados recibidos describen sesiones con condiciones distintas y la comparación final queda pendiente.
- Estado: el script, las salidas de los CSV reales, las fuentes LaTeX, los PDF, el README, el registro de integridad y esta bitácora se publican juntos en un solo commit.

### Estado de entrega confirmado por Melanie

- [x] PDF de una sola página para el SGA entregado, según confirmación de Melanie. No se verificó el envío desde la plataforma.
- La carátula del informe completo es distinta del PDF de entrega del SGA. Se preparó localmente con el diseño de la referencia aportada y se corrigió el título a GA-SUM-02 / PE-U1 por indicación de Melanie, sin fecha en la carátula.
- Las pruebas propias, su integración, la discusión y las conclusiones siguen en revisión local, sin publicar estos cambios.

### Jueves 19/11/2026 — Pruebas propias e integración de Melanie

- Integrante: Melanie Muñoz. Se utilizó Codex como apoyo para ejecutar y comprobar las pruebas, preparar el programa común de medición, analizar los datos y redactar e integrar el informe. Melanie tomó y compartió las capturas de la sesión y revisó las vistas del PDF.
- Ejecución: se reutilizaron los clientes publicados en el commit cd8f1564ffd1 y se ejecutaron sockets y gRPC en el equipo Melanir, como procesos en localhost. El entorno se actualizó en data/entorno_melanie.json. Los eventos y las mediciones propias están separados en data/melanie/2026-11-19/ para conservar los datos anteriores del grupo.
- Intercambios y Lamport: cada mecanismo generó tres CSV con 42 eventos y 21 mensajes emparejados. El verificador comprobó 21/21 relaciones envío–recepción y 42/42 actualizaciones locales. En sockets, los envíos 42dd864c de nodo-A y fe53befd de nodo-B tienen reloj 1 sin camino causal registrado; en gRPC, el par equivalente es 1c1cbfe3 y 93224eb9. La verificación de gRPC no cubre los acuses, que el nodo actual no registra ni aplica al reloj del cliente.
- Medición: analysis/medir_equipo.py reutiliza las funciones originales, registra el equipo y la duración total y aplica una corrida de calentamiento y cinco válidas por tamaño y modo. Se midieron 100 y 10 000 bytes serializados, con 100 envíos por cliente y tres clientes en concurrencia. Los cuatro CSV conservan 9600 observaciones: 1600 de calentamiento y 8000 válidas, en ocho condiciones y 40 corridas válidas.
- Problema encontrado: el primer intento de iniciar el servidor TCP agotó la espera de disponibilidad antes de producir mediciones. Se corrigió la espera para reintentar también ante TimeoutError y se ejecutó de nuevo. Los registros de ese intento permanecen en la sesión temporal local y no aportan filas a los CSV de resultados.
- Análisis: se generaron resumen.csv, por_corrida.csv, dos tablas LaTeX y dos gráficos en PNG/PDF en analysis/resultados-melanie-2026-11-19/. Las estadísticas se contrastaron con NumPy. Los dos archivos resumen_captura.csv de data/ son salidas derivadas para presentar los resultados de cada mecanismo, no datos crudos adicionales.
- Resultados: con 100 bytes y envíos secuenciales, las medianas fueron 0,0901 ms en sockets y 1,28585 ms en gRPC; la mediana de sockets fue un 92,99 % menor respecto de gRPC. Con 10 000 bytes y tres clientes, las medias fueron 0,3553 ms y 1,8018 ms. Se interpretan como resultados de estas implementaciones en este equipo, sin aislar el efecto del transporte o de la serialización.
- Límites registrados: sockets prepara JSON fuera del cronómetro individual y gRPC incluye la serialización interna de la llamada. La duración total incorpora creación y cierre de clientes y conexiones, además del grupo de hilos en concurrencia. Se ejecutó primero sockets y luego gRPC, sin alternar el orden y sin monitorización continua de la carga de fondo.
- Evidencias: se conservaron seis capturas originales en evidencias/melanie/2026-11-19/. Las capturas 01 y 02 son de apoyo por su encuadre incompleto de identificación; las 03–06 muestran usuario, máquina, fecha y hora. La sexta documenta el análisis conjunto. No se modificaron las imágenes.
- Informe: se integraron los resultados propios, las capturas, la discusión ligada a la hipótesis y las conclusiones cuantificadas. Se separaron las dos primeras capturas en páginas completas para mejorar su lectura. Se añadió la carátula con el diseño de la referencia y el título corregido por Melanie. Se compiló y revisó el PDF de 27 páginas y se comprobaron sus enlaces internos.
- Documentación e integridad: se actualizó el README con los comandos de medición, análisis, verificación de Lamport y compilación, y con el estado real de los pendientes. Se verificaron los diez hashes anteriores antes de ampliar data/SHA256SUMS a los CSV de los subdirectorios. Las copias de la sesión propia se contrastaron con los archivos originales conservados en local.
- Pendientes: concretar el escenario del PFC, revisar los aportes y mediciones de los compañeros, completar la declaración de IA y la tabla de aportes, preparar el video y la demostración y revisar las capturas obligatorias. El PDF de una página para el SGA consta como entregado según confirmación de Melanie.
- Estado de este avance: guardado únicamente en local por indicación de Melanie, sin commit ni subida de estas modificaciones.
- Aportes y uso de IA: se añadieron docs/aportes.tex y docs/uso-ia.tex al informe. La fila de Melanie enlaza cuatro commits publicados de los días 17, 18 y 19 y distingue las pruebas propias que aún permanecen locales. La declaración especifica la asistencia de Codex en búsqueda, código, ejecución, redacción técnica y preparación del documento, junto con las comprobaciones realizadas. Los otros integrantes deben completar sus filas y sus declaraciones. Esta actualización también se mantiene local.
- Publicación autorizada: Melanie pidió incorporar todos los avances locales en un solo commit. Se actualizaron las referencias al estado local en el README y la tabla de aportes, se recompilaron el informe y la vista independiente del protocolo y se reunieron los scripts, pruebas, capturas, resultados y documentación.
- Integridad al clonar: se añadió .gitattributes para impedir que Git transforme los CSV. Los diez CSV anteriores de data/ se restauraron a los bytes originales almacenados en Git, tras comprobar que la única diferencia local eran los saltos de línea de Windows. Se ajustaron sus hashes a esa versión original. Los doce CSV propios conservan los bytes contrastados con la sesión. El registro completo se comprueba desde una copia limpia antes de publicar.
