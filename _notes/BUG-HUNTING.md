# vLLM · Bug-Hunting & First-PR Guide (Step 5)

> How to find a bug / good first contribution, validate it without a GPU, and land the PR.
> Grounded in `docs/contributing/README.md` and the real test tree. English per project rule.

---

## 0. READ THIS FIRST — vLLM's AI-Assisted Contribution policy

Because we work with an AI assistant, the project's rules (`docs/contributing/README.md` → "AI Assisted
Contributions") apply directly and are **non-negotiable**:

1. **No "pure agent" PRs.** The human submitter (you) must personally review every changed line,
   validate behavior end-to-end, and run the relevant tests. The AI drafts; you own it.
2. **Ensure significance.** Avoid one-off busywork: a single typo, one isolated style cleanup, one mutable
   default fix. If doing mechanical cleanup, **bundle it into a clear systematic scope** across the codebase.
3. **Disclose + attribute.** Mention AI assistance in the PR description and add commit trailers, e.g.:
   ```text
   [Core] Fix <thing> in scheduler preemption accounting

   Co-authored-by: GitHub Copilot
   Signed-off-by: Ran Ye <ran-ye@outlook.com>
   ```

**Implication for our workflow**: I (AI) help you *find*, *understand*, and *draft*; you *verify*, *test*,
and *submit*. Pick something meaningful (a real logic/test/doc gap), not a cosmetic one-liner.

---

## 1. Mindset: where bugs & opportunities hide in a fast-moving project

vLLM merges dozens of PRs/day. That churn creates predictable gaps:
- **Test gaps**: new logic merged with thin tests → add edge-case tests (safest, high-value first PR).
- **Doc↔code drift**: docs describe old behavior; code changed → doc fix (easy, but bundle for significance).
- **Edge cases in pure logic**: scheduler budget/preemption accounting, KV block free/reuse, prefix-cache
  eviction — your strength areas, all CPU-testable.
- **Error handling / messages**: unclear errors at boundaries (config validation, request preprocessing).
- **Type/interface inconsistencies**: `mypy` is not fully enforced → typed fixes (bundle them).

Rank by *(no-GPU feasibility × significance × your strength)*:
1. **Scheduler/KV logic + tests** (v1/core) — best fit. CPU-testable, your wheelhouse, `[Core]`.
2. **Engine/client logic + tests** (v1/engine) — CPU-testable, `[Core]`/`[Frontend]`.
3. **Docs for design areas you now understand** (paged_attention, prefix_caching, arch_overview) — `[Doc]`.
4. Config validation / error messages — `[Core]`/`[Misc]`.

Avoid as a first PR: kernels/CUDA (`[Kernel]`, needs GPU), new models (`[Model]`, large).

---

## 2. Concrete search strategies

### 2.1 Start from the Job Board (official)
- Good first issues: `https://github.com/vllm-project/vllm/issues?q=is%3Aissue+state%3Aopen+label%3A%22good+first+issue%22`
- Onboarding project: `https://github.com/orgs/vllm-project/projects/6`
- Filter for issues touching `v1/core`, `v1/engine`, scheduler, kv cache, or docs.

### 2.2 Hunt test gaps (recommended first PR)
Read a source function, then its test file, and look for **unexercised branches**:
- `vllm/v1/core/sched/scheduler.py` ↔ `tests/v1/core/test_scheduler.py`
- `vllm/v1/core/block_pool.py` ↔ `tests/v1/core/test_kv_cache_utils.py`, `test_single_type_kv_cache_manager.py`
- prefix caching ↔ `tests/v1/core/test_prefix_caching.py`, `tests/v1/core/prefix_cache/`, `test_reset_prefix_cache_e2e.py`, `test_kv_cache_metrics.py`
- output / detokenize ↔ `tests/v1/engine/test_output_processor.py` (CPU-safe; note `test_engine_core_client.py` skips on non-CUDA)

Technique: pick a function with a non-trivial `if/continue/break` (e.g. the phase-1 `continue`-not-`break`
in `schedule()`, or preemption victim selection). Ask "is this branch covered?" If not, write a focused test
that would fail if the branch regressed. A well-justified test PR is welcomed and low-risk.

### 2.3 Doc↔code drift
Compare a `docs/design/*.md` with the current code:
- `docs/design/prefix_caching.md` vs `block_pool.py` / `kv_cache_manager.py`
- `docs/design/arch_overview.md` vs `v1/engine/core.py`
- `docs/design/multiprocessing.md` vs `v1/executor/multiproc_executor.py`
If the doc names a function/flag that was renamed or a behavior that changed, that's a `[Doc]` fix. Bundle
several small drifts into one coherent PR for significance.

### 2.4 Edge-case reasoning in your strength areas
Questions that often surface real bugs (all CPU-testable):
- **Budget accounting**: after a preemption in phase 1, is `token_budget` restored exactly? (see the
  `token_budget += num_scheduled_tokens.pop(...)` path). Construct a test that preempts and checks the budget.
- **Free-list integrity**: after free/allocate/free cycles, is the `FreeKVCacheBlockQueue` length invariant?
- **Prefix-cache eviction**: can a block be evicted while still referenced? (ref-count invariant.)
- **Stop detection**: off-by-one in `num_computed_tokens` vs `max_tokens` at the boundary.

### 2.5 grep for smells
```bash
grep -rn "TODO\|FIXME\|XXX\|HACK" vllm/v1/core vllm/v1/engine
grep -rn "mutable default\|= \[\]\|= {}" vllm/v1/core   # risky mutable defaults (bundle fixes)
```

---

## 3. No-GPU validation reality (important, honest)

From `docs/contributing/README.md`:
> "not all unit tests pass when run on CPU platforms. If you don't have access to a GPU platform to run unit
> tests locally, rely on the continuous integration system."

So:
- **Some** pure-logic tests run on CPU (scheduler/kv/queue math). Try them; expect a subset to pass.
- For anything needing CUDA, **let CI run it** on your PR — that is the intended workflow for no-GPU devs.
- Setup for the CPU-testable subset:
  ```bash
  # in WSL2 Ubuntu, Python 3.12 recommended (CI uses 3.12)
  VLLM_TARGET_DEVICE=cpu uv pip install -e .   # CPU build; see docs/getting_started/installation/cpu.md (VLLM_USE_PRECOMPILED=1 targets CUDA-torch machines)
  uv pip install pytest pytest-asyncio
  pytest -s -v tests/v1/core/test_scheduler.py
  pytest -s -v tests/v1/core/test_kv_cache_utils.py
  ```
- Lint locally (always): `pre-commit install` then `pre-commit run -a`.

---

## 4. Reproduce & isolate a bug
1. **Minimal repro**: smallest script/test that triggers it. For logic bugs, prefer a unit test in the
   matching `tests/v1/...` file over an end-to-end run.
2. **Pin the cause**: add asserts / prints in a local copy; bisect with `git log` on the relevant file.
3. **State the invariant** that's violated (e.g., "free-list length must return to N after alloc+free").

---

## 5. The safest first PR = a focused test (template)
1. Choose an uncovered branch in `scheduler.py`/`block_pool.py`.
2. Write a test in the matching `tests/v1/core/test_*.py` following the file's existing fixtures/style
   (`utils.py` in that dir has helpers).
3. Confirm it **passes on current code** and would **fail if the branch regressed** (temporarily break the
   code to prove the test catches it, then revert).
4. PR title `[Core] Add test for <specific behavior>`; disclose AI assistance; `git commit -s`.

---

## 6. PR checklist (from CONTRIBUTING)
- [ ] Branch from clean `main` (synced with upstream), not `study`.
- [ ] Change is **significant** (not a lone typo/style nit); bundle mechanical cleanups.
- [ ] Tests added/updated; ran the CPU-runnable ones; rely on CI for GPU ones.
- [ ] `pre-commit run -a` passes (lint/format; optionally `mypy-3.11` manual hook).
- [ ] Commit signed off: `git commit -s` (DCO `Signed-off-by:`).
- [ ] AI assistance disclosed in description + `Co-authored-by:` trailer.
- [ ] PR title prefix (official set): `[Bugfix]` / `[CI/Build]` / `[Doc]` / `[Model]` / `[Frontend]` / `[Kernel]` / `[Core]` / `[Hardware][Vendor]` / `[Misc]`. No-GPU first-timers: use `[Core]` / `[Doc]` / `[Frontend]`; avoid `[Kernel]` / `[Model]` / `[Hardware]`.
- [ ] Human (you) reviewed every changed line and validated behavior.

---

## 7. Ranked first-PR shortlist (tailored)
1. **[Core] Add scheduler edge-case test** — preemption budget-restore or `continue`-not-`break` path.
   *Why*: your strength, CPU-testable, welcomed, low-risk. Start here.
2. **[Core] Add block_pool free-list invariant test** — alloc/free cycle integrity.
3. **[Doc] Sync a design doc with code** — bundle 2-3 prefix_caching/arch_overview drifts.
4. **[Core] Improve a config validation error message** — clearer boundary error (bundle a few).
5. **[Misc] Systematic small cleanup** — only if bundled into a coherent scope (per AI policy).

---

## 8. Anti-patterns (will get a PR rejected)
- A single-typo or lone-style PR (violates "ensure significance").
- A "pure agent" PR you didn't personally verify.
- Undisclosed AI assistance.
- Touching kernels/CUDA as a first no-GPU PR.
- Editing on `study` and PRing from it (PR must come from a clean `main`-based branch).

---
_Guide date: 2026-07-02_
