import multiprocessing
import math
import time

def worker(task_id, n):
    result = sum(math.sqrt(i) for i in range(n))
    print(f"Worker {task_id} done: {result:.2f}")

if __name__ == "__main__":
    print("Spawning 3 child processes")
    processes = []
    for i in range(3):
        p = multiprocessing.Process(
            target=worker, args=(i, 1500000)
        )
        processes.append(p)
        p.start()
        time.sleep(0.1)

    for p in processes:
        p.join()

    print("finished")