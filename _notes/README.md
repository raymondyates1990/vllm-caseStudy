# vLLM Source Study Notes (Ran Ye)

> Goal: understand vLLM deeply, strengthen Python + distributed inference knowledge,
> collect "I can talk about real code" material for interviews, and prepare for a first PR.
> **Methodology: top-down** — first understand what/pain/effect (Stage 0), then draw the
> architecture map (Stage 1), then read strength subsystems in detail (Stage 2), then make
> a first PR (Stage 3). **Do not dive into details first.**
> No GPU: focus on the Python logic layer (v1/core, entrypoints); skip the compiled layer
> with `VLLM_USE_PRECOMPILED=1`.

## Reading order (top-down)
| Stage | Note | Content | Status |
|---|---|---|---|
| 0 Overview | [00-project-overview.md](00-project-overview.md) | What / pain (KV memory waste 60-80%) / PagedAttention / effect (24x) | Done |
| 1 Architecture | [01-architecture-map.md](01-architecture-map.md) | Subsystem table + request data flow + study plan | Done |
| 2 Detail·Scheduler | [02-scheduler.md](02-scheduler.md) | `schedule()` two-phase loop, preemption, prefix caching | M2.1 done (reviewed r5); M2.3/M2.4 TODO |
| 2 Detail·KV | 03-kv-cache.md | block_pool + kv_cache_manager paged block allocation | TODO |
| 2 Detail·Engine | [04-engine.md](04-engine.md) | EngineCore + EngineCoreProc: process/thread/ZMQ skeleton | Done |
| 2 Detail·API | 05-api-server.md | entrypoints/openai request handling | TODO |
| 3 Contribute | 06-first-pr.md | Pick issue + PR workflow record | TODO |

**Planning & meta docs**: [TEACHING-PLAN.md](TEACHING-PLAN.md) (full curriculum + review + detailed modules + QA + interview-breadth pack) · [SCHEDULE.md](SCHEDULE.md) (30-min/day 7-week calendar + minimum-viable path + travel split) · [BUG-HUNTING.md](BUG-HUNTING.md) (find a bug / first-PR guide + AI-assist policy) · [DRILLS.md](DRILLS.md) (predict→verify active-learning drills + answers) · [DISTRIBUTED-SYSTEMS-MAPPING.md](DISTRIBUTED-SYSTEMS-MAPPING.md) (my background → vLLM + 中文 context) · [mini-projects/](mini-projects/README.md) (Python coding katas) · 34-glossary.md (planned: TTFT/TPOT/goodput + key terms).

## Branch convention
> Full rules: [PROJECT-RULES.md](PROJECT-RULES.md). Per-conversation reflections: [REFLECTIONS.md](REFLECTIONS.md).
- `main`  — kept clean, only synced with official `upstream`; branch PRs from here.
- `study` — this branch, holds all `_notes/` study notes. **Learning only, never merged into `main`.**
- Project records are written in English; conversation stays in Chinese (see PROJECT-RULES).

Sync with upstream:
```bash
git checkout main
git fetch upstream
git merge upstream/main
git push origin main
```

Open a new PR (branch from clean main):
```bash
git checkout main && git pull upstream main
git checkout -b fix/<short-desc>
# edit code + add tests...
git commit -s -m "..."   # -s is the DCO sign-off, required by vLLM
git push origin fix/<short-desc>
# open a PR against vllm-project/vllm on GitHub
```

## Reading map (no-GPU sweet spots)
> See the subsystem table in [01-architecture-map.md](01-architecture-map.md).

## Progress log
- 2026-07-02: fork + clone, configured origin/upstream, created study branch.
- 2026-07-02: (detour: dived into scheduler detail too early) corrected to **top-down**.
- 2026-07-02: finished Stage 0 overview + Stage 1 architecture map; repositioned scheduler note to Stage 2 (02-scheduler.md).
- 2026-07-02: added **source-grounded skeleton** (run_busy_loop -> step -> schedule/execute/sample/update); established project rules + reflection log, pushed to study.
- 2026-07-02: added project language rule (records in English, conversation in Chinese).
- 2026-07-02: translated all existing notes from Chinese/mixed to full English.
- 2026-07-02: wrote **04-engine.md** — detailed system skeleton (EngineCore composition, step vs step_with_batch_queue, run_busy_loop, 3-thread ZMQ IO, client/engine message protocol).
- 2026-07-02: added **TEACHING-PLAN.md** (7-phase curriculum, Core/Extended paths, per-module detail, QA review) and **BUG-HUNTING.md** (first-PR strategies grounded in real tests + vLLM AI-assist policy).
