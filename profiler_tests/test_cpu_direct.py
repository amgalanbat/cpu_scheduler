import math
import time

print("Phase 1: Heavy CPU burst - 4 seconds")
start = time.time()
result = 0
while time.time() - start < 4:
    for i in range(50000):
        result += math.sqrt(i) * math.sin(i)

print("Phase 2: Rest - 2 seconds")
time.sleep(2)

print("Phase 3: Second CPU burst - 4 seconds")
start = time.time()
while time.time() - start < 4:
    for i in range(50000):
        result += math.sqrt(i) * math.cos(i)

print(f"Done. Result: {result:.2f}")