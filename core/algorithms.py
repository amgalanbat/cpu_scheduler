from typing import List
from core.process import Process, ProcessState
import heapq


def fcfs(processes: List[Process]) -> List[dict]:
    """
    First Come First Served scheduling.
    Returns a list of tick events representing the execution timeline.
    """
    timeline = []
    current_time = 0

    # Sort by arrival time
    queue = sorted(processes, key=lambda p: p.arrival_time)

    for process in queue:
        # CPU idles if process hasn't arrived yet
        if current_time < process.arrival_time:
            current_time = process.arrival_time

        process.state = ProcessState.RUNNING
        process.start_time = process.start_time or current_time

        # Simulate each tick of execution
        for tick in range(process.burst_time):
            timeline.append({
                "tick": current_time,
                "pid": process.pid,
                "name": process.name,
                "state": ProcessState.RUNNING
            })
            current_time += 1

        process.remaining_time = 0
        process.finish_time = current_time
        process.state = ProcessState.FINISHED
        process.compute_stats()

    return timeline


def sjf(processes: List[Process]) -> List[dict]:
    """
    Shortest Job First (non-preemptive).
    At each decision point, picks the process with the smallest burst time.
    """
    timeline = []
    current_time = 0
    remaining = sorted(processes, key=lambda p: p.arrival_time)
    ready_queue = []
    i = 0

    while i < len(remaining) or ready_queue:
        # Load all processes that have arrived into the ready queue
        while i < len(remaining) and remaining[i].arrival_time <= current_time:
            p = remaining[i]
            heapq.heappush(ready_queue, (p.burst_time, p.pid, p))
            i += 1

        if not ready_queue:
            current_time = remaining[i].arrival_time
            continue

        _, _, process = heapq.heappop(ready_queue)
        process.state = ProcessState.RUNNING
        process.start_time = process.start_time or current_time

        for tick in range(process.burst_time):
            timeline.append({
                "tick": current_time,
                "pid": process.pid,
                "name": process.name,
                "state": ProcessState.RUNNING
            })
            current_time += 1

        process.remaining_time = 0
        process.finish_time = current_time
        process.state = ProcessState.FINISHED
        process.compute_stats()

    return timeline


def round_robin(processes: List[Process], quantum: int = 2) -> List[dict]:
    """
    Round Robin scheduling.
    Each process gets a fixed time quantum before being preempted.
    """
    from collections import deque

    timeline = []
    current_time = 0
    queue = deque()
    remaining = sorted(processes, key=lambda p: p.arrival_time)
    i = 0

    # Load first batch
    while i < len(remaining) and remaining[i].arrival_time <= current_time:
        queue.append(remaining[i])
        i += 1

    while queue:
        process = queue.popleft()
        process.state = ProcessState.RUNNING

        if process.start_time is None:
            process.start_time = current_time

        ticks = min(quantum, process.remaining_time)

        for tick in range(ticks):
            timeline.append({
                "tick": current_time,
                "pid": process.pid,
                "name": process.name,
                "state": ProcessState.RUNNING
            })
            current_time += 1

            # Check for newly arrived processes after each tick
            while i < len(remaining) and remaining[i].arrival_time <= current_time:
                queue.append(remaining[i])
                i += 1

        process.remaining_time -= ticks

        if process.remaining_time > 0:
            process.state = ProcessState.READY
            queue.append(process)
        else:
            process.finish_time = current_time
            process.state = ProcessState.FINISHED
            process.compute_stats()

    return timeline

def srt(processes: List[Process]) -> List[dict]:
    """
    Shortest Remaining Time — preemptive version of SJF.
    At every tick, the process with the least remaining time runs.
    If a new process arrives with shorter remaining time, it preempts.
    """
    import heapq
    timeline = []
    current_time = 0
    remaining = sorted(processes, key=lambda p: p.arrival_time)
    ready_queue = []
    i = 0
    total_ticks = sum(p.burst_time for p in processes)
    ticks_done = 0

    while ticks_done < total_ticks:
        # Load all arrived processes
        while i < len(remaining) and remaining[i].arrival_time <= current_time:
            p = remaining[i]
            p.state = ProcessState.READY
            heapq.heappush(ready_queue, (p.remaining_time, p.pid, p))
            i += 1

        if not ready_queue:
            current_time += 1
            continue

        # Pick shortest remaining time
        _, _, process = heapq.heappop(ready_queue)

        if process.start_time is None:
            process.start_time = current_time

        process.state = ProcessState.RUNNING
        timeline.append({
            "tick": current_time,
            "pid": process.pid,
            "name": process.name,
            "state": ProcessState.RUNNING
        })

        process.remaining_time -= 1
        current_time += 1
        ticks_done += 1

        if process.remaining_time == 0:
            process.finish_time = current_time
            process.state = ProcessState.FINISHED
            process.compute_stats()
        else:
            process.state = ProcessState.READY
            # Re-push with updated remaining time
            heapq.heappush(ready_queue, (process.remaining_time, process.pid, process))

    return timeline


def preemptive_priority(processes: List[Process]) -> List[dict]:
    """
    Preemptive Priority Scheduling.
    Lower priority number = higher priority.
    At every tick, highest priority ready process runs.
    Preempts if a higher priority process arrives.
    """
    import heapq
    timeline = []
    current_time = 0
    remaining = sorted(processes, key=lambda p: p.arrival_time)
    ready_queue = []
    i = 0
    total_ticks = sum(p.burst_time for p in processes)
    ticks_done = 0

    while ticks_done < total_ticks:
        while i < len(remaining) and remaining[i].arrival_time <= current_time:
            p = remaining[i]
            p.state = ProcessState.READY
            heapq.heappush(ready_queue, (p.priority, p.pid, p))
            i += 1

        if not ready_queue:
            current_time += 1
            continue

        _, _, process = heapq.heappop(ready_queue)

        if process.start_time is None:
            process.start_time = current_time

        process.state = ProcessState.RUNNING
        timeline.append({
            "tick": current_time,
            "pid": process.pid,
            "name": process.name,
            "state": ProcessState.RUNNING,
            "priority": process.priority
        })

        process.remaining_time -= 1
        current_time += 1
        ticks_done += 1

        if process.remaining_time == 0:
            process.finish_time = current_time
            process.state = ProcessState.FINISHED
            process.compute_stats()
        else:
            process.state = ProcessState.READY
            heapq.heappush(ready_queue, (process.priority, process.pid, process))

    return timeline