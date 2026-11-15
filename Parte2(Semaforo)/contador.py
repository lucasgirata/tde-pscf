# TDE Programacao Concorrente - Parte 2
# Contador compartilhado entre threads: sem sincronizacao x com semaforo

import sys
import threading
import time

T = 8          # numero de threads
M = 200000     # incrementos por thread
EXECUCOES = 3  # quantas vezes roda cada versao

contador = 0
semaforo = threading.Semaphore(1)  # 1 permissao = semaforo binario


# faz uma "conta" no meio do incremento pra dar tempo de trocar de thread
# sem isso o GIL do python quase nao deixa a corrida aparecer
def incrementa(valor):
    for i in range(20):
        valor = valor ^ 0  # nao muda nada, so gasta tempo
    return valor + 1


# versao 1: sem nenhuma protecao
def tarefa_sem_semaforo():
    global contador
    for i in range(M):
        x = contador          # le
        x = incrementa(x)     # soma
        contador = x          # escreve (pode apagar o que outra thread fez)


# versao 2: com semaforo binario
def tarefa_com_semaforo():
    global contador
    for i in range(M):
        semaforo.acquire()
        try:
            x = contador
            x = incrementa(x)
            contador = x
        finally:
            semaforo.release()


def rodar(tarefa):
    global contador
    contador = 0
    threads = []
    for i in range(T):
        threads.append(threading.Thread(target=tarefa))

    inicio = time.time()
    for t in threads:
        t.start()
    for t in threads:
        t.join()  # espera todas acabarem
    fim = time.time()

    return contador, fim - inicio


def main():
    # da pra escolher a versao: python3 contador.py sem / com
    # sem argumento roda as duas
    opcao = "ambas"
    if len(sys.argv) > 1:
        opcao = sys.argv[1]

    esperado = T * M
    print("T =", T, "threads, M =", M, "incrementos, esperado =", esperado)
    print()

    if opcao == "sem" or opcao == "ambas":
        print("--- SEM semaforo ---")
        for i in range(EXECUCOES):
            obtido, tempo = rodar(tarefa_sem_semaforo)
            print(f"execucao {i+1}: esperado={esperado} obtido={obtido} perdidos={esperado - obtido} tempo={tempo:.2f}s")
        print()

    if opcao == "com" or opcao == "ambas":
        print("--- COM semaforo ---")
        for i in range(EXECUCOES):
            obtido, tempo = rodar(tarefa_com_semaforo)
            print(f"execucao {i+1}: esperado={esperado} obtido={obtido} perdidos={esperado - obtido} tempo={tempo:.2f}s")


main()
