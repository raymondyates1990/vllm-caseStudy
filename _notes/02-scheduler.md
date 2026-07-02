# 02 · Scheduler Deep-Dive (Stage 2 detail)

> Prereq: read [00-project-overview.md](00-project-overview.md) and [01-architecture-map.md](01-architecture-map.md) first.
> Files: `vllm/v1/core/sched/scheduler.py` (2368 lines), `request_queue.py`, `interface.py`
> Core method: `schedule()` (393-1131) is the heart of vLLM continuous batching.
> Status: reviewed 2026-07-02 (round 5) against `scheduler.py` — algorithm claims (two-phase loop, preemption victim selection, prefix caching) verified accurate.

## 0. One-line mental model

The vLLM scheduler has **no "prefill phase" vs "decode phase"**. Each request has just two numbers:
- `num_computed_tokens`: how many tokens are already computed
- `num_tokens_with_spec`: target token count = prompt + generated output + speculative (spec) tokens

Each `schedule()` step simply tries, **within the token budget, to let each request's `num_computed_tokens`
catch up to `num_tokens_with_spec`**. This single abstraction covers chunked prefill, prefix caching, and
speculative decoding at once. Very elegant.

```
        num_computed_tokens ------------->  num_tokens_with_spec
        [========= computed =========|-- this step: num_new_tokens --|-- not yet scheduled --]
                                     ^ token_budget caps how much per step
```

## 1. Core state (from `__init__`, lines 69-334)

| Field | Meaning | Maps to my experience |
|---|---|---|
| `self.requests: dict[str, Request]` | all registered requests | request registry |
| `self.waiting` | **waiting queue**, ordered by policy (FCFS / priority) | admission queue |
| `self.running: list[Request]` | the currently running batch | in-flight batch |
| `self.skipped_waiting` | waiting requests skipped this step (deps not ready, etc.) | secondary buffer queue |
| `max_num_running_reqs` (= `max_num_seqs`) | max concurrent requests | concurrency cap |
| `max_num_scheduled_tokens` | **per-step token budget** | capacity / throttle gate |
| `self.policy` (`SchedulingPolicy`) | FCFS or PRIORITY | soft-throttling admission policy |
| `kv_cache_manager` | KV block allocator (see note 03) | memory pool / block allocator |
| `connector` | KV Connector: cross-node P/D disaggregation + KV offload | distributed state migration |

## 2. The `schedule()` two-phase algorithm

### Phase 1: schedule RUNNING first (already-running requests, from line 437)
```
token_budget = max_num_scheduled_tokens
for request in self.running:          # iterate running requests
    num_new_tokens = num_tokens_with_spec + placeholders - num_computed_tokens
    num_new_tokens = min(num_new_tokens, token_budget, remaining_model_len)
    while True:
        new_blocks = kv_cache_manager.allocate_slots(request, num_new_tokens)
        if new_blocks is not None:    # got KV blocks -> schedulable
            break
        # cannot get blocks (KV memory full) -> preempt the lowest-priority request
        if policy == PRIORITY:
            preempted = max(running, key=lambda r: (r.priority, r.arrival_time))
        else:  # FCFS: preempt the most-recently-added
            preempted = running[-1]
        free preempted's blocks, put it back to waiting  # can recompute/resume later
    token_budget -= num_new_tokens
```

### Phase 2: then schedule WAITING (new-request admission, from ~line 600)
```
while waiting not empty and token_budget > 0 and concurrency not full:
    request = waiting.peek_request()
    # constraint checks:
    #  - blocked status (waiting for remote KV) -> move to skipped_waiting
    #  - max_loras: if scheduled LoRA count is at the cap and this is a new LoRA -> skip
    # prefix caching: find already-cached tokens
    new_computed_blocks, num_local_cached = kv_cache_manager.get_computed_blocks(request)
    num_external = connector.get_num_new_matched_tokens(...)   # remote cache
    num_computed_tokens = num_local_cached + num_external
    num_new_tokens = request.num_tokens - num_computed_tokens  # only compute the uncached part
    new_blocks = kv_cache_manager.allocate_slots(request, num_new_tokens, new_computed_blocks)
    if new_blocks is None:  # not enough blocks -> stop admitting new requests (break)
        break
    running.append(request); waiting.pop_request()
```

## 3. Subtle design points (interview talking points)

1. **Preemption is admission control**: when KV blocks (memory) run out, evict the lowest-priority / most-recently-added request and free its KV blocks for requests that should run. Equivalent to the soft-throttling / overload protection I built, just with memory blocks as the resource. Note: under FCFS the victim is the *most-recently-added* running request (`running.pop()`) — preemption is **LIFO**, which protects the oldest / most-progressed requests.
2. **`continue` instead of `break`** (phase 1, when num_new_tokens==0): the comment explicitly says *"do not strictly follow FCFS, allow lower-priority requests to be scheduled"* — **deliberately breaking strict FCFS to avoid head-of-line blocking**, letting runnable requests run first. A classic scheduling trade-off.
3. **prefix caching**: when multiple requests share a common prefix (e.g. the same system prompt), `get_computed_blocks()` hits already-cached KV blocks and subtracts them from `num_new_tokens`, saving redundant prefill compute. See `BlockHashToBlockMap` in `block_pool.py`.
4. **Unified abstraction**: prefill/decode/chunked-prefill/spec-decode all run on the single "chase num_computed_tokens" logic, with no special-case branches.
5. **token_budget + max_num_seqs dual constraint**: caps both per-step compute (tokens) and concurrency (request count), reflecting the throughput vs latency trade-off.

## 4. Direct links to my experience (interview material)
- `waiting`/`running` dual queues + preemption ~= **admission control + overload protection** I built.
- `token_budget` ~= the **throttling budget** I built (soft-throttling with Redis Lua tokens).
- `max_loras` constraint ~= **multi-tenant resource isolation**.
- KV Connector P/D disaggregation / KV offload ~= **distributed state migration** (a direction I know well).

## 5. To dig deeper / next
- [ ] `kv_cache_manager.allocate_slots()` and `block_pool.py` block allocation detail -> write **note 03**
- [ ] `update_from_output()` (1493-1835): how request state is updated after the model runs, EOS/stop detection
- [ ] `request_queue.py`: concrete FCFS vs priority queue implementation (peek/pop/prepend)
- [ ] `async_scheduler.py`: how async scheduling overlaps batches with the main loop
- [ ] Find a scheduler/doc-related `good first issue`

---
_Study date: 2026-07-02_
