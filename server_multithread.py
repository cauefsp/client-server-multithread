import threading
from socket import *

from constCS import *
from server import serve_client


def atender_conexao(conn, addr):
    print("Cliente conectado:", addr)
    serve_client(conn)
    conn.close()
    print("Cliente desconectado:", addr)


def serve():
    listener = socket(AF_INET, SOCK_STREAM)
    listener.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    listener.bind((HOST, PORT))
    listener.listen(128)
    print("Servidor multithread ouvindo em {}:{}".format(HOST, PORT))
    while True:
        (conn, addr) = listener.accept()
        thread = threading.Thread(target=atender_conexao, args=(conn, addr), daemon=True)
        thread.start()


if __name__ == "__main__":
    try:
        serve()
    except KeyboardInterrupt:
        print("\nServidor encerrado.")
