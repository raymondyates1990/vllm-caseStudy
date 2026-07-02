"""Mini-project B: preemption victim selection (study module M2.4).

Implement vLLM's preemption victim rule (see `scheduler.py:545-563`).

Priority convention in vLLM: **lower `priority` number = MORE important** (served first).
- PRIORITY policy: victim = the LEAST important running request
      = max(running, key=(priority, arrival_time))   # largest priority number, tie-break later arrival
- FCFS policy: victim = the most-recently-added running request = running[-1]

Fill in the `# TODO`, then run:  python 02_preemption_victim.py
Success prints: ALL TESTS PASSED
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Req:
    request_id: str
    priority: int        # lower = more important
    arrival_time: float  # earlier = more senior


def select_victim(running: list[Req], policy: str) -> Req:
    """Return the request to preempt when KV memory is full.

    policy is "PRIORITY" or "FCFS".
    """
    # TODO:
    #   if policy == "PRIORITY": return max(running, key=lambda r: (r.priority, r.arrival_time))
    #   if policy == "FCFS":     return running[-1]
    raise NotImplementedError


def _test():
    running = [Req("A", 10, 1.0), Req("B", 5, 2.0), Req("C", 8, 3.0)]

    v = select_victim(running, "PRIORITY")
    assert v.request_id == "A", (
        f"PRIORITY victim should be A (priority 10 = LEAST important), got {v.request_id}. "
        "Remember: larger priority number = less important."
    )

    v = select_victim(running, "FCFS")
    assert v.request_id == "C", f"FCFS victim should be C (most recently added), got {v.request_id}"

    # tie-break: equal priority -> the later arrival is the victim
    tie = [Req("X", 5, 1.0), Req("Y", 5, 2.0)]
    assert select_victim(tie, "PRIORITY").request_id == "Y"

    print("ALL TESTS PASSED")


if __name__ == "__main__":
    _test()
