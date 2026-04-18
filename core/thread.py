from core.constants import ProcessState

class Thread:
    def __init__(self, tid, name, burst_time, arrival_time, priority, parent_pid):
        self.tid = tid
        self.name = name
        self.burst_time = burst_time
        self.arrival_time = arrival_time
        self.priority = priority
        self.parent_pid = parent_pid

        self.remaining_time = burst_time
        self.state = "ready"
        self.start_time = None
        self.finish_time = None
        self.turnaround_time = 0
        self.waiting_time = 0
        self.response_time = 0

        self.wait_since = None
        self.is_starving = False
        self.aged_priority = priority

    def calc_stats(self):
        if self.start_time is not None and self.finish_time is not None:
            self.turnaround_time = self.finish_time - self.arrival_time
            self.waiting_time = self.turnaround_time - self.burst_time
            self.response_time = self.start_time - self.arrival_time
    
    def is_finished(self):
        return self.remaining_time <= 0
