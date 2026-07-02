# vLLM 源码研读笔记 (Ran Ye)

> 目的：读懂 vLLM，补 Python + 分布式推理知识，为面试积累"能讲真代码"的素材，并为第一个 PR 做准备。
> **方法论：自顶向下**——先搞懂项目是什么/痛点/效果（阶段0），再画架构分类地图（阶段1），
> 然后逐个精读强项子系统（阶段2），最后动手第一个 PR（阶段3）。**不一上来就钻细节。**
> 无 GPU，聚焦 Python 逻辑层（v1/core、entrypoints），编译层用 `VLLM_USE_PRECOMPILED=1` 跳过。

## 阅读顺序（自顶向下）
| 阶段 | 笔记 | 内容 | 状态 |
|---|---|---|---|
| 0 总览 | [00-project-overview.md](00-project-overview.md) | 是什么 / 痛点(KV显存浪费60-80%) / PagedAttention / 效果(24x) | ✅ |
| 1 架构地图 | [01-architecture-map.md](01-architecture-map.md) | 子系统分类表 + 请求数据流 + 学习计划 | ✅ |
| 2 细节·调度 | [02-scheduler.md](02-scheduler.md) | `schedule()` 两阶段循环、抢占、prefix caching | ✅ 待校对 |
| 2 细节·KV | 03-kv-cache.md | block_pool + kv_cache_manager 分页块分配 | ⬜ |
| 2 细节·引擎 | 04-engine.md | EngineCore 主循环 | ⬜ |
| 2 细节·API | 05-api-server.md | entrypoints/openai 请求处理 | ⬜ |
| 3 贡献 | 06-first-pr.md | 选 issue + PR 流程记录 | ⬜ |

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
> 详见 [01-architecture-map.md](01-architecture-map.md) 的子系统分类表。

## 进度日志
- 2026-07-02：fork + clone，配好 origin/upstream，建 study 分支。
- 2026-07-02：（走了弯路：一上来就钻调度器细节）纠正为**自顶向下**。
- 2026-07-02：完成阶段0 总览 + 阶段1 架构地图；调度器笔记归位为阶段2(02-scheduler.md)。
