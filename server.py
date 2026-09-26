import time
from socket import *

from constCS import *
from protocol import send_json, recv_json


def add(a, b):
    return a + b


def subtract(a, b):
    return a - b


def multiply(a, b):
    return a * b


def divide(a, b):
    if b == 0:
        raise ValueError("divisao por zero")
    return a / b


def reverse(text):
    return text[::-1]


def word_count(text):
    return len(text.split())


def sleep(ms):
    time.sleep(ms / 1000)
    return ms


OPERATIONS = {
    "add": add,
    "subtract": subtract,
    "multiply": multiply,
    "divide": divide,
    "reverse": reverse,
    "word_count": word_count,
    "sleep": sleep,
}


def run_operation(call):
    if not isinstance(call, dict):
        return {"op": None, "error": "cada operacao deve ser um objeto JSON"}
    name = call.get("op")
    if name not in OPERATIONS:
        return {"op": name, "error": "operacao desconhecida"}
    try:
        return {"op": name, "result": OPERATIONS[name](*call.get("args", []))}
    except Exception as failure:
        return {"op": name, "error": str(failure)}


def process_request(request):
    if not isinstance(request, dict) or not isinstance(request.get("operations"), list):
        return {"results": [], "error": "a requisicao deve conter a lista 'operations'"}
    return {"results": [run_operation(call) for call in request["operations"]]}


def serve_client(conn):
    while True:
        try:
            request = recv_json(conn)
        except ValueError as failure:
            send_json(conn, {"results": [], "error": "JSON invalido: " + str(failure)})
            continue
        if request is None:
            return
        print("Requisicao:", request)
        response = process_request(request)
        print("Resposta:  ", response)
        send_json(conn, response)


def serve():
    listener = socket(AF_INET, SOCK_STREAM)
    listener.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    listener.bind((HOST, PORT))
    listener.listen(1)
    print("Servidor ouvindo em {}:{}".format(HOST, PORT))
    while True:
        (conn, addr) = listener.accept()
        print("Cliente conectado:", addr)
        serve_client(conn)
        conn.close()
        print("Cliente desconectado:", addr)


if __name__ == "__main__":
    try:
        serve()
    except KeyboardInterrupt:
        print("\nServidor encerrado.")
