# 00 · vLLM Project Overview (What / Pain / Effect)

> Top-down layer 1: before reading code, understand what problem this project solves, how, and the effect.
> Sources: official README, launch blog (2023-06-20), SOSP 2023 paper (arXiv:2309.06180).

## 1. One-line positioning
**vLLM = a fast, cheap, easy-to-use LLM inference and serving engine.**
Slogan: *"Easy, fast, and cheap LLM serving for everyone."*
Origin: UC Berkeley Sky Computing Lab; now one of the most active open-source AI projects with 2000+ contributors.

## 2. Pain point: why is LLM serving slow/expensive? — the bottleneck is **GPU memory**, not compute

During autoregressive decoding, every token produces attention Key/Value tensors that are cached in GPU
memory for reuse by later tokens — this is the **KV cache**. It has two brutal properties:

- **Large**: a single LLaMA-13B sequence's KV cache can take up to **1.7 GB**.
- **Dynamic**: size grows with sequence length, which is **highly unpredictable** (you do not know how long the output will be).

Traditional systems (e.g. pre-reserving one contiguous block for the whole KV cache) therefore suffer:

| Waste type | Cause |
|---|---|
| Internal fragmentation | Reserve by max_len, but the sequence does not fill it |
| External fragmentation | Gaps left by large contiguous allocations |
| Over-reservation | Pre-claim space for the "possible longest output" |

Result: **existing systems waste 60%-80% of KV memory**. Wasted memory -> fewer requests fit in a batch -> low GPU utilization -> low throughput.
> This is exactly the "resource utilization / capacity planning" problem I know well, just with the resource changed from CPU/RAM to GPU memory blocks.

## 3. Solution: PagedAttention — bring OS "virtual memory + paging" to the KV cache

Core insight: **borrow the OS virtual-memory paging idea**.
- Split each sequence's KV cache into **fixed-size blocks** (each block stores K/V for a fixed number of tokens).
- **Blocks need not be contiguous** in physical memory; a **block table** maps "logical block -> physical block" (like a page table).
- Physical blocks are **allocated on demand** (a new block is allocated only when a new token is generated).

The analogy is clean:

| OS virtual memory | PagedAttention |
|---|---|
| page | KV block |
| byte | token |
| process | sequence / request |
| page table | block table |

**Effect 1: near-zero waste** — only the **last block** of each sequence may be partially filled, wasting <4% (vs 60-80% traditionally). Saved memory -> more sequences batched together -> higher GPU utilization -> higher throughput.

**Effect 2: flexible sharing** — when sequences share a common prefix (e.g. parallel sampling or beam search sharing the same prompt), their logical blocks **map to the same physical block**; safety is ensured by **reference counting + Copy-on-Write**. Saves up to 55% memory -> another +2.2x throughput.
> This is the foundation of prefix caching, and the underlying mechanism behind the scheduler's `get_computed_blocks()` cache hit in note 02.

## 4. Effect: the numbers
| Comparison target | Throughput gain |
|---|---|
| vs HuggingFace Transformers | **up to 24x** (8.5-15x for parallel sampling) |
| vs HF TGI (previous SOTA) | 2.2-3.5x |
| vs Orca / FasterTransformer (paper) | **2-4x** at the same latency (more pronounced for long sequences / large models / complex decoding) |

**Real-world**: after LMSYS Chatbot Arena / Vicuna adopted vLLM — **30x** throughput vs the initial HF backend, **GPU count halved**, ~30K requests/day average, 60K peak. A small research team served millions of users with limited campus GPUs.

## 5. Beyond PagedAttention: other "fast" techniques vLLM stacks
(README feature list, expanded later in the classification plan)
- **Continuous batching**, **chunked prefill**, **prefix caching**
- **Speculative decoding** (n-gram / EAGLE, etc.)
- **CUDA/HIP graphs**, torch.compile graph optimizations
- **Quantization**: FP8/INT8/INT4/GPTQ/AWQ/GGUF...
- **Distributed parallelism**: Tensor / Pipeline / Data / Expert / Context parallel
- **Disaggregated prefill/decode/encode** (P/D disaggregation)
- **Multi-LoRA**, structured output, tool calling
- **OpenAI-compatible API server** + Anthropic Messages + gRPC

## 6. Which parts should I focus on? (conclusion first, formal plan next)
- Yes, my sweet spots (no GPU needed): scheduling / KV memory management / serving-layer API / distributed coordination / multi-tenant (LoRA) / observability
- Avoid for now (need GPU/CUDA): attention kernels, quantization kernels, CUDA graph, model executor

---
_Study date: 2026-07-02_
