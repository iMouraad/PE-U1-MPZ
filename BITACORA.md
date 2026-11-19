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
