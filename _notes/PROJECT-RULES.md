# vLLM 学习项目 · 项目级规则 (PROJECT RULES)

> 本仓库是学习用 fork。以下规则对本项目长期有效，AI 助手每次协作都应遵守。

## 分支
- **`main`**：保持干净，只跟官方 `upstream` 同步；将来提 PR 从这里切功能分支。
- **`study`**：**纯学习分支，永不 merge 回 `main`**。所有 `_notes/` 学习笔记、reflection 都提交到这里。
- `_notes/` 及学习产物**不加入 .gitignore**（要长期留存、可回看）。

remotes：`origin` = 我的 fork（raymondyates1990/vllm-caseStudy），`upstream` = vllm-project/vllm。

## 每次对话结束的固定动作
1. 把本次 reflection / 学习记录写进 `_notes/`（[REFLECTIONS.md](REFLECTIONS.md) + 相应笔记）。
2. `git add _notes` → `git commit -s -m "..."`（`-s` 是 DCO 签名）。
3. **`git push origin study`**（每次都要 push，别只 commit）。

## 方法论（自顶向下 + 基于源码）
1. **先整体后细节**：00 是什么/痛点/效果 → 01 架构分类地图 → 02+ 子系统细节 → 第一个 PR。不要一上来钻某个函数。
2. **自顶向下必须读真实源码**：不能只靠 md/博客/论文，要顺着入口（`run_busy_loop` → `step` → `schedule`）读代码骨架，带着理解再展开。
3. **聚焦无 GPU 的强项子系统**：调度 / KV 管理 / engine / API / 分布式协调 / LoRA / 可观测；避开 kernels/csrc/model_executor（需 GPU，用 `VLLM_USE_PRECOMPILED=1` 跳过编译）。

## 语言规则（项目级）
- 本项目所有记录（`_notes/` 下文档、反思、摘要、计划、提交说明）统一使用**英文**，便于后续共享。
- 我们与 AI 助手的实时对话继续使用**中文**。
- 从本次起新增记录按此规则执行；已有历史中文记录后续可逐步迁移到英文。

## PR 工作流（将来用）
```bash
git checkout main && git pull upstream main
git checkout -b fix/<描述>
# 改代码 + 加测试
git commit -s -m "..."
git push origin fix/<描述>   # 再去 GitHub 对 vllm-project/vllm 开 PR
```
