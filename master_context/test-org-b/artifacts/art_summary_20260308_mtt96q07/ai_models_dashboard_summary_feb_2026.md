# AI Models Dashboard Summary — February 2026

## Executive Overview

This summary provides key insights from the AI Models Leaderboard tracking **12 frontier AI models** from **8 providers** across **5 industry-standard benchmarks**.

---

## Dashboard Statistics at a Glance

| Metric | Value |
|--------|-------|
| Models Tracked | 12 |
| Average MMLU Score | 89.2% |
| Maximum Context Window | 2M tokens |
| Top HumanEval Score | 96.4% |
| Last Updated | February 26, 2026 |

---

## Models by Provider

### OpenAI
| Model | MMLU | HumanEval | Context | Pricing (Input/Output per 1M) |
|-------|------|-----------|---------|-------------------------------|
| **GPT-4.5 Turbo** ✨ | 92.8% | 95.2% | 256K | $10.00 / $30.00 |
| GPT-4o | 88.7% | 91.0% | 128K | $2.50 / $10.00 |

### Anthropic
| Model | MMLU | HumanEval | Context | Pricing (Input/Output per 1M) |
|-------|------|-----------|---------|-------------------------------|
| **Claude 4 Opus** ✨ | 93.1% | 96.4% | 500K | $15.00 / $75.00 |
| Claude 3.5 Sonnet | 90.4% | 93.7% | 200K | $3.00 / $15.00 |

### Google
| Model | MMLU | HumanEval | Context | Pricing (Input/Output per 1M) |
|-------|------|-----------|---------|-------------------------------|
| **Gemini 2.0 Ultra** ✨ | 91.9% | 94.8% | 2M | $12.50 / $37.50 |
| Gemini 1.5 Pro | 86.5% | 84.1% | 1M | $1.25 / $5.00 |

### Meta (Open Source)
| Model | MMLU | HumanEval | Context | Pricing |
|-------|------|-----------|---------|---------|
| **Llama 4 405B** ✨ | 90.8% | 93.1% | 256K | Free |
| Llama 3.2 70B | 85.3% | 81.7% | 128K | Free |

### Other Providers
| Model | Provider | MMLU | HumanEval | Context | Pricing (Input/Output per 1M) |
|-------|----------|------|-----------|---------|-------------------------------|
| **Grok-3** ✨ | xAI | 89.7% | 90.3% | 128K | $5.00 / $15.00 |
| Mistral Large 3 🔄 | Mistral | 88.9% | 89.4% | 128K | $4.00 / $12.00 |
| DeepSeek V3 | DeepSeek | 87.6% | 88.2% | 64K | $0.14 / $0.28 |
| Command R+ | Cohere | 82.1% | 75.8% | 128K | $2.50 / $10.00 |

✨ = New | 🔄 = Updated

---

## Benchmark Rankings

### 🎯 Overall Intelligence (MMLU)
| Rank | Model | Score |
|------|-------|-------|
| 🥇 | Claude 4 Opus | 93.1% |
| 🥈 | GPT-4.5 Turbo | 92.8% |
| 🥉 | Gemini 2.0 Ultra | 91.9% |
| 4 | Llama 4 405B | 90.8% |
| 5 | Claude 3.5 Sonnet | 90.4% |

### 💻 Coding (HumanEval)
| Rank | Model | Score |
|------|-------|-------|
| 🥇 | Claude 4 Opus | 96.4% |
| 🥈 | GPT-4.5 Turbo | 95.2% |
| 🥉 | Gemini 2.0 Ultra | 94.8% |
| 4 | Claude 3.5 Sonnet | 93.7% |
| 5 | Llama 4 405B | 93.1% |

### 🧮 Math Reasoning (GSM8K)
| Rank | Model | Score |
|------|-------|-------|
| 🥇 | Claude 4 Opus | 97.8% |
| 🥈 | GPT-4.5 Turbo | 97.1% |
| 🥉 | Gemini 2.0 Ultra | 96.9% |
| 4 | Claude 3.5 Sonnet | 96.4% |
| 5 | Llama 4 405B | 95.7% |

### 🔬 Graduate Science (GPQA)
| Rank | Model | Score |
|------|-------|-------|
| 🥇 | Claude 4 Opus | 62.1% |
| 🥈 | GPT-4.5 Turbo | 61.3% |
| 🥉 | Gemini 2.0 Ultra | 60.7% |
| 4 | Claude 3.5 Sonnet | 59.4% |
| 5 | Llama 4 405B | 58.9% |

### 💬 Conversational (MT-Bench)
| Rank | Model | Score |
|------|-------|-------|
| 🥇 | Claude 4 Opus | 9.7 |
| 🥈 | GPT-4.5 Turbo | 9.6 |
| 🥉 | Gemini 2.0 Ultra | 9.5 |
| 4 | Claude 3.5 Sonnet | 9.5 |
| 5 | Llama 4 405B | 9.4 |

### 💰 Cost Efficiency (Lowest Avg Price)
| Rank | Model | Avg $/1M tokens |
|------|-------|-----------------|
| 🥇 | DeepSeek V3 | $0.21 |
| 🥈 | Gemini 1.5 Pro | $3.13 |
| 🥉 | Mistral Large 3 | $8.00 |
| 4 | Claude 3.5 Sonnet | $9.00 |
| 5 | Grok-3 | $10.00 |

---

## Key Insights

### Top Performers
- **Claude 4 Opus** dominates across all benchmarks, leading in MMLU (93.1%), HumanEval (96.4%), GSM8K (97.8%), GPQA (62.1%), and MT-Bench (9.7)
- **GPT-4.5 Turbo** consistently ranks #2 across all categories
- **Gemini 2.0 Ultra** offers the largest context window at 2M tokens

### Cost Considerations
- **Free tier**: Meta's Llama models (Llama 4 405B, Llama 3.2 70B) — excellent for self-hosted deployments
- **Best value paid**: DeepSeek V3 at $0.14/$0.28 per 1M tokens
- **Premium tier**: Claude 4 Opus commands premium pricing ($15/$75) justified by top benchmark scores

### New Releases (Feb 2026)
Five new/updated models this cycle:
1. GPT-4.5 Turbo (OpenAI) — new
2. Claude 4 Opus (Anthropic) — new
3. Gemini 2.0 Ultra (Google) — new
4. Llama 4 405B (Meta) — new
5. Grok-3 (xAI) — new
6. Mistral Large 3 (Mistral) — updated

### Context Window Comparison
| Tier | Models |
|------|--------|
| 2M | Gemini 2.0 Ultra |
| 1M | Gemini 1.5 Pro |
| 500K | Claude 4 Opus |
| 256K | GPT-4.5 Turbo, Llama 4 405B |
| 200K | Claude 3.5 Sonnet |
| 128K | GPT-4o, Llama 3.2 70B, Mistral Large 3, Grok-3, Command R+ |
| 64K | DeepSeek V3 |

---

## Dashboard Features

The interactive dashboard provides:
- **Sortable columns** — click any column header to sort ascending/descending
- **Provider filtering** — view models by OpenAI, Anthropic, Google, Meta, or Others
- **View modes** — toggle between full model table and rankings view
- **Visual rankings** — progress bars and medal indicators for top performers

---

## Source

Based on the AI Models Dashboard artifact created February 2026.

*Data compiled from official benchmarks and independent evaluations.*
