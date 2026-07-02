# vLLM Study Project · Project Rules

> This repo is a learning fork. The rules below apply long-term; the AI assistant should
> follow them on every collaboration.

## Branches
- **`main`**: kept clean, only synced with official `upstream`; branch future PRs from here.
- **`study`**: **learning-only branch, never merged back into `main`**. All `_notes/` study notes and reflections are committed here.
- `_notes/` and study artifacts are **not added to .gitignore** (must persist and stay reviewable).

Remotes: `origin` = my fork (raymondyates1990/vllm-caseStudy), `upstream` = vllm-project/vllm.

## Language rule (project-level)
- All project records (`_notes/` docs, reflections, summaries, plans, commit messages) are written in **English**, for easier sharing.
- Real-time conversation with the AI assistant stays in **Chinese**.
- Effective 2026-07-02; existing historical records have been migrated to English.

## Fixed actions at the end of every conversation
1. Write this session's reflection / learning into `_notes/` ([REFLECTIONS.md](REFLECTIONS.md) + relevant notes).
2. `git add _notes` -> `git commit -s -m "..."` (`-s` is the DCO sign-off).
3. **`git push origin study`** (always push, not just commit).

## Methodology (top-down + source-grounded)
1. **Whole before parts**: 00 what/pain/effect -> 01 architecture map -> 02+ subsystem detail -> first PR. Do not start by drilling into a single function.
2. **Top-down must read real source**: not only md/blog/paper; follow entry points (`run_busy_loop` -> `step` -> `schedule`) to read the code skeleton, then expand with understanding.
3. **Focus on no-GPU strength subsystems**: scheduling / KV management / engine / API / distributed coordination / LoRA / observability; avoid kernels/csrc/model_executor (need GPU; skip compilation with `VLLM_USE_PRECOMPILED=1`).

## PR workflow (for later)
```bash
git checkout main && git pull upstream main
git checkout -b fix/<desc>
# edit code + add tests
git commit -s -m "..."
git push origin fix/<desc>   # then open a PR against vllm-project/vllm on GitHub
```
