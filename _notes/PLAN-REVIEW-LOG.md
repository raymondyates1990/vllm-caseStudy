# Plan & Content Review Log (20-round subagent audit)

> Each round: an independent read-only Explore subagent reads real source and critiques the teaching
> plan and/or content notes. I (the lead) evaluate every point, ACCEPT or REJECT with rationale, then
> edit the notes. Rounds 1-10 are slice-focused; rounds 11-20 are holistic. English per project rule.

Legend: ✅ ACCEPTED (applied) · ❌ REJECTED (with reason) · 🔶 PARTIAL (applied with modification)

---

## Round 1 — Slice: note 00 overview + M0.1/M0.2
Subagent verified claims against README, docs/design/paged_attention.md, prefix_caching.md, arch_overview.md, kv_cache_utils.py, core.py.
- ✅ Perf numbers (60-80%, 1.7GB, 24x, 2-4x) not in repo docs → added a **source footnote** (SOSP paper/blog, workload-dependent).
- ✅ CoW/ref-count under-specified → added code pointer (`KVCacheBlock.ref_cnt` in kv_cache_utils.py) + CoW-on-divergent-write wording.
- ✅ Append-only block table (v1) confirmed in prefix_caching.md → added M3.3 self-check on why append-only + when CoW triggers. (Confirms my earlier claim was correct.)
- ✅ 60-80% waste is workload-dependent → added a caveat line.
- ✅ Prefix-caching "2.2x" softened to "up to ~55% memory, higher throughput".
- ❌ REJECTED subagent's suggested "continuous batching ~2-4x / PagedAttention ~6-8x" split — it admitted the breakdown is NOT in repo docs; refused to write fabricated numbers. Kept only a qualitative "co-equal driver" note.
- Strengths confirmed: OS-paging analogy, 4-stage step(), on-demand allocation, self-checks — all accurate vs source.

## Round 2 — Slice: note 01 architecture map
Subagent verified all 6 source-line refs in §1.5 and all 13 subsystem dirs/GPU classes — all correct.
- ✅ Added a note on specialized out-of-scope subsystems (multimodal/reasoning/tokenizers/plugins).
- ✅ Fixed data-flow diagram: `sample_tokens()` is an executor method (`v1/executor/abstract.py`), relabeled + noted.
- ✅ §3: added the concrete alias fact `LLMEngine = V1LLMEngine` (old engine/ is a thin shim).
- 🔶 §1.5: added an "omitted for clarity" line (abort drain, grammar bitmask, draft-token post_step) — all confirmed real.
- No factual errors found; note judged source-accurate.

## Round 3 — Slice: note 04 engine skeleton (§0-7)
Subagent verified §1-6 all correct (composition, step 4-stage, step_with_batch_queue, run_busy_loop+1ms GIL yield, msg protocol, both IO threads incl. handshake fields). But raised a HIGH claim that the engine is NOT a separate process.
- ❌ REJECTED the HIGH claim. Source disproves it: `vllm/v1/engine/utils.py:165` uses `context.Process(target=EngineCoreProc.run_engine_core)` — default serving (VLLM_ENABLE_V1_MULTIPROCESSING) spawns a real OS process. The subagent conflated "internal 3 threads use queue.Queue" with "not a separate process."
- ✅ ACCEPTED its MEDIUM point: `input_queue`/`output_queue` are `queue.Queue` (thread queues) INSIDE the engine process; my "ZMQ/mp" shorthand was imprecise. Rewrote §0 to state the process/thread model precisely (process = ZMQ boundary; threads = queue.Queue).
- ✅ Added default-multiprocessing + in-process-mode nuance; added socket pairs (DEALER↔ROUTER, PUSH↔PULL).
- ✅ Fixed the same imprecision in note 01 §1.5.
- Lesson: subagent overreached from correct evidence to a wrong conclusion; source verification caught it.
