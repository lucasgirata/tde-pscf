import threading 
import time

lockA = threading.Lock()
lockB = threading.Lock()

def tarefa(nome):
    with lockA:
        print(nome, "obteve A")
        time.sleep(0.05)
        with lockB:
            print(nome, "obteve B")
            print(nome, "concluiu")

thread1 = threading.Thread(target=tarefa, args=("Thread 1",))
thread2 = threading.Thread(target=tarefa, args=("Thread 2",))

thread1.start()
thread2.start()
thread1.join()
thread2.join()
print("Programa finalizado")