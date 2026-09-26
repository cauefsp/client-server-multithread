import sys
import threading

from client import send_request, rodar_automatico

MAX_THREADS = 50


def enviar_na_thread(request, respostas, indice, vagas):
    try:
        respostas[indice] = send_request(request)
    finally:
        vagas.release()


def enviar_com_threads(requisicoes):
    respostas = [None] * len(requisicoes)
    vagas = threading.Semaphore(MAX_THREADS)
    threads = []
    for indice, request in enumerate(requisicoes):
        vagas.acquire()
        thread = threading.Thread(target=enviar_na_thread, args=(request, respostas, indice, vagas))
        thread.start()
        threads.append(thread)
    for thread in threads:
        thread.join()
    return respostas


if __name__ == "__main__":
    rodar_automatico(enviar_com_threads, sys.argv[1:])
