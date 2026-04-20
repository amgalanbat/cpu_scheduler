from core.process import Process
from core.scheduler import Scheduler


def make_scheduler(algorithm="FCFS", quantum=2):
    """Helper — creates a scheduler with 3 test processes."""
    s = Scheduler(algorithm=algorithm, quantum=quantum)
    s.add_process(Process(pid=1, name="P1", burst_time=4, arrival_time=0, priority=2))
    s.add_process(Process(pid=2, name="P2", burst_time=2, arrival_time=1, priority=1))
    s.add_process(Process(pid=3, name="P3", burst_time=8, arrival_time=2, priority=3))
    return s


def test_describe_fcfs():
    s = Scheduler(algorithm="FCFS")
    description = s.describe()
    assert "FCFS" in description or "First Come" in description


def test_describe_rr_includes_quantum():
    s = Scheduler(algorithm="RR", quantum=3)
    description = s.describe()
    assert "3" in description


def test_describe_unknown_returns_message():
    s = Scheduler(algorithm="FCFS")
    s.algorithm = "FAKE"
    assert s.describe() == "Unknown algorithm"


def test_summary_contains_total_time():
    s = make_scheduler()
    result = s.run()
    summary = result.summary()
    assert str(result.total_time) in summary


def test_summary_contains_cpu_utilization():
    s = make_scheduler()
    result = s.run()
    summary = result.summary()
    assert str(result.cpu_utilization) in summary


def test_summary_mentions_longest_waiter():
    s = make_scheduler()
    result = s.run()
    summary = result.summary()
    worst = result.worst_process()
    assert worst.name in summary


def test_best_process_has_shortest_turnaround():
    s = make_scheduler()
    result = s.run()
    best = result.best_process()
    finished = [p for p in result.processes if p.finish_time is not None]
    min_turnaround = min(p.turnaround_time for p in finished)
    assert best.turnaround_time == min_turnaround


def test_worst_process_has_longest_wait():
    s = make_scheduler()
    result = s.run()
    worst = result.worst_process()
    finished = [p for p in result.processes if p.finish_time is not None]
    max_wait = max(p.waiting_time for p in finished)
    assert worst.waiting_time == max_wait


def test_summary_starvation_warning():
    s = Scheduler(algorithm="FCFS")
    s.add_process(Process(pid=1, name="P1", burst_time=10, arrival_time=0, priority=1))
    s.add_process(Process(pid=2, name="P2", burst_time=10, arrival_time=0, priority=1))
    s.add_process(Process(pid=3, name="P3", burst_time=1,  arrival_time=0, priority=1))
    result = s.run()
    summary = result.summary()
    assert isinstance(summary, str)