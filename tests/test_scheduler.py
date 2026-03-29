from core.process import Process
from core.scheduler import Scheduler

def test_scheduler_fcfs():
    s = Scheduler(algorithm="FCFS")
    s.add_process(Process(pid=1, name="P1", burst_time=4, arrival_time=0))
    s.add_process(Process(pid=2, name="P2", burst_time=2, arrival_time=1))
    result = s.run()
    assert result.total_time == 6
    assert result.cpu_utilization == 100.0
    assert len(result.timeline) == 6

def test_scheduler_rr():
    s = Scheduler(algorithm="RR", quantum=2)
    s.add_process(Process(pid=1, name="P1", burst_time=5, arrival_time=0))
    s.add_process(Process(pid=2, name="P2", burst_time=3, arrival_time=0))
    result = s.run()
    assert result.total_time == 8
    assert len(result.processes) == 2

def test_scheduler_rejects_unknown_algorithm():
    try:
        s = Scheduler(algorithm="FAKE")
        assert False, "Should have raised ValueError"
    except ValueError:
        pass

def test_scheduler_rejects_empty():
    s = Scheduler()
    try:
        s.run()
        assert False, "Should have raised ValueError"
    except ValueError:
        pass