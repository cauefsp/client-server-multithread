import random

WORDS = ["cliente", "servidor", "thread", "socket", "mensagem", "rede", "processo", "sistema"]
NUMBER_OPERATIONS = ["add", "subtract", "multiply", "divide"]
TEXT_OPERATIONS = ["reverse", "word_count"]


def random_text():
    return " ".join(random.choice(WORDS) for _ in range(random.randint(1, 6)))


def gerar_operacao():
    name = random.choice(NUMBER_OPERATIONS + TEXT_OPERATIONS)
    if name in TEXT_OPERATIONS:
        return {"op": name, "args": [random_text()]}
    return {"op": name, "args": [random.randint(0, 1000), random.randint(0, 100)]}


def gerar_requisicoes(quantidade, espera_ms=0, semente=42):
    random.seed(semente)
    requisicoes = []
    for _ in range(quantidade):
        operations = [gerar_operacao() for _ in range(random.randint(1, 4))]
        if espera_ms > 0:
            operations.append({"op": "sleep", "args": [espera_ms]})
        requisicoes.append({"operations": operations})
    return requisicoes
