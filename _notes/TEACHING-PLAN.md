# vLLM Learning · Master Teaching Plan

> Autonomous plan built 2026-07-02. Covers the 5 requested steps:
> (1) overall plan, (2) plan review, (3) per-step detailed elaboration, (4) implementation review, (5) bug-finding (in [BUG-HUNTING.md](BUG-HUNTING.md)).
> Language: English (project rule). Grounded in the real source tree of this repo.

---

## Part 0 · Goals, constraints, how to use

**Learner profile**: Ran Ye — 10 yrs distributed systems / scheduling / reliability (SSIS, ADF, ADMS at Microsoft). Strong on queues, admission control, capacity, fault isolation. Python is the weak spot (mostly AI-assisted so far). **No local GPU.**

**Goals** (priority order):
1. Understand vLLM deeply enough to *talk about real code* in interviews.
2. Strengthen Python + distributed-inference vocabulary.
3. Land a first merged PR (credibility signal).
4. Build reusable, English, shareable notes.

**Hard constraints**:
- No GPU -> focus on CPU-side logic (scheduler, KV mgmt, engine, API, config, tests). Read—not run—GPU code.
- Limited time (traveling, ~30 min/day) -> the plan has a **Core Path** (must-do) and an **Extended Path** (nice-to-have). Concrete calendar: [SCHEDULE.md](SCHEDULE.md) — Core Path ≈ 27.75 h ≈ 55 sessions (fits 60 days). Split L-modules into 30-min bites; do **dev-env (M6.1) in Week 1**; DEFER Part E2-E8 / F2 / mini-projects 03-05 to Day 50+; pick 2 of 5 mini-projects.
- `study` branch only; English notes; commit + push after each session.

**How to use**: go phase by phase. Each module has: Objective, Source, Official design doc, Key concepts, Hands-on, Self-check, Pitfalls, Interview hook, Effort. Do the **Hands-on** and answer the **Self-check** out loud — that is where real understanding forms. **Active learning beats re-reading**: use [DRILLS.md](DRILLS.md) (predict→verify + tricky questions with answers) and space your review (Week 1 days 1-3, Week 2 days 4-7, Week 3 days 8-14); re-do any drill you rate < 4/5 confidence.

---

## Part A · Step 1: The high-level curriculum

Seven phases, ordered to maximize the learner's strengths first (skeleton + scheduler), then broaden.

| Phase | Theme | Modules | Path | Status |
|---|---|---|---|---|
| 0 | Orientation | M0.1 what/pain/effect · M0.2 architecture map | Core | Done (notes 00,01) |
| 1 | Serving skeleton (control plane) | M1.1 engine core · M1.2 frontend · M1.3 e2e request trace | Core | Partial (note 04) |
| 2 | Scheduler (continuous batching) | M2.1 schedule() · M2.2 queues · M2.3 update_from_output · M2.4 preemption · M2.5 async | Core | Partial (note 02 = M2.1; M2.3/M2.4 sections TODO) |
| 3 | KV cache (PagedAttention) | M3.1 block_pool · M3.2 kv_cache_manager · M3.3 prefix caching · M3.4 hybrid/coordinator | Core | TODO (note 03) |
| 4 | Distributed compute plane | M4.1 executor tiers · M4.2 worker/model_runner (read-only) · M4.3 TP/PP/DP/EP · M4.4 KV connectors / P-D | Extended | TODO |
| 5 | Cross-cutting & features | M5.1 config · M5.2 LoRA · M5.3 observability · M5.4 structured output / spec decode | Extended | TODO |
| 6 | Contribution | M6.1 dev env · M6.2 run tests · M6.3 find issue · M6.4 make PR | Core | TODO |

**Sequencing rationale**: skeleton (1) gives a coordinate system; scheduler (2) and KV (3) are the learner's strongest, highest-interview-value, fully-no-GPU areas; distributed (4) leverages the distributed background but is broader; features (5) are breadth; contribution (6) can start as soon as Phase 2 is understood (docs/test PRs don't need the whole system).

**Milestones**:
- M-A "I can whiteboard the request data flow" (after Phase 1).
- M-B "I can explain continuous batching + preemption from real code" (after Phase 2).
- M-C "I can explain PagedAttention block allocation + prefix caching from real code" (after Phase 3).
- M-D "First PR opened" (after M6.3/M6.4; can overlap Phase 2-3).
- M-E "I can contrast control plane vs data plane and the 4 parallelisms" (after Phase 4).
- M-F "I can design a serving system backward from SLOs, and tell my distributed-systems → LLM-serving story" (Part F).

---

## Part B · Step 2: Plan review (critique + revisions)

**What is good**: strength-first ordering; no-GPU scoping; ties each topic to interview value; contribution can start early.

**Weaknesses found & fixes**:
1. *Too much breadth risk.* Phases 4-5 could balloon. **Fix**: mark them Extended; the Core Path is Phases 0-3 + 6. Interview-ready = Core Path.
2. *Reading without doing = shallow.* **Fix**: every module now has a **Hands-on** using the repo's real tests (`tests/v1/core/*`, `tests/v1/engine/*`) and a **Self-check** question set.
3. *"Understand" is unmeasurable.* **Fix**: milestones M-A..M-E are phrased as *"I can explain X from real code"* — a concrete bar.
4. *PR gated on finishing everything.* **Fix**: Phase 6 explicitly says a docs/test PR can be done right after Phase 2; do not wait for Phase 4-5.
5. *Python weakness not addressed inside the plan.* **Fix**: added a **Python-lens** note to each code-reading module (what Python idiom to learn there — dataclasses, `deque`, `Future`, context managers, `@property`, typing).
6. *No official-docs cross-check.* **Fix**: each module cites the matching `docs/design/*.md` so understanding is validated against maintainers' own words, not just my reading.
7. *Effort un估计.* **Fix**: each module has an Effort tag (S/M/L ≈ 1 / 2-3 / 4+ sessions of ~30 min).

**Revised Core Path (the must-do spine)**:
`M0.1 → M0.2 → M1.1 → M1.3 → M2.1 → M2.3 → M2.4 → M3.1 → M3.2 → M3.3 → M6.1 → M6.2 → M6.3 → M6.4`
(M1.2, M2.2, M2.5, M3.4, all of Phase 4-5 = Extended.)

**Why each Extended module is deferred** (so you can skip with confidence): M1.2 API details are breadth (M1.3 covers the high-level flow); M2.2 queue impl is optimization detail behind M2.1's logic; M2.5 async scheduling is latency-hiding, not a fundamental; M3.4 hybrid/Mamba KV is a specialized model feature; Phase 4 (distributed) is broad multi-node scale-out beyond single-node fundamentals; Phase 5 (config/LoRA/observability/spec-decode) are orthogonal features, not prerequisites. Revisit any of them after the Core spine if time permits.

---

## Part C · Step 3: Detailed module breakdowns

> Format per module — Objective · Source · Design doc · Key concepts · Python-lens · Hands-on · Self-check · Pitfalls · Interview hook · Effort.

### Phase 0 — Orientation (Done)

**M0.1 What / pain / effect** — Effort S — Done in [00-project-overview.md](00-project-overview.md).
- Objective: state the memory-bound pain (KV waste 60-80%), the PagedAttention idea, the effect (24x).
- Self-check: Why is LLM serving memory-bound, not compute-bound? What exactly is wasted, and how does paging fix it?
- Interview hook: "vLLM's core insight is OS paging applied to the KV cache."

**M0.2 Architecture map** — Effort S — Done in [01-architecture-map.md](01-architecture-map.md).
- Objective: draw the request data flow; classify subsystems by GPU-need and priority.
- Self-check: Name the 4 stages of one engine step. Which touch GPU?

### Phase 1 — Serving skeleton (control plane)

**M1.1 Engine core** — Effort M — mostly Done in [04-engine.md](04-engine.md).
- Objective: explain EngineCore composition, `step()` 4 stages, `run_busy_loop`, the 3-thread ZMQ IO, and control-plane vs data-plane.
- Source: `vllm/v1/engine/core.py` (EngineCore:96, step:479, step_with_batch_queue:519, run_busy_loop:1259, process_input_sockets:1484, process_output_sockets:1589).
- Design doc: `docs/design/arch_overview.md`, `docs/design/multiprocessing.md`.
- Key concepts: composition root; producer-consumer queues; GIL-release overlap; pipelining to remove PP bubbles; typed message protocol (ADD/ABORT/UTILITY/WAKEUP).
- Python-lens: `queue.Queue`, `threading.Thread(daemon=True)`, `concurrent.futures.Future`, `contextmanager`, `deque`.
- Hands-on: read `tests/v1/engine/test_engine_core.py`; map each test to a `step()`/lifecycle behavior.
- Self-check: Why separate input/output threads from the main loop? Why is `step_with_batch_queue` needed for PP? What does the startup handshake advertise and why?
- Pitfalls: conflating control plane (queues) with data plane (NCCL). Assuming single-node.
- Interview hook: "Control/data plane split: queues for requests, collectives for tensors."

**M1.2 Frontend (API + streaming)** — Effort M — *Extended* — TODO note 05.
- Objective: trace how an HTTP request becomes an `ADD` message and how tokens stream back.
- Source: `vllm/entrypoints/openai/api_server.py`; `vllm/v1/engine/async_llm.py` (`add_request`:280, `generate`:524, `abort`:709); `vllm/v1/engine/core_client.py` (async client BINDS `zmq.ROUTER`:521 + `zmq.PULL`:526 via `zmq.asyncio`); `vllm/v1/engine/output_processor.py` (detokenize:388) + `detokenizer.py`.
- Design doc: `docs/serving/*`, `docs/design/arch_overview.md`.
- Key concepts: OpenAI protocol mapping (`request.to_sampling_params()`); `AsyncLLM` request registration; **detokenization happens in the frontend process** (OutputProcessor owns tokenizer/detokenizer; the engine emits only raw token IDs); ZMQ **asymmetry** — client BINDS ROUTER/PULL, engine CONNECTS DEALER/PUSH (async); SSE streaming (`text/event-stream`); abort propagation (HTTP disconnect → CancelledError → `abort()` → ABORT msg).
- Python-lens: `asyncio`, async generators (`async for`), FastAPI/Starlette, `AsyncGenerator`.
- Hands-on: read `tests/v1/engine/test_async_llm.py`, `test_output_processor.py`.
- Self-check: Where is backpressure applied if a client reads slowly? How does an aborted HTTP connection reach the scheduler?
- Interview hook: "End-to-end async path with backpressure and abort handling."

**M1.3 End-to-end request trace** — Effort S — Core — Exercise (no new note; annotate 01).
- Objective: follow ONE prompt through the whole system and be able to explain each hop + which process/thread it runs in.
- Deliverable (this is "done"): in [01-architecture-map.md](01-architecture-map.md) §1.5, write the 5 phases below, each with the **verified `file:line`**:
  1. Ingress: curl → FastAPI → `AsyncLLM.add_request` → ZMQ ADD (client ROUTER→engine DEALER) → `input_queue`.
  2. Admission: `input_queue` → `scheduler.add_request` → waiting queue → `schedule()`.
  3. Execution: `schedule()` → `executor.execute_model` → `sample_tokens` (GPU).
  4. State update: `update_from_output` → RequestStatus transition.
  5. Egress: `output_queue` → ZMQ PUSH→client PULL → `output_processor` detokenize (frontend) → SSE.
- Self-check (no notes): explain each of the 5 hops aloud and name the process/thread. At which hop does prefix caching save work? preemption? detokenization?

### Phase 2 — Scheduler (continuous batching)

**M2.1 `schedule()` two-phase loop** — Effort L — [02-scheduler.md](02-scheduler.md) (reviewed round 5, source-accurate).
- Objective: explain the two phases (RUNNING first w/ preemption, then WAITING admission w/ prefix caching), token budget, the unified `num_computed_tokens` abstraction.
- Source: `vllm/v1/core/sched/scheduler.py` (__init__:68, schedule:393, phase-1 ~437, phase-2 ~600).
- Design doc: `docs/design/arch_overview.md` (scheduling section), `docs/design/prefix_caching.md`.
- Key concepts: token_budget vs max_num_seqs; chunked prefill via unified abstraction; `continue`-not-`break` (anti head-of-line-blocking).
- Python-lens: `dict`/`list` as queues, `min()` clamping, `max(key=...)`, walrus `:=`.
- Hands-on: read + run (CPU) `tests/v1/core/test_scheduler.py`; add a print in a local copy to watch `token_budget` per step.
- Self-check: Why no prefill/decode phases? When exactly does the scheduler break vs continue? How does `token_budget` interact with `max_num_seqs`?
- Pitfalls: thinking FCFS is strict (it isn't).
- Interview hook: "Preemption = admission control on GPU memory; budget = throttling." Analogy (fits my background): continuous batching is like an **SSIS data-flow pipeline** re-evaluating which buffers to drain each cycle instead of waiting for all data — the scheduler re-decides what runs each GPU step, mixing prefill and decode rather than strict phases.

**M2.2 `request_queue.py` (FCFS vs priority)** — Effort S — *Extended*.
- Objective: understand the two queue implementations behind `self.waiting`.
- Source: `vllm/v1/core/sched/request_queue.py`; `create_request_queue(policy)`.
- Hands-on: `tests/v1/core/test_priority_scheduler_random.py`.
- Self-check: What is the ordering key for priority? How are `peek/pop/prepend` used by the scheduler?
- Python-lens: `heapq` / `collections.deque` (queue impls), custom ordering via `Request.__lt__` (priority → arrival_time → request_id; `Request` is a plain class, not a dataclass).

**M2.3 `update_from_output()` (state machine)** — Effort M — Core.
- Objective: how sampled tokens update requests, stop/EOS detection, and what becomes output.
- Source: `scheduler.py:update_from_output:1493`, `_update_request_with_output:1878`, `_handle_stopped_request:1860`; `RequestStatus` enum in `vllm/v1/request.py:323`.
- Key concepts: the request state machine has **12 `RequestStatus` values**, not 3 — core flow `WAITING → RUNNING → FINISHED_*`, plus special waiting states `WAITING_FOR_STRUCTURED_OUTPUT_GRAMMAR`, `WAITING_FOR_REMOTE_KVS`, `WAITING_FOR_STREAMING_REQ`, and `PREEMPTED`. Finished states are anything `> PREEMPTED` (FINISHED_STOPPED / _LENGTH_CAPPED / _ABORTED / _IGNORED / _ERROR / _REPETITION). Stop detection via `check_stop()`; `_handle_stopped_request()` decides truly-done vs streaming-resumable; spec-decode acceptance.
- Hands-on: `tests/v1/core/test_scheduler.py::test_stop_via_update_from_output` (EOS / custom stop / max-length); `tests/v1/engine/test_output_processor.py`.
- Self-check: Enumerate the request states and legal transitions. What frees the KV blocks on finish? When does a request go to `WAITING_FOR_STREAMING_REQ` instead of finishing?
- Interview hook: "A request lifecycle state machine driven by model output each step."

**M2.4 Preemption & recompute** — Effort M — Core.
- Objective: what happens when KV runs out mid-flight; priority vs FCFS victim selection; recompute on resume.
- Source: `scheduler.py:_preempt_request:1136` (frees blocks via `_free_request_blocks`:1143 → sets `status=PREEMPTED`:1148 → `num_computed_tokens=0`:1149 → `waiting.prepend_request`:1157); victim selection :545-563.
- Hands-on: `tests/v1/core/test_scheduler.py::test_preempt_during_execution` (small `num_blocks` forces preemption; asserts `status==PREEMPTED` and that the preempted req still receives sampled tokens).
- Self-check: Which request is evicted under PRIORITY? under FCFS? What state does a preempted request return to, and what work is redone? (Answer: PREEMPTED → prepended to waiting; `num_computed_tokens` reset to 0 so its prefill is recomputed on resume.)
- Interview hook: "Overload protection: evict lowest-priority to protect the rest."

**M2.5 `async_scheduler.py`** — Effort M — *Extended*.
- Objective: how async scheduling overlaps schedule(step n+1) with execute(step n).
- Source: `vllm/v1/core/sched/async_scheduler.py`; `tests/v1/core/test_async_scheduler.py`.
- Interview hook: "Latency hiding by overlapping CPU scheduling with GPU compute."

> **Transition — from preemption to blocks (why Phase 3?)**: Phase 2 ended with "KV memory ran out, so we preempted a request and freed its blocks." But *what is a block*, and why is memory so scarce that preemption is needed? Phase 3 answers: KV **blocks** are the fixed-size memory pages of PagedAttention. Without them we would pre-reserve contiguous worst-case space per sequence (the 60-80% waste from note 00); with them we allocate on demand, share prefixes, and reclaim via preemption. M3.1 = what a block is; M3.2 = how the allocator hands them out (and returns None to trigger preemption); M3.3 = how sharing blocks (prefix caching) saves more.

### Phase 3 — KV cache management (PagedAttention)

**M3.1 `block_pool.py`** — Effort L — Core — TODO note 03.
- Objective: how physical KV blocks are represented, freed, and reused.
- Source: `vllm/v1/core/block_pool.py` — `BlockPool.get_new_blocks`/`free_blocks`/`touch`, `BlockHashToBlockMap`; and `vllm/v1/core/kv_cache_utils.py` — `KVCacheBlock` (has `ref_cnt`, `prev/next_free_block`), `FreeKVCacheBlockQueue` (doubly-linked, sentinel head/tail; `popleft_n`, `remove` = O(1) evict, `append_n`).
- Design doc: `docs/design/prefix_caching.md` (authoritative for v1). Note: `docs/design/paged_attention.md` is **historical** (its own header warns it no longer matches current code) — use for paper-level intuition only.
- Key concepts: free-list as a doubly-linked queue; block = fixed #tokens of K/V; append-only block tables; ref counting.
- Python-lens: linked-list via object refs, `@dataclass(slots=True)`, sentinel head/tail nodes.
- Hands-on: `tests/v1/core/test_kv_cache_utils.py`, `test_single_type_kv_cache_manager.py`.
- Self-check: How is a free block chosen? What makes eviction O(1)? Why append-only block tables?
- Interview hook: "A slab/free-list allocator for GPU memory pages — classic OS memory management."

**M3.2 `kv_cache_manager.py`** — Effort L — Core.
- Objective: the manager the scheduler calls — `allocate_slots`, `get_computed_blocks`.
- Source: `vllm/v1/core/kv_cache_manager.py`, `kv_cache_coordinator.py`.
- Key concepts: logical→physical mapping (block table); how `allocate_slots` returns None to trigger preemption; how cached prefixes are matched.
- Hands-on: trace `allocate_slots` from a `test_scheduler.py` case.
- Self-check: What is the contract of `allocate_slots` (inputs/outputs, None case)? How does it connect to `schedule()`?
- Interview hook: "The block table IS the page table; allocate_slots is on-demand paging."

**M3.3 Prefix caching** — Effort M — Core.
- Objective: how shared prefixes (system prompts) skip recompute.
- Source: `block_pool.py:BlockHashToBlockMap`, `kv_cache_utils.py` (hashing), `get_computed_blocks`.
- Design doc: `docs/design/prefix_caching.md`.
- Key concepts: content hashing of blocks; Copy-on-Write; ref counts; eviction interplay with the free queue; hit-rate stats.
- Hands-on: `tests/v1/core/test_prefix_caching.py`, `tests/v1/core/prefix_cache/`.
- Self-check: How is a cache hit computed? What guarantees safety when two requests share a block? When is a cached block evictable? Why is the v1 block table append-only, and why does that mean a diverging request allocates *new* blocks instead of mutating (copying) a shared one? How does `ref_cnt` gate eviction?
- Interview hook: "Content-addressed KV sharing with CoW — dedup + safety."

**M3.4 Hybrid / coordinator** — Effort L — *Extended*.
- Objective: multi-group / Mamba-hybrid KV management.
- Source: `kv_cache_coordinator.py` (HybridKVCacheCoordinator), `single_type_kv_cache_manager.py`.
- Design doc: `docs/design/hybrid_kv_cache_manager.md`.

### Phase 4 — Distributed compute plane (Extended)

**M4.1 Executor tiers** — Effort M.
- Source: `vllm/v1/executor/{uniproc_executor,multiproc_executor,ray_executor}.py`; `abstract.py`.
- Key concepts: UniProc (1 proc) → Multiproc (worker procs/GPU) → Ray (multi-node); command broadcast via shared-memory message queue (control), NCCL collectives (data).
- Design doc: `docs/design/multiprocessing.md`.
- Self-check: How does the executor send work to N workers? What is on the control vs data plane here?

**M4.2 Worker / model_runner (read-only)** — Effort M.
- Source: `vllm/v1/worker/*` (interfaces only — do NOT try to run; needs GPU).
- Objective: understand the *interface* the scheduler/executor drive, not the CUDA internals.
- Design doc: `docs/design/model_runner_v2.md`.

**M4.3 Parallelism TP/PP/DP/EP** — Effort L.
- Source: `vllm/distributed/*`, `parallel_config`.
- Key concepts: TP (per-layer all-reduce), PP (stage pipeline), DP (replicas+coordinator), EP (MoE).
- Self-check: For each, what is split and what is communicated?

**M4.4 KV connectors / disaggregated P/D** — Effort L.
- Source: `vllm/distributed/kv_transfer/*`, scheduler `connector` hooks.
- Design doc: `docs/design/nixl_kv_cache_lease.md`, `nixl_kv_push_connector.md`.
- Interview hook: "Distributed state migration — your wheelhouse."

### Phase 5 — Cross-cutting & features (Extended)

- **M5.1 Config** (`vllm/config/*`) — Effort S — easiest doc/typing PR surface.
- **M5.2 LoRA** (`vllm/lora/*`) — Effort M — multi-tenant isolation.
- **M5.3 Observability** (`vllm/tracing`, `vllm/v1/metrics`) — Effort S — `docs/design/metrics.md`; OTel background fit.
- **M5.4 Structured output / spec decode** (`vllm/v1/structured_output`, `vllm/v1/spec_decode`) — Effort M — `docs/design/logits_processors.md`.

### Phase 6 — Contribution (Core)

**M6.1 Dev env** — Effort M.
- Steps: WSL2 Ubuntu (Python 3.12) → `uv venv` → install vllm → `uv pip install -r requirements/dev.txt` → `uv pip install pre-commit>=4.5.1 && pre-commit install`.
- No-GPU install: follow `docs/getting_started/installation/cpu.md` and set `VLLM_TARGET_DEVICE=cpu` (without it the build auto-detects CUDA when torch has CUDA). The `VLLM_USE_PRECOMPILED=1` shortcut targets machines with a CUDA-capable torch; here the goal is only to *import vllm* and run the pure-logic CPU tests, not to run models.
- Design doc: `docs/contributing/README.md`, `docs/contributing/incremental_build.md`.
- Self-check: Can you import vllm and run one CPU unit test?

**M6.2 Run tests** — Effort S.
- No-GPU-friendly targets (pure logic; marked `pytest.mark.cpu_test`): `pytest tests/v1/core/test_scheduler.py`, `test_kv_cache_utils.py`, `test_prefix_caching.py`, `tests/v1/engine/test_output_processor.py`. (Verified: `tests/v1/engine/test_engine_core_client.py` **skips on non-CUDA** — not a CPU target.)
- Self-check: Which tests pass without a GPU? (scheduler / kv / prefix-cache / detokenizer logic should; anything importing the model runner or NCCL won't.)

**M6.3 Find an issue** — Effort M — see [BUG-HUNTING.md](BUG-HUNTING.md).

**M6.4 Make the PR** — Effort M.
- Branch from clean `main`; small change + test; `git commit -s` (DCO); pass `pre-commit`; push; open PR; respond to review.

---

## Part D · Step 4: Implementation review (QA of the plan)

Checklist — does every Core module have the required parts?

| Module | Objective | Source refs | Design doc | Hands-on (real test) | Self-check | Interview hook | Verdict |
|---|---|---|---|---|---|---|---|
| M0.1 | Y | note 00 | — | Q | Y | Y | OK (done) |
| M0.2 | Y | note 01 | — | Q | Y | Y | OK (done) |
| M1.1 | Y | core.py lines | arch/multiproc | test_engine_core | Y | Y | OK (note 04) |
| M1.3 | Y | call chain | arch | annotate 01 | Y | — | OK |
| M2.1 | Y | scheduler.py lines | arch/prefix | test_scheduler | Y | Y | OK (review 02) |
| M2.3 | Y | update_from_output:1493 | — | test_output_processor | Y | Y | OK |
| M2.4 | Y | _preempt_request:1136 | — | forced-preempt test | Y | Y | OK |
| M3.1 | Y | block_pool.py | paged_attention | test_kv_cache_utils | Y | Y | OK |
| M3.2 | Y | kv_cache_manager.py | paged_attention | trace from test | Y | Y | OK |
| M3.3 | Y | BlockHashToBlockMap | prefix_caching | test_prefix_caching | Y | Y | OK |
| M6.1-4 | Y | contributing docs | contributing | pytest targets | Y | — | OK |

**Gaps flagged**:
1. Note **03-kv-cache.md does not exist yet** — M3.1-3.3 point to it; must be written when reaching Phase 3. (Tracked in README index as TODO.)
2. ~~M2.1 note (02) review pending~~ — DONE (round 5): re-read against `scheduler.py`; preemption victim selection, two-phase loop, and prefix caching all verified accurate.
3. **M1.2/M2.5/Phase 4-5** are Extended and intentionally lighter; acceptable.
4. Design-doc claims should be **cross-checked against source** (methodology rule) rather than trusted blindly.
5. Effort tags are rough; recalibrate after the first two modules.
6. **M2.3/M2.4 lack dedicated reading material** — note 02 currently covers M2.1 (schedule loop) only. When reaching Phase 2, expand 02-scheduler.md with an `update_from_output` (state machine) section and a preemption/recompute section. (Core gap; tracked.)
7. **Python-lens lives only in the plan** — when writing each note (02/03/04/05), copy the relevant Python idioms into a short "Python idioms to learn" box with real `file:line`, to serve the Python-strengthening goal.

**QA verdict**: Core Path is complete and self-consistent; each Core module is actionable with a real test and a self-check. Safe to execute.

---

## Part E · Interview-breadth pack (added round 12)

The Core Path makes you deep on scheduling + KV. AI-infra interviews also probe **breadth**. These close the
highest-value gaps; all are **no-GPU-learnable** (config/interface/logic or reading-only) and each source below
was verified to exist. Tier = Core-breadth (do) vs Reading (skim for vocabulary).

| # | Topic | Tier | Source (no-GPU, verified) | Interview hook | Effort |
|---|---|---|---|---|---|
| E1 | **Chunked prefill** | Core-breadth | `scheduler.py` schedule() (`long_prefill_token_threshold`); fold into note 02 | "Split big prefills across steps so they don't stall decode / cause head-of-line blocking." | S |
| E2 | **Metrics & SLOs: TTFT / TPOT / goodput** | Core-breadth | `vllm/v1/metrics/` (perf.py, stats.py, prometheus.py) | "Batching trades TTFT for throughput; goodput = requests meeting SLO. Measure before optimizing." | S |
| E3 | **Speculative decoding** | Reading | `vllm/v1/spec_decode/`; acceptance in `scheduler.update_from_output` | "Draft N tokens, verify in one pass → fewer forward passes → lower TPOT." | M |
| E4 | **KV cache quantization** | Reading | `vllm/v1/kv_cache_interface.py:33` `KVQuantMode` | "FP8/INT8 KV shrinks memory → bigger batch; precision-vs-capacity tradeoff." | S |
| E5 | **Disaggregated prefill/decode (P/D)** | Core (for distributed bg) | `vllm/distributed/kv_transfer/`; scheduler `connector` hooks | "Prefill is latency-bound, decode throughput-bound → separate pools, migrate KV. (My SSIS/ADF pipeline-stage intuition.)" | M |
| E6 | **Sampling params** | Reading | `vllm/sampling_params.py` | "temperature/top-p/n; beam or n>1 multiplies memory+compute per request." | S |
| E7 | **Benchmarking & profiling** | Core-breadth | `vllm/benchmarks/` (throughput.py, latency.py) — read + `--help` on CPU; **full runs need a GPU/CI** | "I can tell if a setup is latency- or throughput-bound and propose a fix." | S |
| E8 | **torch.compile & CUDA graphs (concept)** | Reading | `docs/design/cuda_graphs.md`, `docs/design/torch_compile.md` | "Fixed batch shapes + captured graphs cut Python/launch overhead per step." | S |

Actions: fold **E1** into note 02 (Core); relabel **M4.4 = E5** "Core for a distributed-systems background"; write **34-glossary.md** (E2/E7 vocabulary + all key terms); **do E2+E7 hands-on once** (run `vllm/benchmarks/throughput.py --help`; add a `token_budget`/batch-size print to a scheduler test; read `vllm/v1/metrics/perf.py` for TTFT/TPOT).

---

## Part F · Interview performance: design framing + story (added round 15)

The Core Path makes you *explain* vLLM. Senior AI-infra interviews also test whether you can *design
backward from requirements* and *tell why your background fits*. These two skills separate "knows the code"
from "senior hire". Neither needs a GPU.

### F1 · System-design recipe: from SLOs to vLLM config
A repeatable backward-reasoning framework (rehearse it; apply to any design question):
1. **Clarify SLOs + workload**: TTFT target? TPOT target? request mix (prompt/output lengths)? concurrency? tiers?
2. **Measure current goodput** (% requests meeting SLO) — never optimize before measuring.
3. **Find the bottleneck**: latency-bound (prefill-heavy, TTFT high) vs throughput-bound (decode-heavy, TPOT high) vs memory-bound (frequent preemption/OOM, small batch).
4. **Turn the right knob** (one at a time, re-measure):

| Symptom | Knob | Direction |
|---|---|---|
| TTFT too high (prefill stalls) | chunked prefill (`long_prefill_token_threshold`); priority for interactive tier | split prefills; preempt batch tier |
| Throughput too low | `max_num_seqs`, token budget (`max_num_scheduled_tokens`), prefix caching | raise batch/budget |
| OOM / frequent preemption | block count (`gpu_memory_utilization`), KV quant (E4), shorter `max_model_len` | free memory |
| Mixed SLO tiers | request `priority` + preemption (M2.4) | high tier always runs; low tier preempts/re-queues |
| Shared prompts | prefix caching (M3.3) | dedupe KV |

5. **Scale out** only after single-node is tuned: TP (bigger model), P/D disaggregation (E5) to split latency vs throughput, DP replicas for more traffic.

**Worked example** — two tiers on 2 GPUs: interactive (0.5s TTFT) + batch (5s OK). Give interactive requests higher `priority`; the scheduler's preemption (M2.4) already lets them preempt batch under load; cap `max_num_seqs` to protect interactive TTFT; measure per-tier goodput; if batch throughput suffers, add a DP replica. This demonstrates reasoning from SLO → scheduler primitive.

### F2 · Narrative arc: distributed-systems background → LLM serving
Rehearse out loud (often the decisive "why you" answer):
- **Setup**: "10 years of systems design taught me it's all tradeoffs — latency vs throughput, admission vs utilization, isolation vs multiplexing."
- **Problem**: "LLM serving *looked* alien (GPUs, KV caches), but reading vLLM I saw the same problems in a new domain."
- **Evidence** (3 concrete mappings):
  1. SSIS/ADF dynamic scheduling ↔ vLLM **continuous batching** (re-decide each step, not static batches).
  2. ADMS soft-throttling / admission control ↔ **token budget + preemption** (evict lowest-priority under memory overload).
  3. Distributed fault isolation / process lifecycle ↔ **engine process decoupling + ZMQ handshake + control/data-plane split**.
- **Implication**: "So I bring fault-tolerance, multi-tenant isolation, and capacity modeling from day one — not a career pivot, the same discipline."

Keep a worked **STAR story per mapping**, from my real experience (fill in):
- *Situation/Task*: a real SSIS/ADMS overload or admission-control incident I owned.
- *Action*: how I throttled/shed/isolated (the mechanism).
- *Result*: the outcome + metric.
- *Bridge*: "— that's exactly vLLM's preemption/token-budget under KV pressure."
Full mapping table: [DISTRIBUTED-SYSTEMS-MAPPING.md](DISTRIBUTED-SYSTEMS-MAPPING.md). Reinforce concepts by coding them: [mini-projects/](mini-projects/README.md).

---

## Progress checklist (tick as you go)
> Each Core step is "done" only when you can explain it AND the cited CPU test passes.
- [ ] M1.1 done: `pytest tests/v1/engine/test_engine_core.py -v` (understand the flow it exercises)
- [ ] M1.3 e2e trace: 01 §1.5 annotated with `file:line` for all 5 hops; can explain each aloud
- [ ] M2.1 done: `pytest tests/v1/core/test_scheduler.py -v` passes; can explain two-phase loop
- [ ] M2.3 done: `pytest tests/v1/core/test_scheduler.py::test_stop_via_update_from_output`
- [ ] M2.4 done: `pytest tests/v1/core/test_scheduler.py::test_preempt_during_execution`
- [ ] M3.1 done: `pytest tests/v1/core/test_kv_cache_utils.py -v` passes; can explain free-list + O(1) evict
- [ ] M3.2 done: trace `allocate_slots()` through a `test_scheduler.py` case (note 03)
- [ ] M3.3 done: `pytest tests/v1/core/test_prefix_caching.py -v` passes
- [ ] M6.1 dev env up (one CPU test passes)
- [ ] M6.3 first issue chosen
- [ ] M6.4 first PR opened

_Plan date: 2026-07-02_
