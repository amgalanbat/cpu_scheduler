from core.process import Process
from core.algorithms import fcfs
from core.algorithms import srt, preemptive_priority


def test_fcfs_basic():
    processes = [
        Process(pid=1, name="P1", burst_time=4, arrival_time=0),
        Process(pid=2, name="P2", burst_time=3, arrival_time=1),
        Process(pid=3, name="P3", burst_time=2, arrival_time=2),
    ]

    timeline = fcfs(processes)

    # P1 runs ticks 0-3, P2 runs 4-6, P3 runs 7-8
    assert processes[0].finish_time == 4
    assert processes[1].finish_time == 7
    assert processes[2].finish_time == 9

    # Waiting time checks
    assert processes[0].waiting_time == 0
    assert processes[1].waiting_time == 3
    assert processes[2].waiting_time == 5

def test_fcfs_respects_arrival_time():
    processes = [
        Process(pid=1, name="P1", burst_time=2, arrival_time=5),
    ]
    timeline = fcfs(processes)
    # CPU should idle until tick 5
    assert processes[0].start_time == 5
    assert processes[0].finish_time == 7

from core.algorithms import sjf, round_robin

def test_sjf_picks_shortest():
    processes = [
        Process(pid=1, name="P1", burst_time=8, arrival_time=0),
        Process(pid=2, name="P2", burst_time=4, arrival_time=1),
        Process(pid=3, name="P3", burst_time=2, arrival_time=2),
    ]
    sjf(processes)
    # P1 runs first (already running), then P3 (shortest), then P2
    assert processes[0].finish_time == 8
    assert processes[2].finish_time == 10  # P3 runs after P1
    assert processes[1].finish_time == 14  # P2 runs last

def test_round_robin_quantum():
    processes = [
        Process(pid=1, name="P1", burst_time=5, arrival_time=0),
        Process(pid=2, name="P2", burst_time=3, arrival_time=0),
    ]
    round_robin(processes, quantum=2)
    # P1: 0-2, P2: 2-4, P1: 4-6, P2: 6-7, P1: 7-8
    assert processes[0].finish_time == 8
    assert processes[1].finish_time == 7


def test_srt_preempts():
    """P1 starts first but P2 arrives with shorter remaining time and preempts."""
    processes = [
        Process(pid=1, name="P1", burst_time=6, arrival_time=0),
        Process(pid=2, name="P2", burst_time=2, arrival_time=1),
    ]
    timeline = srt(processes)
    # P1 runs tick 0, P2 arrives at 1 with shorter remaining — preempts
    # P2 runs ticks 1-2, P1 resumes ticks 3-7
    assert timeline[0]["pid"] == 1  # tick 0: P1
    assert timeline[1]["pid"] == 2  # tick 1: P2 preempts
    assert timeline[2]["pid"] == 2  # tick 2: P2 continues
    assert timeline[3]["pid"] == 1  # tick 3: P1 resumes
    assert processes[1].finish_time == 3  # P2 finishes first

def test_preemptive_priority_preempts():
    """Higher priority process (lower number) preempts lower priority."""
    processes = [
        Process(pid=1, name="P1", burst_time=5, arrival_time=0, priority=3),
        Process(pid=2, name="P2", burst_time=3, arrival_time=2, priority=1),
    ]
    timeline = preemptive_priority(processes)
    # P1 runs ticks 0-1, P2 arrives at tick 2 with higher priority — preempts
    assert timeline[0]["pid"] == 1
    assert timeline[1]["pid"] == 1
    assert timeline[2]["pid"] == 2  # P2 preempts at tick 2
    assert processes[1].finish_time == 5  # P2 finishes before P1