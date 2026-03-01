# Spinal Loop Orchestrator

**Bio-inspired multi-agent orchestration for LLMs.**

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![No LangChain](https://img.shields.io/badge/LangChain-not%20needed-red.svg)](#)
[![Anthropic API](https://img.shields.io/badge/Anthropic-API%20direct-blueviolet.svg)](https://docs.anthropic.com/)

> What if multi-agent orchestration worked like the human neuromuscular system?

Spinal Loop maps four biological mechanisms from neuromuscular physiology onto a multi-agent LLM system. Instead of ad-hoc routing heuristics, it uses principles that evolved over millions of years to solve the exact same problems: **recruit minimum force needed**, **detect overload before failure**, **lock action modes to prevent oscillation**, and **reverse behavior based on context**.

No frameworks. No abstractions. Direct Anthropic API calls only.

---

## Architecture

```
                          User Query
                              |
                    +---------v---------+
                    |   MODE CLASSIFIER |  Reciprocal Inhibition
                    |      (Haiku)      |  REFLEX vs DELIBERATIVE
                    +---------+---------+
                              |
              +---------------+---------------+
              |                               |
     +--------v--------+           +----------v----------+
     |     REFLEX       |           |     DELIBERATIVE     |
     |  Haiku, 150 tok  |           |                      |
     |  No chain-of-    |           |  +----------------+  |
     |  thought, direct |           |  |   HENNEMAN     |  |
     +--------+---------+           |  |   RECRUITER    |  |
              |                     |  |                |  |
              |                     |  | Haiku (Lv1)    |  |
              |                     |  |   | escalate?  |  |
              |                     |  | Sonnet (Lv2)   |  |
              |                     |  |   | escalate?  |  |
              |                     |  | Opus (Lv3)     |  |
              |                     |  +-------+--------+  |
              |                     |          |           |
              |                     |  +-------v--------+  |
              |                     |  |  GTO MONITOR   |  |
              |                     |  |  Overload?     |  |
              |                     |  |  Y: decompose  |  |
              |                     |  |  N: pass       |  |
              |                     |  +-------+--------+  |
              |                     |          |           |
              |                     |  +-------v--------+  |
              |                     |  |   MODULATOR    |  |
              |                     |  | EXPLORE phase: |  |
              |                     |  |   diverge      |  |
              |                     |  | CONSOLIDATE:   |  |
              |                     |  |   converge     |  |
              |                     |  +-------+--------+  |
              |                     +----------+-----------+
              |                                |
              +----------------+---------------+
                               |
                           Response
```

## The 4 Mechanisms

| # | Mechanism | Biology | Implementation |
|---|-----------|---------|----------------|
| 1 | **Henneman's Principle** | Motor neurons recruit small units first, large units only when needed | Always start with Haiku. Each agent self-evaluates confidence (0-1) and complexity (0-1). Escalate to Sonnet, then Opus only if needed. Never skip levels. |
| 2 | **GTO / Autogenic Inhibition** | Golgi tendon organ detects excessive muscle tension and inhibits contraction | A monitor agent analyzes every response for repetitions, excessive length, incoherence, and circular reasoning. If overloaded: inhibit, decompose into subtasks, redistribute. |
| 3 | **Reciprocal Inhibition** | Flexor activation inhibits extensor (and vice versa) — mutually exclusive | Two modes: REFLEX (fast, Haiku-only, 150 tokens) and DELIBERATIVE (deep, full pipeline). Mutually exclusive with a 3-turn refractory period after switching. |
| 4 | **Reflex Reversal** | Same reflex arc produces opposite responses depending on locomotion phase | Same modulator agent, two opposite system prompts. EXPLORATION phase: amplify divergent ideas. CONSOLIDATION phase: force convergence. Phase switches automatically or by keyword. |

### 1. Henneman's Principle — Ordered Recruitment

The most expensive model should be the last resort, not the default. Each agent includes a self-evaluation block:

```json
{"confidence": 0.4, "complexity": 0.85, "escalate": true, "reason": "..."}
```

If `confidence < 0.7` OR `complexity > 0.7` → escalate to the next level. The previous agent's response is passed as context, so the stronger model can build on it rather than starting from scratch.

In our simulation, a philosophy question escalated through all 3 levels:
- **Haiku** (confidence: 0.4) → "Kant and Nietzsche diverge on morality..." → ESCALATE
- **Sonnet** (confidence: 0.55) → added historical context → ESCALATE
- **Opus** (confidence: 0.93) → full analysis with contemporary critics → ACCEPTED

### 2. GTO — Overload Monitor

LLMs have a known failure mode: when a question is too broad, they produce repetitive, circular, or hallucinated responses. Normally, the user has to detect this and rephrase.

The GTO monitor detects this automatically:
- Repetitions (same concept >3 times)
- Excessive length (>2x expected)
- Internal contradictions
- Circular reasoning / saturation

When overload is detected, the monitor **inhibits** the response, **decomposes** the question into focused subtasks, and **redistributes** them to lower-level agents that handle each part cleanly.

### 3. Reciprocal Inhibition — Mode Switching

A classifier (Haiku, <100 tokens) determines if the query needs a quick reflex or deep deliberation. The two modes are mutually exclusive — like flexor/extensor muscles, only one can be active.

The **refractory period** (3 turns) prevents oscillation. Once in REFLEX mode, the system stays there for at least 3 turns, even if a complex question arrives. This mirrors biological neurons that can't refire immediately after an action potential.

### 4. Reflex Reversal — Phase Modulation

The same modulator agent runs two opposite system prompts depending on the conversation phase:

- **EXPLORATION** (early turns): "Amplify divergent ideas, add unexpected connections, challenge assumptions"
- **CONSOLIDATION** (later turns or keyword trigger): "Inhibit divergence, force convergence, eliminate redundancies, structure actionable points"

Phase switches automatically after N turns (configurable) or when the user says "summarize", "conclude", "synthesize".

---

## Quick Start

```bash
git clone https://github.com/contactjccoaching-wq/spinal-loop.git
cd spinal-loop
pip install -r requirements.txt

# Set your Anthropic API key
export ANTHROPIC_API_KEY="sk-ant-your-key-here"

# Interactive mode
python main.py

# One-shot mode
python main.py "What are the philosophical implications of AI consciousness?"
```

## Run the Simulation (No API Key Needed)

See all 4 mechanisms in action with mocked responses:

```bash
python simulate.py
```

This runs 6 queries through the real orchestration code with mock API responses:

| Turn | Query | Mechanism Triggered |
|------|-------|-------------------|
| 1 | "What is the capital of France?" | **Mode Switch** → REFLEX |
| 2 | "Is it in Europe?" | **Refractory period** (REFLEX locked) |
| 3 | "What currency?" | **Refractory** (last locked turn) |
| 4 | "Compare Kant and Nietzsche on morality" | **Henneman** escalade: Haiku → Sonnet → Opus |
| 5 | "Describe the complete history of computing" | **GTO** overload → decompose into 3 subtasks |
| 6 | "Synthesize everything" | **Reflex Reversal** → CONSOLIDATION |

## Configuration

All thresholds are in `config.yaml`:

| Parameter | Default | Description |
|-----------|---------|-------------|
| `henneman.confidence_threshold` | 0.7 | Below this → escalate |
| `henneman.complexity_threshold` | 0.7 | Above this → escalate |
| `gto.max_repetitions` | 3 | Same concept repeated N times → overload |
| `gto.length_multiplier` | 2.0 | Response >2x expected length → overload |
| `mode_switch.refractory_period` | 3 | Minimum turns before mode can switch again |
| `mode_switch.reflex_max_tokens` | 150 | Token limit in REFLEX mode |
| `modulator.phase_switch_turn` | 5 | Turn number for automatic EXPLORATION → CONSOLIDATION |
| `modulator.consolidation_keywords` | see file | Keywords that trigger CONSOLIDATION phase |

## How It Compares

| Feature | OpenRouter | Martian | FrugalGPT | LangChain | **Spinal Loop** |
|---------|-----------|---------|-----------|-----------|-----------------|
| Model selection | yes | yes | yes | yes | yes (Henneman) |
| Progressive escalation | no | no | yes | possible | yes |
| Agent self-evaluation | no | no | no (external) | no | **yes** |
| Post-response overload detection | no | no | no | no | **yes (GTO)** |
| Automatic decomposition | no | no | no | manual | **yes** |
| Exclusive fast/slow modes | no | no | no | no | **yes** |
| Refractory period | no | no | no | no | **yes** |
| Explore/consolidate modulation | no | no | no | no | **yes** |

## Cost Efficiency

From our 6-turn simulation:

```
Total API calls: 22
Models used:     Haiku: 20 (91%)  |  Sonnet: 1 (4.5%)  |  Opus: 1 (4.5%)
Tokens:          2,300 in / 1,997 out = 4,297 total
```

91% of calls go to Haiku (the cheapest model). Sonnet and Opus are recruited **once each**, only when necessary. Compared to sending everything to Opus, this represents a **~70% cost reduction** with equivalent or better output quality on complex queries (thanks to the escalation context passing).

## Project Structure

```
spinal_loop/
├── config.yaml           # All thresholds and parameters
├── main.py               # CLI entry point (one-shot + interactive)
├── orchestrator.py        # Main pipeline coordinating all 4 mechanisms
├── simulate.py            # Full simulation with mock API (no key needed)
├── agents/
│   ├── recruiter.py       # Henneman — ordered recruitment with escalation
│   ├── monitor.py         # GTO — overload detection and decomposition
│   ├── mode_switch.py     # Reciprocal inhibition — REFLEX/DELIBERATIVE
│   └── modulator.py       # Reflex reversal — EXPLORATION/CONSOLIDATION
└── utils/
    ├── logger.py          # Biological event logging (colored + file)
    └── context.py         # Shared session state management
```

~1,400 lines of Python. No dependencies beyond `anthropic` and `pyyaml`.

## Biological Events Log

Every decision is logged with its biological event type:

```
[CLASSIFY]   Haiku classifier → REFLEX or DELIBERATIVE
[SWITCH]     Mode transition (with refractory lock)
[RECRUIT]    Agent recruited at level N
[ESCALADE]   Confidence too low → escalate to next level
[OVERLOAD]   GTO monitor checks response quality
[INHIBITION] Overload detected → inhibit and decompose
[DECOMPOSE]  Split into subtasks for redistribution
[MODULATE]   Apply EXPLORATION or CONSOLIDATION lens
[REVERSAL]   Phase switch triggered
```

## Why Biomimicry?

This isn't just a metaphor. Neuromuscular systems evolved over millions of years to solve the exact problems multi-agent AI systems face:

- **Recruit minimum force** → recruit minimum cost (Henneman)
- **Detect overload before rupture** → detect quality degradation before user sees it (GTO)
- **Lock action mode to prevent oscillation** → refractory period prevents mode thrashing
- **Reverse behavior based on phase** → same agent, opposite prompts, context-dependent

The biological framing provides a **coherent design framework** instead of ad-hoc heuristics stacked on top of each other.

## Requirements

- Python 3.11+
- `anthropic>=0.25.0`
- `pyyaml>=6.0`
- An Anthropic API key (for real usage; simulation works without one)

## Related Projects

Spinal Loop is part of a trilogy of multi-agent research projects:

| Project | What it does |
|---------|-------------|
| **[PRISM Framework](https://github.com/contactjccoaching-wq/prism-framework)** | N-parallel sampling + meritocratic synthesis — exploit LLM stochasticity instead of engineering personas |
| **[DACO](https://github.com/contactjccoaching-wq/daco-framework)** | Single MCP endpoint that routes tool calls to multiple backends — the execution layer for agent orchestration |
| **Spinal Loop** *(this repo)* | Bio-inspired model routing — 4 neuromuscular mechanisms for cost-efficient multi-agent orchestration |

Each solves a different piece of the multi-agent puzzle: PRISM handles *what to ask*, Spinal Loop handles *who to ask*, and DACO handles *what to do with it*.

## License

MIT — see [LICENSE](LICENSE).

---

*Built with direct Anthropic API calls. No LangChain. No LangGraph. No abstractions. Just biology and code.*
