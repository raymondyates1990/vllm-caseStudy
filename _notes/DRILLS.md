# Active-Learning Drills (predict → verify)

> Fixes the "read-only = passive" gap. Do these OUT LOUD or on paper, commit to an answer, THEN check.
> Priority convention in vLLM: **lower `priority` number = more important** (served first). The preemption
> victim under PRIORITY is `max(running, key=(priority, arrival_time))` = the **largest** priority number
> (least important). Under FCFS the victim is `running.pop()` = the **most-recently-added** (LIFO).

## How to use (active-learning method)
1. **Predict first**: write your answer before reading code. Prediction errors are where learning happens.
2. **Verify**: run the cited test / trace the code; compare.
3. **Space it**: revisit — Week 1 (days 1-3), Week 2 (days 4-7), Week 3 (days 8-14). Re-do drills you missed.
4. **Rate confidence 1-5** after each; re-drill anything < 4.

---

## Drill 1 — PREDICT-SCHEDULER-STATE  (module M2.1)
**Given**: `max_num_seqs=3`, `max_num_scheduled_tokens (token_budget)=200`.
- running = [R1 (needs 150 new tokens), R2 (needs 100 new tokens)]
- waiting = [R3 (prompt 120 tokens, no cache), R4 (prompt 90 tokens)]
- KV blocks: plenty free.

**Predict**: (a) In phase 1, how many tokens are scheduled for R1 and R2? (b) How much budget remains for phase 2? (c) Does R3 get admitted, and with how many tokens?

**Answer**: (a) Phase 1 schedules RUNNING first: R1 gets `min(150, 200)=150`; budget →50; R2 gets `min(100,50)=50` (clamped by remaining budget), budget →0. (b) 0 tokens left. (c) Phase 2 loop condition needs `token_budget>0`; it's 0, so **R3/R4 are NOT admitted this step** — they wait. This shows the token budget throttles admission and that RUNNING has priority over new WAITING work.
**Verify**: add prints for `token_budget` and per-request `num_new_tokens` in a local copy of `tests/v1/core/test_scheduler.py`.

---

## Drill 2 — PREDICT-PREEMPTION-VICTIM  (module M2.4)
**Given**: phase 1 needs 1 more block but 0 are free, so a running request must be preempted.
- running = [R1 (priority=10), R2 (priority=5), R3 (priority=8)] (all arrived at distinct times)

**Predict**: Which request is preempted under (a) PRIORITY policy? (b) FCFS policy?

**Answer**: (a) PRIORITY: victim = `max(running, key=(priority, arrival_time))` = **R1 (priority=10)** — the *largest* priority number = *least* important. (Not R2! R2 has the smallest number = most important = protected.) (b) FCFS: victim = `running.pop()` = **R3** (the most-recently-added, LIFO), regardless of priority. The victim is freed (blocks reclaimed), set to `PREEMPTED`, `num_computed_tokens=0` (recompute on resume), and prepended to `waiting`.
**Verify**: `tests/v1/core/test_scheduler.py::test_preempt_during_execution` (adapt priorities).

---

## Drill 3 — PREDICT-CACHE-HITS  (module M3.3)
**Given**: block size = 16 tokens. R1 has prompt = [system(32 tokens)] + [userA(16 tokens)] → 3 full blocks, all cached after R1 runs. R2 arrives with prompt = [same system(32)] + [userB(16)].

**Predict**: (a) How many blocks can R2 reuse via prefix caching? (b) What happens to the block that differs? (c) Is any shared block mutated?

**Answer**: (a) R2 reuses the **2 system blocks** (identical content → identical hash → cache hit; `ref_cnt`++). (b) The 3rd block (userB ≠ userA) is a **new** allocation — different content hash, no hit. (c) **No mutation**: v1 block tables are append-only and cached full blocks are immutable; R2 just maps its logical blocks 0-1 to the shared physical blocks and appends a new block 2. (This is the v1 realization of copy-on-write.)
**Verify**: `tests/v1/core/test_prefix_caching.py` — trace the block allocation + `ref_cnt`.

---

## Drill 4 — TRACE-THE-REQUEST  (module M1.3)
**Task**: On paper, trace two concurrent requests R1, R2 across 3 `EngineCore.step()` calls. For each step mark: which are in `running` vs `waiting`, any status transition (WAITING→RUNNING→FINISHED/PREEMPTED), the step where prefix caching helps R2 (if they share a prompt), and which process/thread each hop runs in (frontend vs engine; input/main/output thread).
**Verify**: compare against your annotated call chain in [01-architecture-map.md](01-architecture-map.md) §1.5.

---

## Tricky questions (answer, then check)
1. **Q**: Under FCFS, if the only running request is the one just scheduled this step, is it preempted when the next request can't fit? **A**: No — preemption in phase 1 fires only when an *already-running* request needs blocks it can't get; a brand-new admission that can't fit simply isn't admitted (phase 2 `break`). Preemption protects progress, it doesn't thrash the just-scheduled request.
2. **Q**: Prefix caching is ON but a prompt was never seen before — reuse or new blocks? **A**: New blocks; a cache *miss* just allocates fresh blocks (and caches them for later).
3. **Q**: Can a request go RUNNING → WAITING directly? **A**: No — the path is RUNNING → PREEMPTED → (prepended to) waiting. PREEMPTED is the explicit intermediate state; a plain RUNNING never silently reverts to WAITING.

---
_Drills date: 2026-07-02 (round 17). Answers verified against scheduler.py / block_pool semantics reviewed in rounds 5-7._
