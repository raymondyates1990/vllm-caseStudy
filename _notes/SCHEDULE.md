# Study Schedule (30 min/day, ~60 days, travel-friendly)

> Reality check (round 19): the Core Path is ~27.75 h ≈ 55 sessions vs a 30 h / 60-day budget — **doable
> with discipline**. Rules: split big modules into 30-min bites, do dev-env in Week 1, DEFER breadth to Day 50+.

## Scope discipline (to actually finish)
- **DO (Core, non-negotiable)**: M0 → M1.1/M1.3 → M2.1 → M2.3 → M2.4 → M3.1 → M3.2 → M3.3 → M6, + Drills 1-4, + Part F1, + fold E1 into M2.1.
- **PICK 2 of 5 mini-projects** (recommend 01 free-block-queue + 02 preemption-victim). 03-05 optional.
- **DEFER to Day 50+ (only if ahead)**: Part E2-E8 (metrics, spec-decode, KV quant, sampling, benchmarking, CUDA graphs), Part F2 narrative polish, Phase 4-5.
- **AT-DESK PREREQUISITE**: do **M6.1 dev-env by Week 1 (Day ~8)** — catch WSL2/import failures early, not in Week 7.

## Split the big (L) modules into 30-min daily bites
- **M2.1a** phase-1 RUNNING loop + preemption (`scheduler.py:437-563`) · **M2.1b** phase-2 WAITING + token budget (`~600-700`) · **M2.1c** integration + run one test.
- **M3.1a** block concept · **M3.1b** `block_pool.py` · **M3.1c** `kv_cache_utils.py` free-list.
- **M3.2a** block-table recap · **M3.2b** `allocate_slots`/`get_computed_blocks`.

## 7-week calendar (each bullet ≈ one 30-min session)
- **W1 Foundation + setup**: M0.1+M0.2 · M1.1 · M1.3 trace · **M6.1 dev-env (at-desk)** · M6.2 pytest.
- **W2 Scheduler**: M2.1a · M2.1b · M2.1c · run `test_scheduler.py` · Drill 1 (predict scheduler state).
- **W3 Preemption**: M2.3 (state machine) · M2.4 (preemption) · Drill 2 (victim) · mini-project 02 (code it) · catch-up.
- **W4 Block pool**: M3.1a · M3.1b · M3.1c · run `test_kv_cache_utils.py` · mini-project 01 (optional).
- **W5 KV mgr + prefix**: M3.2a · M3.2b · M3.3 · Drill 3+4 · run `test_prefix_caching.py`.
- **W6 Issue + design**: M6.3 search issues · read chosen issue's code · F1 recipe · design exercise · PR prep.
- **W7 PR + buffer**: M6.4 open PR (`git commit -s`, pre-commit) · address review · buffer / F2 if energy.

**Checkpoints**: EOW1 env works + 1 CPU test passes · EOW2 continuous batching + budget · EOW3 preemption · EOW4 block allocation · EOW5 prefix caching · EOW6 issue + PR code ready · EOW7 PR opened.

## Minimum-viable path (~15 sessions, if time collapses)
M0 (2) → M1 + e2e (2) → M2.1 skim (3) → M2.4 + Drill 2 (2) → M3.1 + M3.3 (3) → M6.3 issue + F1 (3).
After these you can credibly discuss: PagedAttention + continuous batching, two-phase scheduler + preemption,
KV free-list + prefix caching, and the SSIS↔vLLM parallels. (Deep on scheduler/KV, shallow on the rest.)

## Travel vs at-desk split
- **Travel-safe (phone/tablet, reading + paper drills)**: all M0/M1 concept reads, M2/M3 code reading, Drills 1-4, M6.3 GitHub issue browsing.
- **At-desk (WSL2 + pytest)**: M6.1 install, all `pytest` hands-on, mini-projects, M6.4 PR.
- Suggested: do reading-heavy weeks (W1-2) while traveling; mix travel-read + at-desk-test W3-7.

## First-PR timing (realistic)
- **Docs/test PR by ~Day 40** (low risk, builds credibility) — e.g. `[Doc]` docstring for the 12 `RequestStatus` states.
- **Substantive fix by ~Day 60** (stretch) — a `[Core]` scheduler/KV edge-case test (see BUG-HUNTING).

---
_Schedule date: 2026-07-02 (round 19)._
