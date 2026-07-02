# 02 · Scheduler 调度器研读（阶段 2 细节）

> 前置：先读 [00-project-overview.md](00-project-overview.md) 和 [01-architecture-map.md](01-architecture-map.md)。
> 文件：`vllm/v1/core/sched/scheduler.py`（2368 行）、`request_queue.py`、`interface.py`
> 核心方法：`schedule()`（393–1131）是 vLLM continuous batching 的心脏。

## 0. 一句话心智模型

vLLM 调度器**没有"prefill 阶段 / decode 阶段"之分**。每个请求只有两个数：
- `num_computed_tokens`：已经算完的 token 数
- `num_tokens_with_spec`：目标 token 数 = prompt + 已生成 output + 投机(spec) token

每一步 `schedule()` 就是**在 token 预算内，尽量让每个请求的 `num_computed_tokens` 往 `num_tokens_with_spec` 追**。
这一个抽象同时覆盖了：chunked prefill、prefix caching、speculative decoding。非常优雅。

```
        num_computed_tokens ────────────►  num_tokens_with_spec
        [=========已算=========|--本步要算 num_new_tokens--|--还没排到--]
                               ↑ token_budget 夹住每步能算多少
```

## 1. 核心状态（来自 `__init__` 68–335）

| 字段 | 含义 | 映射我的经验 |
|---|---|---|
| `self.requests: dict[str, Request]` | 所有在册请求 | 请求登记表 |
| `self.waiting` | **等待队列**，按 policy 排序（FCFS / priority） | 准入队列 |
| `self.running: list[Request]` | 正在跑的批 | in-flight batch |
| `self.skipped_waiting` | 本步跳过的等待请求（依赖未就绪等） | 二级缓冲队列 |
| `max_num_running_reqs` (= `max_num_seqs`) | 最大并发请求数 | 并发上限 |
| `max_num_scheduled_tokens` | **每步 token 预算** | 容量/限流闸 |
| `self.policy` (`SchedulingPolicy`) | FCFS 或 PRIORITY | soft-throttling 的准入策略 |
| `kv_cache_manager` | KV 块分配器（见 02 笔记） | 内存池/块分配器 |
| `connector` | KV Connector：跨节点 P/D 分离 + KV offload | 分布式状态迁移 |

## 2. `schedule()` 两阶段算法

### 阶段一：先调度 RUNNING（已在跑的请求，437 起）
```
token_budget = max_num_scheduled_tokens
for request in self.running:          # 遍历在跑的
    num_new_tokens = num_tokens_with_spec + placeholders - num_computed_tokens
    num_new_tokens = min(num_new_tokens, token_budget, 剩余model_len)
    while True:
        new_blocks = kv_cache_manager.allocate_slots(request, num_new_tokens)
        if new_blocks is not None:    # 要到 KV 块 → 可调度
            break
        # 要不到块（KV 内存满）→ 抢占最低优先级请求
        if policy == PRIORITY:
            preempted = max(running, key=lambda r: (r.priority, r.arrival_time))
        else:  # FCFS：抢最后进来的
            preempted = running[-1]
        释放 preempted 的块，放回 waiting  # 之后可重算/恢复
    token_budget -= num_new_tokens
```

### 阶段二：再调度 WAITING（新请求准入，~600 起）
```
while waiting 非空 and token_budget > 0 and 并发未满:
    request = waiting.peek_request()
    # 约束检查：
    #  - blocked 状态（等远端 KV）→ 跳到 skipped_waiting
    #  - max_loras：若已排的 LoRA 数达上限且本请求是新 LoRA → 跳过
    # prefix caching：找已缓存 token
    new_computed_blocks, num_local_cached = kv_cache_manager.get_computed_blocks(request)
    num_external = connector.get_num_new_matched_tokens(...)   # 远端缓存
    num_computed_tokens = num_local_cached + num_external
    num_new_tokens = request.num_tokens - num_computed_tokens  # 只算没缓存的
    new_blocks = kv_cache_manager.allocate_slots(request, num_new_tokens, new_computed_blocks)
    if new_blocks is None:  # 块不够 → 停止收新请求（break）
        break
    running.append(request); waiting.pop_request()
```

## 3. 几个精妙设计点（面试可讲）

1. **抢占即准入控制**：KV 块（显存）不够时，踢掉优先级最低 / 最后进来的请求，释放其 KV 块给更该跑的请求。等价于我做过的 soft-throttling / 过载保护，只是资源换成了显存块。
2. **`continue` 而非 `break`**（阶段一 num_new_tokens==0 时）：注释明说 *"do not strictly follow FCFS, allow lower-priority requests to be scheduled"*——**故意打破严格 FCFS 避免队头阻塞**，让能跑的先跑。经典调度权衡。
3. **prefix caching**：多个请求共享相同前缀（如同一 system prompt）时，`get_computed_blocks()` 命中已缓存的 KV 块，`num_new_tokens` 直接扣掉，省掉重复 prefill 计算。→ 见 `block_pool.py` 的 `BlockHashToBlockMap`。
4. **统一抽象**：prefill/decode/chunked-prefill/spec-decode 全靠 "追 num_computed_tokens" 一套逻辑，无分支特判。
5. **token_budget + max_num_seqs 双约束**：既限每步算力（token），又限并发（请求数），对应吞吐 vs 延迟的权衡。

## 4. 我的经验直连点（面试话术素材）
- `waiting`/`running` 双队列 + 抢占 ≈ 我做的**准入控制 + 过载保护**。
- `token_budget` ≈ 我做的**限流预算**（soft-throttling 的 Redis Lua 令牌）。
- `max_loras` 约束 ≈ **多租户资源隔离**。
- KV Connector 的 P/D 分离 / KV offload ≈ **分布式状态迁移**（我熟的方向）。

## 5. 待深挖 / 下一步
- [ ] `kv_cache_manager.allocate_slots()` 与 `block_pool.py` 的块分配细节 → 写 **02 笔记**
- [ ] `update_from_output()`（1493–1835）：模型跑完后如何更新请求状态、判 EOS/停止
- [ ] `request_queue.py`：FCFS vs priority 队列的具体实现（peek/pop/prepend）
- [ ] `async_scheduler.py`：异步调度如何与主循环叠 batch
- [ ] 找一个和调度器/文档相关的 `good first issue`

---
_研读日期：2026-07-02_
