# Mini-projects: implement vLLM concepts in Python (active learning)

> Fixes the "Python is passive" gap. After reading each Core module, **implement** the matching kata,
> then run it to self-check. All are pure Python, CPU-only, ~30-90 min each. Building > reading.

| # | File | Module | Builds | Status |
|---|---|---|---|---|
| A | [01_free_block_queue.py](01_free_block_queue.py) | M3.1 | doubly-linked O(1) free-list allocator | skeleton ready |
| B | [02_preemption_victim.py](02_preemption_victim.py) | M2.4 | PRIORITY vs FCFS victim selection | skeleton ready |
| C | 03_unified_scheduler.py | M2.1 | two-phase schedule() with token budget | planned |
| D | 04_request_state_machine.py | M2.3 | RequestStatus transitions | planned |
| E | 05_prefix_block_cache.py | M3.3 | content-hash block map + ref counting | planned |

How to use: open the file, implement the `# TODO` bodies, run `python 0X_....py`. It prints
`ALL TESTS PASSED` when correct. Then compare your design to the real vLLM source cited in the docstring.
These are learning artifacts (they live on the `study` branch and are never PR'd upstream).
