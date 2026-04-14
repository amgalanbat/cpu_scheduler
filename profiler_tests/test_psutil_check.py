import psutil
import os
import time
import math

# print(f"My PID: {os.getpid()}")
# print(f"Parent PID: {os.getppid()}")

# p = psutil.Process(os.getpid())

# # First call always returns 0 on Windows - discard it
# p.cpu_percent(interval=None)
# time.sleep(0.1)

# print("Starting CPU work...")
# for i in range(3):
#     # Do heavy work
#     result = sum(math.sqrt(j) for j in range(1000000))
    
#     cpu = p.cpu_percent(interval=0.5)
#     mem = p.memory_info().rss / (1024 * 1024)
#     print(f"Sample {i+1}: CPU={cpu}% | Memory={mem:.1f}MB")

# print("Done.")

print(f"My PID: {os.getpid()}")

p = psutil.Process(os.getpid())

# Try with create_time approach
print(f"Process create time: {p.create_time()}")
print(f"CPU times: {p.cpu_times()}")

# Do work then measure delta manually
times_before = p.cpu_times()
time_before = time.time()

result = sum(math.sqrt(j) for j in range(2000000))

times_after = p.cpu_times()
time_after = time.time()

elapsed = time_after - time_before
cpu_used = (times_after.user - times_before.user) + \
           (times_after.system - times_before.system)
cpu_percent = (cpu_used / elapsed) * 100

print(f"Elapsed: {elapsed:.2f}s")
print(f"CPU time used: {cpu_used:.3f}s")
print(f"Calculated CPU%: {cpu_percent:.1f}%")