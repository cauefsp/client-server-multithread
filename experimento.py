import statistics
import subprocess
import sys
import time
from socket import *

from client import enviar_em_sequencia, contar_falhas
from client_multithread import enviar_com_threads, MAX_THREADS
from constCS import *
from gerador import gerar_requisicoes

QUANTIDADE = 5000
REPETICOES = 5
CENARIOS = [("operacoes normais", 0), ("com espera de 2 ms", 2)]
VERSOES = [
    ("single-threaded", "server.py", enviar_em_sequencia),
    ("threads so no servidor", "server_multithread.py", enviar_em_sequencia),
    ("threads no cliente e no servidor", "server_multithread.py", enviar_com_threads),
]


def porta_ocupada():
    conn = socket(AF_INET, SOCK_STREAM)
    try:
        conn.connect((HOST, PORT))
        return True
    except OSError:
        return False
    finally:
        conn.close()


def iniciar_servidor(arquivo):
    processo = subprocess.Popen([sys.executable, arquivo], stdout=subprocess.DEVNULL)
    while not porta_ocupada():
        if processo.poll() is not None:
            sys.exit("O servidor {} encerrou antes de aceitar conexoes.".format(arquivo))
        time.sleep(0.1)
    return processo


def medir_versao(arquivo, enviar, requisicoes):
    processo = iniciar_servidor(arquivo)
    tempos = []
    for _ in range(REPETICOES):
        inicio = time.perf_counter()
        respostas = enviar(requisicoes)
        tempos.append(time.perf_counter() - inicio)
    processo.terminate()
    processo.wait()
    return tempos, respostas


def rodar_cenario(nome, espera_ms):
    requisicoes = gerar_requisicoes(QUANTIDADE, espera_ms)
    print("\nCenario: {} ({} requisicoes, {} repeticoes)".format(nome, QUANTIDADE, REPETICOES))
    print("{:<34}{:>10}{:>9}{:>9}{:>8}{:>8}{:>8}".format(
        "versao", "media (s)", "desvio", "req/s", "ganho", "iguais", "falhas"))
    referencia = None
    tempo_base = None
    for nome_versao, arquivo, enviar in VERSOES:
        tempos, respostas = medir_versao(arquivo, enviar, requisicoes)
        media = statistics.mean(tempos)
        if referencia is None:
            referencia = respostas
            tempo_base = media
        print("{:<34}{:>10.3f}{:>9.3f}{:>9.0f}{:>7.2f}x{:>8}{:>8}".format(
            nome_versao, media, statistics.stdev(tempos), QUANTIDADE / media, tempo_base / media,
            "sim" if respostas == referencia else "nao", contar_falhas(respostas)))


def main():
    if porta_ocupada():
        sys.exit("Ja existe um servidor em {}:{}. Feche-o antes de rodar o experimento.".format(HOST, PORT))
    print("Limite de threads simultaneas no cliente: {}".format(MAX_THREADS))
    for nome, espera_ms in CENARIOS:
        rodar_cenario(nome, espera_ms)


if __name__ == "__main__":
    main()
