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

## Round 4 — Slice: note 04 §8 distributed / two-plane
Subagent confirmed ALL major claims accurate and precisely verified the mechanisms: control plane = `rpc_broadcast_mq` (MessageQueue/ShmRingBuffer in shm_broadcast.py) broadcasting SchedulerOutput; data plane = NCCL via PyNcclCommunicator (cuda_communicator.py:304); TP/PP/DP/EP all real in ParallelConfig. Judged the control/data-plane dichotomy "novel and correct."
- ✅ Added NCCL backend caveat (GPU=NCCL; CPU/XPU/Ray = torch.distributed/Gloo/custom).
- ✅ Refined "every layer" → TP-split layers (RowParallel all-reduce / ColumnParallel all-gather, tp_size>1).
- ✅ Added Ray nuance (RayExecutorV2 extends Multiproc + reuses MQ vs RayDistributedExecutor compiled DAG).
- No errors; §8 validated as source-accurate and insightful.

## Round 5 — Slice: note 02 scheduler (was "review pending")
Thorough subagent audit: judged "exemplary / EXACT MATCH". Verified against scheduler.py: no prefill/decode phase (docstring 396-406), all core-state fields, PRIORITY victim `max(running, key=(priority,arrival_time))` (546-548), FCFS victim `running.pop()` (569), full phase-2 flow (636-942), the exact "continue not break" comment (524-526), BlockHashToBlockMap (block_pool.py:34).
- ✅ Fixed `__init__` line range 68-335 → 69-334 (class at 68, def at 69).
- ✅ Added FCFS-LIFO preemption clarification (victim = most-recently-added, protects oldest/most-progressed).
- ✅ Marked note 02 as reviewed; updated README + TEACHING-PLAN M2.1 status and QA gap #2 (closed).
- Note: subagent's second "issue" (docstring line range) was critiquing my prompt's approximation, not the note — no change.
- No HIGH/MEDIUM errors. Note 02 APPROVED.

## Round 6 — Slice: plan M2.3 / M2.4 source refs
Subagent confirmed line refs 1493 (update_from_output) and 1136 (_preempt_request) are CORRECT; all 7 M2.4 claims exact (free blocks:1143, status=PREEMPTED:1148, num_computed_tokens=0:1149, prepend to waiting:1157, victim selection:545-563). Provided full 12-value RequestStatus enum and exact test names.
- ✅ Enriched M2.3: replaced the 3-state simplification with the real 12-state RequestStatus (incl. WAITING_FOR_* + PREEMPTED + FINISHED_* family); added refs request.py:323, _handle_stopped_request:1860, _update_request_with_output:1878; added streaming-resumable nuance.
- ✅ Added exact test names: test_stop_via_update_from_output (L578), test_preempt_during_execution (L930).
- ✅ Enriched M2.4 with the exact preemption line chain (1143/1148/1149/1157).
- No errors found; both modules' source refs validated.

## Round 7 — Slice: plan M3.1 / M3.2 / M3.3 (KV cache)
Subagent verified ALL symbols/claims correct with exact refs: KVCacheBlock (kv_cache_utils.py:126, ref_cnt:138, prev/next_free_block:144), FreeKVCacheBlockQueue doubly-linked w/ sentinels + O(1) remove, BlockPool.get_new_blocks:714/free_blocks:614/touch:603, BlockHashToBlockMap (block_pool.py:31), allocate_slots returns None on failure (kv_cache_manager.py:476), get_computed_blocks:202. All 4 test files + both design docs exist.
- ✅ Reframed CoW (note00 §3 + M3.3 self-check) to v1 reality: append-only block table, immutable cached blocks, diverging requests allocate NEW blocks; paper/v0 byte-copy CoW was a worker-layer concept. (Corrects my Round-1 wording.)
- ✅ Marked `paged_attention.md` HISTORICAL (its header warns so); made `prefix_caching.md` the authoritative M3 doc.
- ✅ Fixed symbol locations: KVCacheBlock/FreeKVCacheBlockQueue live in kv_cache_utils.py (not block_pool.py); added exact method names to M3.1.
- Plan judged ready to write note 03. No HIGH errors.

## Round 8 — Slice: plan M1.2 frontend + M1.3 e2e
Subagent verified ALL claims PASS; traced the full 16-hop flow in correct order. Key confirmations: detokenization runs in the FRONTEND process (`output_processor.py:388`; engine emits only raw token IDs); ZMQ client BINDS ROUTER:521 + PULL:526 (async zmq.asyncio) while engine CONNECTS DEALER/PUSH; async_llm add_request:280, generate:524, abort:709; SSE via text/event-stream.
- ✅ Enriched M1.2: frontend-detokenization fact, ZMQ bind/connect asymmetry, exact line refs.
- ✅ Refined M1.3 chain to place detokenize in the frontend + added a self-check on it.
- ✅ Synced the ZMQ bind/connect + async detail into note 04 §6.
- No errors; both modules validated, ready to write note 05.

## Round 9 — Slice: BUG-HUNTING.md
Subagent verified against docs/contributing/README.md: AI-assist policy summary, DCO `-s`, the exact no-GPU "rely on CI" quote, dev-install `VLLM_USE_PRECOMPILED=1 uv pip install -e .`, Python 3.12, all 4 cited test files, pre-commit workflow, and job-board links — all CORRECT.
- ✅ ACCEPTED HIGH: §6 PR-prefix checklist was incomplete (5 of 9). Added full official set ([Bugfix]/[CI/Build]/[Doc]/[Model]/[Frontend]/[Kernel]/[Core]/[Hardware][Vendor]/[Misc]) + no-GPU focus/avoid note.
- ✅ Added bonus CPU-friendly test targets (test_reset_prefix_cache_e2e, test_kv_cache_metrics).
- Rest of guide validated as doc-accurate.
