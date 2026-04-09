from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

class ProcessState(Enum):
    NEW      = "new"
    READY    = "ready"
    RUNNING  = "running"
    WAITING  = "waiting"
    FINISHED = "finished"

class ProcessType(Enum):
    PROCESS = "process"
    THREAD  = "thread"

@dataclass
class Process:
    pid: int
    name: str
    burst_time: int
    arrival_time: int = 0
    priority: int = 0
    process_type: ProcessType = ProcessType.PROCESS
    state: ProcessState = ProcessState.NEW

    # Filled during simulation, manually hiigeed hereggu
    remaining_time: int = field(init=False)
    start_time: Optional[int] = field(default=None, init=False)
    finish_time: Optional[int] = field(default=None, init=False)
    waiting_time: int = field(default=0, init=False)
    turnaround_time: int = field(default=0, init=False)

    starvation_threshold: int = field(default=10, init=True)
    wait_since: Optional[int] = field(default=None, init=False)
    is_starving: bool = field(default=False, init=False)
    aged_priority: int = field(default=0, init=False)

    def __post_init__(self):
        self.remaining_time = self.burst_time
        self.aged_priority = self.priority

    # def __post_init__(self):
    #     self.remaining_time = self.burst_time

    @property
    def is_finished(self) -> bool:
        return self.remaining_time <= 0

    def compute_stats(self):
        if self.finish_time is not None and self.start_time is not None:
            self.turnaround_time = self.finish_time - self.arrival_time
            self.waiting_time = self.turnaround_time - self.burst_time