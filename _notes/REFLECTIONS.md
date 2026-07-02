# Reflections · Learning Log

> Append one entry per conversation: what I learned, which detours I took, how to improve next time. Newest on top.

## 2026-07-02 · #4 (Autonomous teaching-plan build)
**What I did (user at dinner, 5-step autonomous task, no check-ins)**
- Surveyed the real source tree (vllm subpackages, tests/, docs/design, docs/contributing) to ground the plan.
- Wrote **TEACHING-PLAN.md**: Part A high-level 7-phase curriculum, Part B plan review + revised Core Path, Part C detailed per-module breakdowns (objective/source/design-doc/hands-on-test/self-check/pitfalls/interview-hook/effort), Part D QA of the plan.
- Wrote **BUG-HUNTING.md**: first-PR strategies (test gaps, doc drift, edge-case reasoning), no-GPU validation reality (CPU tests partial, rely on CI), PR checklist.

**Key facts learned (source-grounded)**
- vLLM has an explicit **AI-Assisted Contribution policy**: no pure-agent PRs, human must review/validate/test, avoid busywork (bundle mechanical changes), disclose + `Co-authored-by:` trailer. Directly shapes how we contribute.
- Python-only dev install: `VLLM_USE_PRECOMPILED=1 uv pip install -e .`. CI uses Python 3.12.
- Honest constraint: not all unit tests pass on CPU; no-GPU devs rely on CI. `tests/v1/core/*` (scheduler/kv) are the most CPU-friendly.
- PR title prefixes: [Bugfix] [CI/Build] [Doc] [Model] [Frontend] [Kernel] [Core] [Hardware] [Misc].

**Next-time improvement**
- When starting Phase 3, write 03-kv-cache.md (still the one missing Core note).
- Re-review 02-scheduler.md for correctness before relying on it (flagged in plan QA).

## 2026-07-02 · #3 (Full English migration)
**What changed**
- Migrated all existing notes (00/01/02, README, PROJECT-RULES, this log) from Chinese/mixed to full English, per the language rule.

**Follow-up**
- Keep every new note in English from the start.

## 2026-07-02 · #2 (Language rule)
**What changed**
- Added a project-level language policy: all project records in `_notes/` are in English for easier sharing.
- Conversation language stays Chinese for efficient collaboration.

**Follow-up**
- Apply this rule to all new note entries.

## 2026-07-02 · #1 (Methodology + skeleton)
**What I did**
- fork + clone + configured origin/upstream, created `study` branch and `_notes/` structure.
- Finished 00 overview (pain = KV memory waste 60-80%, solution = PagedAttention, effect = vs HF 24x).
- Finished 01 architecture map (subsystem table + data flow), and **added a source-verified skeleton**:
  `run_busy_loop` -> `EngineCore.step()` -> `schedule/execute/sample/update` (with file:line).
- 02 scheduler detail (`schedule()` two phases: RUNNING preemption + WAITING admission + prefix caching).

**Detours / lessons (user corrections)**
1. Wrong: dived into scheduler detail immediately. Right: go top-down — understand what/pain/effect, then classify, then detail.
2. Wrong: top-down done from md/online only. Right: must read **real source** for the skeleton, then go top-down with understanding.
3. Rule established: `study` never merges into main, it is a learning-only branch; commit **and push** after every conversation; do not gitignore `_notes`.

**Next-time improvement**
- For each subsystem, first locate its position in the `EngineCore.step()` call chain, then expand the implementation.
- Continue Stage 2: 03 KV paged block management (`block_pool.py` + `kv_cache_manager.py`), or review 02 first.
