import time
from PyQt6.QtCore import QThread, pyqtSignal
from core.process import Process
from core.scheduler import Scheduler

class SimulationWorker(QThread):
    tick_ready = pyqtSignal(dict, list)
    finished = pyqtSignal(object)

    def __init__(self, processes: list[Process], algorithm: str, quantum: int, speed: float = 0.3):
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

        for event in result.timeline:
            if not self._running:
                break
            self.tick_ready.emit(event, list(result.processes))
            time.sleep(self.speed)

        if self._running:
            self.finished.emit(result)

    def stop(self):
        self._running = False