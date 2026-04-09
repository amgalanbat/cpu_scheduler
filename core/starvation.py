from typing import List
from core.process import Process, ProcessState

STARVATION_THRESHOLD = 8

def apply_aging(processes: List[Process], current_tick: int, aging_rate: int = 1):
    """
    For every process in READY state, increment wait time.
    If waited too long, mark as starving.
    Aging reduces aged_priority every few ticks to boost scheduling chance.
    """
    for p in processes:
        if p.state == ProcessState.READY:
            if p.wait_since is None:
                p.wait_since = current_tick

            waited = current_tick - p.wait_since

            # mark as starving if left too long
            if waited >= STARVATION_THRESHOLD:
                p.is_starving = True

            # aging - reduce priority number and increase urgency every 3 ticks
            if waited > 0 and waited % 3 == 0:
                p.aged_priority = max(0, p.aged_priority - aging_rate)

        elif p.state == ProcessState.RUNNING:
            # reset when it finally runs
            p.wait_since = current_tick
            p.is_starving = False

def get_starving_processes(processes: List[Process]) -> List[Process]:
    return [p for p in processes if p.is_starving]

def reset_starvation(processes: List[Process]):
    for p in processes:
        p.is_starving = False
        p.wait_since = None
        p.aged_priority = p.priority