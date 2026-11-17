import socket, json

HOST, PUERTO = "127.0.0.1", 5000

srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # socket TCP
srv.bind((HOST, PUERTO))     # lo amarra al puerto 5000
srv.listen()                 # queda esperando conexiones
print(f"[nodo-A] escuchando en {PUERTO}")

conn, addr = srv.accept()    # se bloquea hasta que llega un cliente
with conn:
    archivo = conn.makefile("r", encoding="utf-8")
    linea = archivo.readline()          # lee hasta el \n: un mensaje completo
    msg = json.loads(linea)
    print(f"[nodo-A] recibí de {msg['sender']}: {msg['message']} (reloj {msg['timestamp']})")
    acuse = {"sender": "nodo-A", "timestamp": 0, "message": "ok"}
    conn.sendall((json.dumps(acuse) + "\n").encode("utf-8"))