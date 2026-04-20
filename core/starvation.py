STARVATION_THRESHOLD = 8

def apply_aging(processes, current_tick, aging_rate=1):
    """
    For every process in READY state, increment wait time.
    If waited too long, mark as starving.
    Aging reduces aged_priority every few ticks to boost scheduling chance.
    """
    for p in processes:
        state = p.state.value if hasattr(p.state, 'value') else p.state

        if state == "ready":
            if p.wait_since is None:
                p.wait_since = current_tick

            waited = current_tick - p.wait_since

            if waited >= STARVATION_THRESHOLD:
                p.is_starving = True

            if waited > 0 and waited % 3 == 0:
                p.aged_priority = max(0, p.aged_priority - aging_rate)

        elif state == "running":
            p.wait_since = current_tick
            p.is_starving = False

def get_starving_processes(processes):
    return [p for p in processes if p.is_starving]

def reset_starvation(processes):
    for p in processes:
        p.is_starving = False
        p.wait_since = None
        p.aged_priority = p.priority