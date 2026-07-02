# 00 · vLLM 项目总览（是什么 / 痛点 / 效果）

> 自顶向下第一层：先不看代码，先搞懂这项目在解决什么问题、怎么解决、效果如何。
> 资料来源：官方 README、发布博客(2023-06-20)、SOSP 2023 论文(arXiv:2309.06180)。

## 1. 一句话定位
**vLLM = 快、省、易用的 LLM 推理与服务引擎。**
Slogan: *"Easy, fast, and cheap LLM serving for everyone."*
起源：UC Berkeley Sky Computing Lab；现为最活跃开源 AI 项目之一，2000+ 贡献者。

## 2. 痛点：LLM 服务为什么慢/贵？—— 瓶颈在**显存**，不是算力

自回归解码时，每个 token 都会产生 attention 的 Key/Value 张量，缓存在 GPU 显存里供后续 token 复用，这就是 **KV cache**。它有两个要命特性：

- **大**：LLaMA-13B 单条序列的 KV cache 最高占 **1.7 GB**。
- **动态**：大小随序列长度变化，而长度**高度不可预测**（不知道会生成多长）。

传统系统（如把整段 KV 预留成一块连续显存）因此产生：
| 浪费类型 | 原因 |
|---|---|
| 内部碎片 (internal frag.) | 按 max_len 预留，实际没用满 |
| 外部碎片 (external frag.) | 连续大块分配留下的空隙 |
| 过度预留 (over-reservation) | 为"可能的最长输出"提前占坑 |

结果：**现有系统浪费 60%–80% 的 KV 显存**。显存被浪费 → batch 装不下更多请求 → GPU 利用率低 → 吞吐低。
> 这正是我熟的"资源利用率/容量规划"问题，只是资源从 CPU/内存换成了 GPU 显存块。

## 3. 解决方案：PagedAttention —— 把操作系统的"虚拟内存 + 分页"搬到 KV cache

核心洞察：**借鉴 OS 的虚拟内存分页**。
- 把每条序列的 KV cache 切成**固定大小的 block**（每块存固定数量 token 的 K/V）。
- **block 在物理显存里不必连续**，通过 **block table** 把"逻辑块 → 物理块"映射（就像页表）。
- 物理块**按需分配**（生成新 token 才分配新块）。

类比一目了然：

| OS 虚拟内存 | PagedAttention |
|---|---|
| 页 (page) | KV block |
| 字节 (byte) | token |
| 进程 (process) | 序列 (sequence/request) |
| 页表 (page table) | block table |

**效果 1：近零浪费**——只有每条序列的**最后一个 block**可能没填满，浪费 <4%（对比传统 60–80%）。省下的显存 → 能同时 batch 更多序列 → GPU 利用率↑ → 吞吐↑。

**效果 2：灵活共享**——多序列共享相同前缀（如并行采样、beam search 共享同一 prompt）时，让它们的逻辑块**映射到同一物理块**；靠**引用计数 + Copy-on-Write** 保证安全。省显存最多 55% → 吞吐再 +2.2x。
> 这就是后来 prefix caching 的地基，也是我 01 笔记里调度器 `get_computed_blocks()` 命中缓存的底层机制。

## 4. 效果：数字说话
| 对比对象 | 吞吐提升 |
|---|---|
| vs HuggingFace Transformers | **最高 24x**（并行采样场景 8.5–15x） |
| vs HF TGI（前 SOTA） | 2.2–3.5x |
| vs Orca / FasterTransformer（论文） | 同延迟下 **2–4x**（长序列/大模型/复杂解码时更明显） |

**真实战绩**：LMSYS Chatbot Arena / Vicuna 用 vLLM 后——比初版 HF 后端吞吐 **30x**，**GPU 数量砍半**，日均处理 30K 请求、峰值 60K。一个小研究团队靠有限校园 GPU 就服务了数百万用户。

## 5. 除了 PagedAttention，vLLM 还叠了哪些"快"的技术
（README feature 列表，后面做分类计划时展开）
- **Continuous batching**（连续批处理）、**chunked prefill**（分块预填充）、**prefix caching**
- **Speculative decoding**（投机解码：n-gram / EAGLE 等）
- **CUDA/HIP graphs**、torch.compile 图优化
- **量化**：FP8/INT8/INT4/GPTQ/AWQ/GGUF...
- **分布式并行**：Tensor / Pipeline / Data / Expert / Context 并行
- **Disaggregated prefill/decode/encode**（P/D 分离）
- **多 LoRA**、结构化输出、Tool calling
- **OpenAI 兼容 API server** + Anthropic Messages + gRPC

## 6. 我该关注哪块？（先记结论，下一步做正式分类计划）
- ✅ 我的主场（无 GPU 可碰）：调度 / KV 内存管理 / 服务层 API / 分布式协调 / 多租户(LoRA) / 可观测
- ❌ 暂避开（需 GPU/CUDA）：attention kernels、量化 kernel、CUDA graph、model executor

---
_研读日期：2026-07-02_
