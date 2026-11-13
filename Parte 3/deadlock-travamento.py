import threading
import time

lockA = threading.Lock()
lockB = threading.Lock()

def thread1():
    with lockA:
        print("Thread 1 pegou A")
        time.sleep(0.05)
        print("Thread 1 tenta B")
        with lockB:
            print("Thread 1 concluiu")

def thread2():
    with lockB:
        print("Thread 2 pegou B")
        time.sleep(0.05)
        print("Thread 2 tenta A")
        with lockA:
            print("Thread 2 concluiu")

t1 = threading.Thread(target=thread1, daemon=True)
t2 = threading.Thread(target=thread2, daemon=True)

t1.start()
t2.start()

t1.join(timeout=2)
t2.join(timeout=2)

if t1.is_alive() or t2.is_alive():
    print("Deadlock: Threads não finalizaram")
    print(threading.enumerate())