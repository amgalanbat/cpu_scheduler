import time
import os
import tempfile

print("Memory and I/O growth test...")
chunks = []
temp_files = []

for i in range(8):
    # Write a 20MB temp file and read it back into memory
    size = 20 * 1024 * 1024
    data = bytes([i % 256]) * size

    tmp = tempfile.NamedTemporaryFile(delete=False)
    tmp.write(data)
    tmp.close()
    temp_files.append(tmp.name)

    # Read back into memory — this forces RSS commitment
    with open(tmp.name, "rb") as f:
        chunk = f.read()
    chunks.append(chunk)

    allocated = (i + 1) * 20
    print(f"Step {i+1}: ~{allocated}MB in memory")
    time.sleep(0.8)

print("Holding for 3 seconds...")
time.sleep(3)

print("Releasing...")
chunks.clear()
for f in temp_files:
    os.unlink(f)
time.sleep(1)
print("Done.")