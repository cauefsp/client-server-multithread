import json
import shlex
import sys
import time
from socket import *

from constCS import *
from gerador import gerar_requisicoes
from protocol import send_json, recv_json

DEMO_OPERATIONS = [
    {"op": "add", "args": [2, 3]},
    {"op": "divide", "args": [10, 4]},
    {"op": "reverse", "args": ["sistemas distribuidos"]},
    {"op": "word_count", "args": ["cliente e servidor trocam mensagens"]},
]


def parse_argument(token):
    try:
        return int(token)
    except ValueError:
        pass
    try:
        return float(token)
    except ValueError:
        return token


def read_batch():
    print("Digite uma operacao por linha (ex.: add 2 3).")
    print("Linha vazia envia o lote; lote vazio encerra o cliente.")
    operations = []
    while True:
        try:
            line = input("> ").strip()
        except EOFError:
            return operations
        if not line:
            return operations
        name, *tokens = shlex.split(line)
        operations.append({"op": name, "args": [parse_argument(t) for t in tokens]})


def request_operations(conn, operations):
    request = {"operations": operations}
    print("Enviado: " + json.dumps(request))
    send_json(conn, request)
    response = recv_json(conn)
    print("Recebido:")
    for entry in response.get("results", []):
        outcome = entry["result"] if "result" in entry else "ERRO: " + entry["error"]
        print("  {}: {}".format(entry["op"], outcome))
    if "error" in response:
        print("  ERRO: " + response["error"])


def send_request(request):
    conn = socket(AF_INET, SOCK_STREAM)
    try:
        conn.connect((HOST, PORT))
        send_json(conn, request)
        return recv_json(conn)
    except OSError as failure:
        return {"results": [], "error": "falha de conexao: " + str(failure)}
    finally:
        conn.close()


def enviar_em_sequencia(requisicoes):
    return [send_request(request) for request in requisicoes]


def contar_falhas(respostas):
    return sum(1 for response in respostas if response is None or "error" in response)


def mostrar_resumo(respostas, tempo_total):
    print("{} requisicoes em {:.3f} s ({:.0f} req/s), {} falhas".format(
        len(respostas), tempo_total, len(respostas) / tempo_total, contar_falhas(respostas)))


def rodar_automatico(enviar, argumentos):
    quantidade = int(argumentos[0]) if len(argumentos) > 0 else 1000
    espera_ms = int(argumentos[1]) if len(argumentos) > 1 else 0
    requisicoes = gerar_requisicoes(quantidade, espera_ms)
    inicio = time.perf_counter()
    respostas = enviar(requisicoes)
    mostrar_resumo(respostas, time.perf_counter() - inicio)


def main():
    if "-a" in sys.argv:
        rodar_automatico(enviar_em_sequencia, sys.argv[sys.argv.index("-a") + 1:])
        return
    conn = socket(AF_INET, SOCK_STREAM)
    conn.connect((HOST, PORT))
    if "-i" in sys.argv:
        while True:
            operations = read_batch()
            if not operations:
                break
            request_operations(conn, operations)
    else:
        request_operations(conn, DEMO_OPERATIONS)
    conn.close()


if __name__ == "__main__":
    main()
