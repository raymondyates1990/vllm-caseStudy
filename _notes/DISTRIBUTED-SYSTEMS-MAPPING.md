# vLLM ↔ Distributed-Systems Mapping (leverage my background)

> Purpose: compress learning by mapping my 10 yrs of SSIS / ADF / ADMS (scheduling, admission control,
> capacity, fault isolation, multi-tenancy) onto vLLM. Use these as **interview stories** and as a fast
> on-ramp: I'm not learning these ideas from scratch, only their new form.

## Core mappings
| My background (SSIS / ADF / ADMS) | vLLM equivalent | Note |
|---|---|---|
| Data-flow buffers: fixed-size, pooled, reused via a free list | **KV blocks** + `FreeKVCacheBlockQueue` (doubly-linked free list, O(1) reuse) | Same slab/free-list allocator idea; resource is GPU memory pages |
| Pipeline re-evaluates which buffers to drain each tick (not "wait for all data") | **Continuous batching**: `schedule()` re-decides the running set every GPU step | No static batch; prefill+decode mixed each step |
| ADMS soft-throttling / admission control (token bucket, backpressure) | **`token_budget` (max_num_scheduled_tokens) + `max_num_seqs`** dual constraint | Per-step compute budget + concurrency cap |
| Overload protection: shed / evict low-priority work under pressure | **Preemption** (evict `max(priority)` under PRIORITY, LIFO under FCFS) when KV is full | Same admission-control instinct; victim → PREEMPTED → recompute on resume |
| Process/stage isolation, failure domains | **Engine process decoupling** + **control-plane (queues/ZMQ) vs data-plane (NCCL collectives)** | Crash/OOM in engine ≠ HTTP down; sync tensor comm can't be queue-decoupled |
| Multi-tenant isolation / fairness | **Multi-LoRA** + per-request `priority` + preemption | Serve many adapters/tenants on one engine |
| Dedup of shared work | **Prefix caching** (content-hashed KV blocks, ref-count, append-only) | Shared system prompts → reuse KV, huge cost save |
| Capacity planning / SLOs (throughput vs latency) | **TTFT / TPOT / goodput** + batch-size tradeoff (Part E2, Part F1) | Batching ↑ throughput but ↑ TTFT |
| Distributed state migration | **KV connectors / disaggregated prefill-decode (P/D)** | Move KV between prefill and decode pools |

## Reverse-engineering exercise (active)
Take one real ADMS/SSIS admission-control design I built and **re-express it as a vLLM scheduling policy**:
map my throttle signal → `token_budget`; my priority tiers → request `priority`; my shed policy → preemption
victim rule; my backpressure → phase-2 `break`. Write it out; it becomes a strong "why me" interview answer.

## Chinese-market context (measured)
- vLLM is one of the most widely adopted open-source LLM-serving engines in the Chinese AI industry; being
  able to discuss its internals is directly relevant to serving/infra roles at Chinese AI companies.
- The problems vLLM is engineered for — **multi-tenant contention, strict latency SLAs, KV-memory cost at
  scale** — are exactly the production pressures Chinese serving teams face. Frame my background as: "I've
  solved multi-tenant admission/overload before; vLLM applies the same discipline to GPU memory."
- Interview ammunition: browse vLLM GitHub issues/discussions for real production pain points (long-context
  memory, preemption tuning, P/D disaggregation) and have an opinion on 1-2.

## Glossary bridge (EN ↔ 中文, for Chinese-language interviews)
连续批处理 = continuous batching · 优先级抢占 = priority preemption · 准入控制 = admission control ·
令牌预算 = token budget · KV 缓存 = KV cache · 分页注意力 = PagedAttention · 前缀缓存 = prefix caching ·
控制面/数据面 = control/data plane · 张量并行 = tensor parallelism · 投机解码 = speculative decoding.

---
_Mapping date: 2026-07-02 (round 18)._
