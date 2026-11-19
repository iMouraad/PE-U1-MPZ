# PE-U1: Comunicación entre procesos con sockets TCP y gRPC

Universidad Técnica Estatal de Quevedo · Carrera de Software · Aplicaciones Distribuidas · 7mo nivel, paralelo B

Docente: Ing. Gleiston Cicerón Guerrero Ulloa

Actividad: GA-SUM-01 / PE-U1, Práctica Experimental de la Unidad 1

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

## Estado

En desarrollo. Las instrucciones para ejecutar los nodos, el análisis y la compilación del informe se agregan a medida que cada parte quede lista.

## Informe del grupo

El documento integrado está en [docs/informe.pdf](docs/informe.pdf). Su archivo principal es [docs/informe.tex](docs/informe.tex), que incorpora las secciones de hipótesis, implementación del análisis, protocolo experimental y verificación de Lamport de sockets. El protocolo señala los datos y decisiones pendientes de confirmar.

Para compilar la versión actual con pdfLaTeX desde la raíz del repositorio:

```text
cd docs
pdflatex -interaction=nonstopmode -halt-on-error informe.tex
biber informe
pdflatex -interaction=nonstopmode -halt-on-error informe.tex
pdflatex -interaction=nonstopmode -halt-on-error informe.tex
```

Se necesita una distribución LaTeX con babel (español), amsmath, booktabs, tabularx, graphicx, caption, pdflscape, listings, csquotes, biblatex con estilo IEEE, Biber e hyperref. La bibliografía se lee desde docs/referencias.bib. La captura se carga desde evidencias/ y los fragmentos de código desde analysis/analizar.py, por lo que debe conservarse la estructura de carpetas al compilar.
