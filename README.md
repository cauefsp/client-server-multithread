# Cliente-Servidor multithread

Trabalho de Sistemas Distribuídos, a partir da [tarefa anterior](https://github.com/cauefsp/client-server-basics).
O servidor cria uma thread por requisição e o cliente envia cada requisição por uma thread.

## Como executar

```bash
python3 server.py                   # servidor single-threaded
python3 server_multithread.py       # servidor multithread

python3 client.py -a 5000           # 5000 requisições aleatórias, uma de cada vez
python3 client_multithread.py 5000  # 5000 requisições, uma thread para cada

python3 experimento.py              # compara as três versões (uns 3 minutos)
```

## Resultado

Tempo médio para 5000 requisições, com e sem uma espera de 2 ms no servidor:

| Versão | Normal | Com espera |
|---|---|---|
| Single-threaded | 0,61 s | 12,75 s |
| Threads só no servidor | 1,44 s | 14,17 s |
| Threads no cliente e no servidor | 1,73 s | 2,33 s |
