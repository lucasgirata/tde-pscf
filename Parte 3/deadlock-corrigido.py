import threading 
import time

lockA = threading.Lock()
lockB = threading.Lock()

def log(mensagem):
    print(f"[{threading.current_thread().name}] {mensagem}", flush=True)

def task(nome):
    with lockA:
        log("Obteve Lock A")
        time.sleep(0.05)
        with lockB:
            log("Obteve Lock B")
            print(f"{nome} terminou", flush=True)

if __name__ == "__main__":
    thread1 = threading.Thread(target=task, args=("T1",), name="T1")
    thread2 = threading.Thread(target=task, args=("T1",), name="T2")

    thread1.start(); thread2.start()
    thread1.join(); thread2.join()

    print("O programa finalizou")