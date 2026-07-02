# Reflections · 学习反思日志

> 每次对话后追加一条：这次学到什么、走了什么弯路、下次怎么改进。倒序（最新在上）。

## 2026-07-02 · 第 1 次（建立方法论 + 骨架）
**做了什么**
- fork + clone + 配 origin/upstream，建 `study` 分支与 `_notes/` 结构。
- 完成 00 总览（痛点=KV显存浪费60-80%，解法=PagedAttention，效果=vs HF 24x）。
- 完成 01 架构地图（子系统分类表 + 数据流），并**补上源码验证的骨架**：
  `run_busy_loop`→`EngineCore.step()`→`schedule/execute/sample/update`（带 file:line）。
- 02 调度器细节（`schedule()` 两阶段：RUNNING 抢占 + WAITING 准入 + prefix caching）。

**弯路 / 教训（用户纠正）**
1. ❌ 一上来就钻调度器细节 → ✅ 应自顶向下：先懂是什么/痛点/效果，再分类，再细节。
2. ❌ 自顶向下只读了 md/在线资料 → ✅ 必须**基于真实源码**读骨架，带着理解自顶向下。
3. ✅ 确立规则：`study` 永不 merge main，是纯学习分支；每次对话后 commit **且 push**；`_notes` 不 gitignore。

**下次改进**
- 每读一个子系统，先定位它在 `EngineCore.step()` 调用链里的位置，再展开实现。
- 继续阶段 2：03 KV 分页块管理（`block_pool.py` + `kv_cache_manager.py`），或先校对 02。
