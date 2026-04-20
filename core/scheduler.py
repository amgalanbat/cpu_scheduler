from core.algorithms import fcfs, sjf, round_robin, srt, preemptive_priority, preemptive_priority_aging

ALGORITHMS = {
    "FCFS":     fcfs,
    "SJF":      sjf,
    "SRT":      srt,
    "RR":       round_robin,
    "PP":       preemptive_priority,
    "PP+Aging": preemptive_priority_aging,
}


class SimulationResult:
    def __init__(self, timeline, processes, total_time, cpu_utilization, avg_waiting_time, avg_turnaround_time):

        self.timeline = timeline
        self.processes = processes
        self.total_time = total_time 
        self.cpu_utilization = cpu_utilization
        self.avg_waiting_time = avg_waiting_time
        self.avg_turnaround_time = avg_turnaround_time

    def summary(self):
        lines = []
        lines.append(f"Simulation ran for {self.total_time} ticks.")
        lines.append(f"CPU was busy {self.cpu_utilization}% of the time.")
        lines.append(f"On average, processes waited {self.avg_waiting_time} ticks before running.")
        lines.append(f"On average, processes took {self.avg_turnaround_time} ticks from arrival to finish.")

        finished = [p for p in self.processes if p.finish_time is not None]

        if finished:
            most_waited = max(finished, key=lambda p: p.waiting_time)
            least_waited = min(finished, key=lambda p: p.waiting_time)
            lines.append(f"'{most_waited.name}' waited the longest ({most_waited.waiting_time} ticks).")
            lines.append(f"'{least_waited.name}' waited the least ({least_waited.waiting_time} ticks).")

        starving = [p for p in finished if p.waiting_time > self.avg_waiting_time * 2]
        if starving:
            names = ", ".join(p.name for p in starving)
            lines.append(f"Starvation warning: {names} waited more than double the average")

        return "\n".join(lines)

    def best_process(self):
        finished = [p for p in self.processes if p.finish_time is not None]
        if not finished:
            return None
        return min(finished, key=lambda p: p.turnaround_time)

    def worst_process(self):
        finished = [p for p in self.processes if p.finish_time is not None]
        if not finished:
            return None
        return max(finished, key=lambda p: p.waiting_time)


class Scheduler:
    def __init__(self, algorithm="FCFS", quantum=2):
        if algorithm not in ALGORITHMS:
            raise ValueError(
                f"Unknown algorithm '{algorithm}'. "
                f"Choose from: {list(ALGORITHMS)}"
            )
        self.algorithm = algorithm
        self.quantum = quantum
        self.processes = []

    def add_process(self, process):
        self.processes.append(process)

    def reset(self):
        self.processes = []

    def run(self):
        if not self.processes:
            raise ValueError("No processes to schedule.")

        if self.algorithm == "RR":
            timeline = ALGORITHMS[self.algorithm](
                self.processes, self.quantum
            )
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
    
    def describe(self):
        descriptions = {
            "FCFS": "First Come First Serve - Processes are ran in the order that they arrive. Simple, but can cause long wait times.",
            "SJF": "Shortest Job First - The process with the shortest burst time is chosen. Minimizes wait time, but can starve long processes.",
            "SRT": "Shortest Remaining Time - SJF but preemptive. A new shorter processes can interrupt the current running one.",
            "RR": f"Round Robin - Each process gets an equal time each and run in loops. Fair, but adds overhead.",
            "PP": "Preemptive Priority - Highest priority process always runs first. Low priority processes may starve.",
            "PP+Aging": "Preemptive Priority with Aging - PP but the waiting processes gradually gain priority to prevent starvation.",
        }
        return descriptions.get(self.algorithm, "Unknown algorithm")