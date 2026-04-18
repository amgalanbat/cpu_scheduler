from core.thread import Thread
from core.constants import ProcessState, ProcessType

class Process:
    def __init__(self, pid, name, memory_size = 10, cswitch_cost= 1):
        self.pid = pid
        self.name = name
        self.memory_size = memory_size
        self.cswitch_cost = cswitch_cost

        self.threads = []
        self.state = "ready"

    def add_thread(self, burst_time, arrival_time, priority = 0, name = ""):
        tid = len(self.threads) + 1

        if name == "":
            thread_name = f"{self.name} - T{tid}"
        else:
            thread_name = name

        new_thread = Thread(tid, thread_name, burst_time, arrival_time, priority, self.pid)

        self.threads.append(new_thread)
        return new_thread
    
    def is_finished(self):
        for t in self.threads:
            if not t.is_finished():
                return False
        return True
    
    def get_all_threads(self):
        return self.threads
    



