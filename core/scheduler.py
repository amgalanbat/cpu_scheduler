from dataclasses import dataclass, field
from typing import List, Optional
from core.process import Process, ProcessState
from core.algorithms import fcfs, sjf, round_robin, srt, preemptive_priority

ALGORITHMS = {
    "FCFS": fcfs,
    "SJF": sjf,
    "RR": round_robin,
    "SRT": srt,
    "PP": preemptive_priority,
}
@dataclass
class SimulationResult:
    timeline: List[dict]
    processes: List[Process]
    total_time: int
    cpu_utilization: float
    avg_waiting_time: float
    avg_turnaround_time: float

class Scheduler:
    def __init__(self, algorithm: str = "FCFS", quantum: int = 2):
        if algorithm not in ALGORITHMS:
            raise ValueError(f"Unknown algorithm '{algorithm}'. Choose from: {list(ALGORITHMS)}")
        self.algorithm = algorithm
        self.quantum = quantum
        self.processes: List[Process] = []

    def add_process(self, process: Process):
        self.processes.append(process)

    def reset(self):
        self.processes = []

    def run(self) -> SimulationResult:
        if not self.processes:
            raise ValueError("No processes to schedule.")

        if self.algorithm == "RR":
            timeline = ALGORITHMS[self.algorithm](self.processes, self.quantum)
        else:
            timeline = ALGORITHMS[self.algorithm](self.processes)

        finished = [p for p in self.processes if p.finish_time is not None]
        if not finished:
            raise ValueError("No processes finished.")

        total_time = max(p.finish_time for p in finished)
        busy_ticks = len(timeline)
        cpu_utilization = (busy_ticks / total_time) * 100 if total_time > 0 else 0
        avg_waiting = sum(p.waiting_time for p in finished) / len(finished)
        avg_turnaround = sum(p.turnaround_time for p in finished) / len(finished)

        return SimulationResult(
            timeline=timeline,
            processes=self.processes,
            total_time=total_time,
            cpu_utilization=round(cpu_utilization, 2),
            avg_waiting_time=round(avg_waiting, 2),
            avg_turnaround_time=round(avg_turnaround, 2),
        )