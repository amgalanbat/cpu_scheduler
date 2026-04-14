import threading
import multiprocessing
import time
import math
import random

def cpu_task(n):
    return sum(math.sqrt(i) for i in range(n))

def io_task(duration):
    time.sleep(duration)

def memory_task():
    data = []
    for _ in range(6):
        data.append("x" * (8 * 1024 * 1024))
        time.sleep(0.5)
    time.sleep(2)
    data.clear()

def child_process_work():
    result = cpu_task(2000000)
    print(f"Child done: {result:.2f}")

if __name__ == "__main__":
    print("Phase 1: CPU burst with threads")
    cpu_threads = [
        threading.Thread(target=cpu_task, args=(2000000,))
        for _ in range(3)
    ]
    for t in cpu_threads:
        t.start()
    for t in cpu_threads:
        t.join()

    print("Phase 2: Memory growth")
    mem_thread = threading.Thread(target=memory_task)
    mem_thread.start()
    mem_thread.join()

    print("Phase 3: I/O waiting")
    io_threads = [
        threading.Thread(target=io_task, args=(random.uniform(0.5, 1.5),))
        for _ in range(4)
    ]
    for t in io_threads:
        t.start()
    for t in io_threads:
        t.join()

    print("Phase 4: Child processes")
    children = [
        multiprocessing.Process(target=child_process_work)
        for _ in range(3)
    ]
    for c in children:
        c.start()
    for c in children:
        c.join()

    print("All phases complete.")