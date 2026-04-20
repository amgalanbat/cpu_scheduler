import time
import copy
from PyQt6.QtCore import QThread, pyqtSignal
from core.process import Process
from core.scheduler import Scheduler

class SimulationWorker(QThread):
    tick_ready = pyqtSignal(dict, list)
    finished = pyqtSignal(object)

    def __init__(self, processes, algorithm, quantum, speed=0.3):
        super().__init__()
        self.processes = processes
        self.algorithm = algorithm
        self.quantum = quantum
        self.speed = speed
        self._running = True

    def run(self):
        scheduler = Scheduler(algorithm=self.algorithm, quantum=self.quantum)
        for p in self.processes:
            scheduler.add_process(p)

        result = scheduler.run()

        for i, event in enumerate(result.timeline):
            if not self._running:
                break
            current_tick = event["tick"]
            running_pid = event["pid"]

            snapshot = []
            for p in result.processes:
                if p.finish_time is not None and p.finish_time <= current_tick + 1:
                    state = "finished"
                elif p.pid == running_pid:
                    state = "running"
                elif p.arrival_time <= current_tick \
                        and (p.finish_time is None or p.finish_time > current_tick):
                    state = "ready"
                else:
                    state = "new"

                display = type('obj', (object,), {
                    'pid': p.pid,
                    'name': p.name,
                    'burst_time':p.burst_time,
                    'arrival_time': p.arrival_time,
                    'priority': p.priority,
                    'remaining_time': max(0, p.burst_time - max(0, current_tick - (p.start_time or current_tick))),
                    'state': state,
                    'finish_time': p.finish_time,
                    'start_time': p.start_time,
                    'waiting_time': p.waiting_time,
                    'turnaround_time': p.turnaround_time,
                    'process_type': p.process_type,
                    'is_starving': getattr(p, 'is_starving', False),
    
                })()
                snapshot.append(display)

            self.tick_ready.emit(event, snapshot)
            time.sleep(self.speed)

        if self._running:
            self.finished.emit(result)

    def stop(self):
        self._running = False