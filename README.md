# Cliente-Servidor multithread

Trabalho de Sistemas Distribuídos. Parte do código da tarefa anterior
([client-server-basics](https://github.com/cauefsp/client-server-basics)), em que o
servidor processa lotes de operações enviados pelo cliente, e acrescenta:

- um servidor que dispara uma thread nova para cada requisição recebida;
- um cliente que envia cada requisição por uma thread nova, com várias em paralelo;
- geração automática de requisições aleatórias;
- um experimento que compara o tempo das versões single-threaded e multithread.

## Protocolo

Sockets TCP. Cada mensagem é um objeto JSON terminado por `\n`. A requisição traz a
lista `operations`; a resposta traz `results`, na mesma ordem.

```json
{"operations": [{"op": "add", "args": [2, 3]}, {"op": "reverse", "args": ["socket"]}]}

{"results": [{"op": "add", "result": 5}, {"op": "reverse", "result": "tekcos"}]}
```

Cada resultado traz `result` ou `error`. Uma operação que falha (operação
desconhecida, argumentos errados, divisão por zero) não invalida as outras do lote.

## Operações

| Operação | Argumentos | Retorno |
|---|---|---|
| `add` | dois números | soma |
| `subtract` | dois números | diferença |
| `multiply` | dois números | produto |
| `divide` | dois números | quociente |
| `reverse` | um texto | texto invertido |
| `word_count` | um texto | quantidade de palavras |
| `sleep` | milissegundos | o próprio valor, depois de esperar esse tempo |

A operação `sleep` foi criada para o experimento: ela simula um processamento lento,
como um acesso a disco ou banco de dados.

## Como executar

Requer apenas Python 3. Host e porta ficam em `constCS.py` (`127.0.0.1:5678`).
Rode um dos servidores em um terminal e o cliente em outro.

```bash
python3 server.py              # servidor single-threaded (tarefa anterior)
python3 server_multithread.py  # servidor multithread: uma thread por requisição

python3 client.py              # envia um lote de demonstração
python3 client.py -i           # modo interativo: uma operação por linha, linha vazia envia
python3 client.py -a 5000      # 5000 requisições aleatórias, uma de cada vez
python3 client_multithread.py 5000    # 5000 requisições, cada uma enviada por uma thread
python3 client_multithread.py 5000 2  # o mesmo, com um sleep de 2 ms em cada requisição
```

Nos modos automáticos, `gerador.py` monta as requisições com 1 a 4 operações
sorteadas e semente fixa, então toda execução gera as mesmas requisições. Cada
requisição abre a sua própria conexão, e por isso o servidor multithread cria uma
thread para cada requisição. No fim, o cliente mostra o tempo total:

```
5000 requisicoes em 1.705 s (2933 req/s), 0 falhas
```

O cliente multithread cria uma thread por requisição, mas deixa no máximo 50 rodando
ao mesmo tempo (`MAX_THREADS`), para não abrir milhares de conexões de uma vez.

## Experimento

`python3 experimento.py` sobe cada servidor, envia as requisições, mede o tempo e
mostra a tabela (leva uns 3 minutos). Foram comparadas três versões:

1. **single-threaded**: `client.py -a` com `server.py`, as duas da tarefa anterior;
2. **threads só no servidor**: `client.py -a` com `server_multithread.py`;
3. **threads no cliente e no servidor**: `client_multithread.py` com `server_multithread.py`.

Cada versão enviou as mesmas 5000 requisições, 5 vezes, e a tabela mostra a média. O
tempo é medido no cliente, do envio da primeira requisição até a última resposta. A
saída dos servidores é descartada durante a medição, e o script confere se todas as
versões devolveram exatamente as mesmas respostas. Rodei em um notebook com Intel Core
i7-13650HX (20 threads), Linux no WSL2 e Python 3.12, com cliente e
servidor na mesma máquina.

**Cenário 1: operações normais** (as seis operações, sem espera)

| Versão | Tempo médio | Desvio | Req/s | Ganho |
|---|---|---|---|---|
| single-threaded | 0,609 s | 0,084 s | 8210 | 1,00x |
| threads só no servidor | 1,438 s | 0,052 s | 3477 | 0,42x |
| threads no cliente e no servidor | 1,729 s | 0,090 s | 2892 | 0,35x |

**Cenário 2: com espera de 2 ms** (cada requisição termina com `sleep 2`)

| Versão | Tempo médio | Desvio | Req/s | Ganho |
|---|---|---|---|---|
| single-threaded | 12,749 s | 0,193 s | 392 | 1,00x |
| threads só no servidor | 14,169 s | 0,511 s | 353 | 0,90x |
| threads no cliente e no servidor | 2,331 s | 0,232 s | 2145 | 5,47x |

Com operações que levam microssegundos, as threads só atrapalharam: criar uma thread
por requisição custa mais do que a própria operação, e o GIL do Python não deixa as
threads processarem ao mesmo tempo. Threads só no servidor não ajudam em nenhum dos
cenários, porque o cliente sequencial nunca tem mais de uma requisição pendente. O
ganho só aparece quando existe espera e o cliente também usa threads: enquanto uma
requisição espera, outras avançam, e o tempo caiu de 12,7 s para 2,3 s.

Numa segunda execução completa os números ficaram parecidos; o que mais variou foi a
versão com threads nos dois lados no cenário 2 (1,9 s, ganho de 6,8x). Como cada
requisição abre e fecha uma conexão, o sistema acumula milhares de sockets em
`TIME_WAIT`, então também medi cada versão do cenário 1 sozinha, esperando esses
sockets sumirem antes. A ordem entre as versões não mudou.

## Arquivos

- `constCS.py`: host e porta.
- `protocol.py`: envio e leitura das mensagens JSON.
- `server.py`: operações e servidor single-threaded.
- `server_multithread.py`: servidor que cria uma thread por requisição.
- `client.py`: demonstração, modo interativo e modo automático sequencial.
- `client_multithread.py`: cliente que envia cada requisição por uma thread.
- `gerador.py`: geração das requisições aleatórias.
- `experimento.py`: experimento de desempenho.
