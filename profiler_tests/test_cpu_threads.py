import multiprocessing
import math
import time

def heavy_compute(n):
    """CPU intensive work — runs in separate process to bypass GIL."""
    result = 0
    for i in range(n):
        result += math.sqrt(i) * math.sin(i)
    return result

if __name__ == "__main__":
    print("Starting CPU intensive multiprocessing work...")
    
    # Use Pool to run work in the SAME process group
    # This makes CPU show up in parent's measurements
    pool = multiprocessing.Pool(processes=2)
    
    print("Submitting heavy tasks...")
    results = []
    for i in range(4):
        r = pool.apply_async(heavy_compute, args=(3000000,))
        results.append(r)
        time.sleep(0.1)
    
    # Wait for all tasks
    for r in results:
        r.get()
    
    pool.close()
    pool.join()
    print("All tasks complete.")