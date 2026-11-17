import socket, json

msg = {"sender": "nodo-B", "timestamp": 1, "message": "hola nodo-A"}

with socket.create_connection(("127.0.0.1", 5000)) as s:
    s.sendall((json.dumps(msg) + "\n").encode("utf-8"))   # el \n delimita el mensaje
    respuesta = s.makefile("r", encoding="utf-8").readline()
    print("[nodo-B] respuesta:", json.loads(respuesta))