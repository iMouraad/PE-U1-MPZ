# Entorno de las pruebas

## gRPC — Steven Pozo

- Equipo: `DESKTOP-5MJCPHU`
- Usuario: `redsito`
- Sistema operativo: Microsoft Windows 10.0.26300 (Windows Home 26H2, compilación 26300)
- Procesador: 13th Gen Intel(R) Core(TM) i7-13620H
- Memoria RAM instalada: 15.73 GB
- Python: 3.12.10
- grpcio: 1.85.1
- grpcio-tools: 1.85.1
- protobuf: 7.36.2

Comandos ejecutados desde la raíz del repositorio, uno en cada terminal:

```powershell
python -m pip install -r requirements.txt
python src/grpc/nodo.py nodo-A 7 --espera-inicio 2 --espera-final 5 --semilla 101
python src/grpc/nodo.py nodo-B 7 --espera-inicio 2 --espera-final 5 --semilla 102
python src/grpc/nodo.py nodo-C 7 --espera-inicio 2 --espera-final 5 --semilla 103
```

Comando de verificación de los eventos:

```powershell
python analysis/verificar_lamport.py "data/eventos_grpc_*.csv"
```
