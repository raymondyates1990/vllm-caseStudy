# vLLM 源码研读笔记 (Ran Ye)

> 目的：读懂 vLLM 核心（调度器 / KV 块管理 / 服务层），补 Python + 分布式推理知识，
> 为面试积累"能讲真代码"的素材，并为第一个 PR 做准备。
> 无 GPU，聚焦 Python 逻辑层（v1/core、entrypoints），避开 kernels/csrc。

## 分支约定
- `main`   —— 保持干净，只跟官方 upstream 同步；PR 从这里切功能分支。
- `study`  —— 本分支，放所有 `_notes/` 研读笔记。**不用于提 PR。**

同步官方更新：
```bash
git checkout main
git fetch upstream
git merge upstream/main
git push origin main
```

开一个新 PR（从干净 main 切）：
```bash
git checkout main && git pull upstream main
git checkout -b fix/<简短描述>
# 改代码 + 加测试...
git commit -s -m "..."   # -s 是 DCO 签名，vLLM 必须
git push origin fix/<简短描述>
# 去 GitHub 开 PR 到 vllm-project/vllm
```

## 阅读地图（黄金区，无 GPU）
| # | 主题 | 文件 | 笔记 |
|---|------|------|------|
| 01 | 调度器 Scheduler | `vllm/v1/core/sched/scheduler.py`, `request_queue.py` | ✅ [01-scheduler.md](01-scheduler.md) |
| 02 | KV 块管理 | `vllm/v1/core/block_pool.py`, `kv_cache_manager.py` | 待写 |
| 03 | OpenAI API 服务层 | `vllm/entrypoints/openai/api_server.py` | 待写 |
| 04 | LLMEngine 引擎 | `vllm/v1/engine/` | 待写 |

## 进度日志
- 2026-07-02：fork + clone 完成，配好 origin/upstream，建 study 分支与笔记结构。
- 2026-07-02：读完 `schedule()` 两阶段主循环（RUNNING 抢占 + WAITING 准入 + prefix caching），写完 01 笔记。
