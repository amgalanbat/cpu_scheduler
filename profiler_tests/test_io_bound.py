import threading
import time
import random

def io_simulation(thread_id):
    for i in range(5):
        wait = random.uniform(0.2, 0.8)
        time.sleep(wait)
        print(f"Thread {thread_id} completed I/O operation {i+1}")

threads = []
for i in range(6):
    t = threading.Thread(target=io_simulation, args=(i,))
    threads.append(t)
    t.start()

for t in threads:
    t.join()

print("All I/O operations done.")