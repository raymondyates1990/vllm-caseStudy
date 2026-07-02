# Reflections · Learning Log

> Append one entry per conversation: what I learned, which detours I took, how to improve next time. Newest on top.

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
