import threading
import multiprocessing
import time
import math

def cpu_work():
    result = 0
    for i in range(3000000):
        result += math.sqrt(i)

def io_work():
    time.sleep(2)

def child_work():
    time.sleep(1.5)

if __name__ == "__main__":
    print("Spawning threads...")
    threads = [threading.Thread(target=cpu_work) for _ in range(3)]
    for t in threads:
        t.start()

    print("Spawning child process...")
    child = multiprocessing.Process(target=child_work)
    child.start()

    for t in threads:
        t.join()
    child.join()
    print("All done.")