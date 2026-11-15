import threading
import time
import random
import sys

N = 5
garfos = [threading.Lock() for _ in range(N)]
estado = ["pensando"] * N
refeicoes = [0] * N
rodando = True
inicio = time.time()


def muda_estado(i, novo):
    estado[i] = novo
    print(f"[{time.time() - inicio:.2f}s] Filosofo {i}: {novo}")


def filosofo(i, modo):
    esq = i
    dire = (i + 1) % N

    if modo == "correto":
        primeiro = min(esq, dire)
        segundo = max(esq, dire)
    else:
        primeiro = esq
        segundo = dire

    while rodando:
        time.sleep(random.uniform(0.1, 0.4))
        muda_estado(i, "com fome")

        garfos[primeiro].acquire()
        time.sleep(0.5)
        garfos[segundo].acquire()

        muda_estado(i, "comendo")
        time.sleep(random.uniform(0.1, 0.3))
        refeicoes[i] += 1

        garfos[segundo].release()
        garfos[primeiro].release()
        muda_estado(i, "pensando")


modo = sys.argv[1] if len(sys.argv) > 1 else "correto"

for i in range(N):
    threading.Thread(target=filosofo, args=(i, modo), daemon=True).start()

time.sleep(8)
rodando = False

print()
if all(e == "com fome" for e in estado):
    print("DEADLOCK: todos com fome, cada um com um garfo esperando o outro")
else:
    print("Sem deadlock")
print("Refeicoes de cada filosofo:", refeicoes)