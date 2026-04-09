import psutil
import subprocess
import sys
import time
from dataclasses import dataclass, field
from typing import List, Optional
from PyQt6.QtCore import QThread, pyqtSignal

@dataclass
class ThreadInfo:
    thread_id: int
    status: str = "running"

@dataclass
class ChildProcessInfo:
    pid: int
    name: str
    cpu_percent: float
    memory_mb: float
    status: str

@dataclass
class ProfileSample:
    timestamp: float
    cpu_percent: float
    memory_mb: float
    status: str
    thread_count: int = 0
    child_count: int = 0
    threads: List[ThreadInfo] = field(default_factory=list)
    children: List[ChildProcessInfo] = field(default_factory=list)

@dataclass
class ProfileResult:
    script_path: str
    samples: List[ProfileSample]
    duration: float
    peak_cpu: float
    peak_memory_mb: float
    avg_cpu: float
    avg_memory_mb: float
    peak_threads: int
    peak_children: int
    exit_code: int

class ProfilerWorker(QThread):
    sample_ready = pyqtSignal(float, float, float, int, int)  # time, cpu, mem, threads, children
    finished = pyqtSignal(object)
    error = pyqtSignal(str)

    def __init__(self, script_path: str, interval: float = 0.1):
        super().__init__()
        self.script_path = script_path
        self.interval = interval
        self._running = True
        self.samples: List[ProfileSample] = []

    def run(self):
        try:
            process = subprocess.Popen(
                [sys.executable, self.script_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

            ps_process = psutil.Process(process.pid)
            start_time = time.time()
            time.sleep(0.05)

            while process.poll() is None and self._running:
                try:
                    cpu = ps_process.cpu_percent(interval=None)
                    mem = ps_process.memory_info().rss / (1024 * 1024)
                    status = ps_process.status()
                    elapsed = time.time() - start_time

                    # Collect thread info
                    threads = []
                    try:
                        for t in ps_process.threads():
                            threads.append(ThreadInfo(thread_id=t.id))
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass

                    # Collect child process info
                    children = []
                    try:
                        for child in ps_process.children(recursive=True):
                            try:
                                children.append(ChildProcessInfo(
                                    pid=child.pid,
                                    name=child.name(),
                                    cpu_percent=round(child.cpu_percent(), 1),
                                    memory_mb=round(
                                        child.memory_info().rss / (1024 * 1024), 2
                                    ),
                                    status=child.status()
                                ))
                            except (psutil.NoSuchProcess, psutil.AccessDenied):
                                pass
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass

                    sample = ProfileSample(
                        timestamp=round(elapsed, 2),
                        cpu_percent=round(cpu, 1),
                        memory_mb=round(mem, 2),
                        status=status,
                        thread_count=len(threads),
                        child_count=len(children),
                        threads=threads,
                        children=children
                    )
                    self.samples.append(sample)
                    self.sample_ready.emit(
                        elapsed, cpu, mem,
                        len(threads), len(children)
                    )

                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    break

                time.sleep(self.interval)

            process.wait()
            duration = time.time() - start_time

            if not self.samples:
                self.error.emit(
                    "No samples collected - script may have finished too quickly."
                )
                return

            result = ProfileResult(
                script_path=self.script_path,
                samples=self.samples,
                duration=round(duration, 2),
                peak_cpu=round(max(s.cpu_percent for s in self.samples), 1),
                peak_memory_mb=round(max(s.memory_mb for s in self.samples), 2),
                avg_cpu=round(
                    sum(s.cpu_percent for s in self.samples) / len(self.samples), 1
                ),
                avg_memory_mb=round(
                    sum(s.memory_mb for s in self.samples) / len(self.samples), 2
                ),
                peak_threads=max(s.thread_count for s in self.samples),
                peak_children=max(s.child_count for s in self.samples),
                exit_code=process.returncode
            )
            self.finished.emit(result)

        except FileNotFoundError:
            self.error.emit(f"Script not found: {self.script_path}")
        except Exception as e:
            self.error.emit(f"Profiler error: {str(e)}")

    def stop(self):
        self._running = False