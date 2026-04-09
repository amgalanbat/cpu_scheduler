from core.process import Process, ProcessState
from core.starvation import apply_aging, get_starving_processes, STARVATION_THRESHOLD

def test_starvation_detected():
    p = Process(pid=1, name="P1", burst_time=5, arrival_time=0, priority=5)
    p.state = ProcessState.READY
    p.wait_since = 0

    # Simulate waiting past threshold
    apply_aging([p], current_tick=STARVATION_THRESHOLD + 1)
    assert p.is_starving is True

def test_aging_reduces_priority():
    p = Process(pid=1, name="P1", burst_time=5, arrival_time=0, priority=9)
    p.state = ProcessState.READY
    p.wait_since = 0
    p.aged_priority = p.priority

    # After 3 ticks, priority should decrease
    apply_aging([p], current_tick=3)
    assert p.aged_priority < p.priority

def test_no_starvation_when_running():
    p = Process(pid=1, name="P1", burst_time=5, arrival_time=0)
    p.state = ProcessState.RUNNING
    apply_aging([p], current_tick=20)
    assert p.is_starving is False