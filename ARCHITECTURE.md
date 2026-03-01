# Architecture — Spinal Loop Orchestrator

## Overview

Spinal Loop maps four neuromuscular control mechanisms onto a multi-agent LLM pipeline. Each mechanism solves a specific failure mode of naive multi-agent systems.

| Problem | Biological Solution | Spinal Loop Component | File |
|---------|--------------------|-----------------------|------|
| Wasting expensive models on easy tasks | Henneman's size principle — recruit small motor units first | Ordered recruitment with self-evaluation | `agents/recruiter.py` |
| LLM produces repetitive/hallucinated output | Golgi tendon organ — inhibit when tension is excessive | Post-response quality monitor with decomposition | `agents/monitor.py` |
| System oscillates between fast/slow modes | Reciprocal inhibition — flexor inhibits extensor | Mutually exclusive modes with refractory period | `agents/mode_switch.py` |
| Always converges too early, kills exploration | Reflex reversal — same arc, opposite response based on phase | Same agent, two opposite prompts, phase-dependent | `agents/modulator.py` |

---

## Mechanism 1: Henneman's Principle (Ordered Recruitment)

### The Biology

In human muscles, motor neurons are recruited in order of size. Small motor units (fine control, low energy) fire first. Large motor units (high force, high energy) are recruited only when the task demands it. You don't activate your entire quadriceps to lift a pen.

### The Implementation

Three agent levels, ordered by cost:

```
Level 1: Haiku    (~$0.25/M tokens)  — fast, cheap, good for simple tasks
Level 2: Sonnet   (~$3/M tokens)     — balanced
Level 3: Opus     (~$15/M tokens)    — deep reasoning, expensive
```

Every agent must include a self-evaluation block in its response:

```xml
<evaluation>
{"confidence": 0.4, "complexity": 0.85, "escalate": true, "reason": "..."}
</evaluation>
```

Decision logic (`recruiter.py:201-208`):

```python
def _should_escalate(self, evaluation):
    if evaluation.get("escalate", False):
        return True
    return (confidence < 0.7 or complexity > 0.7)
```

### Sequence Diagram

```
User: "Compare Kant and Nietzsche"
  |
  v
[Haiku Lv1] → confidence=0.4, complexity=0.85
  |             escalate=True ("superficial response")
  |  ESCALADE ↓ (pass Haiku's response as context)
  |
[Sonnet Lv2] → confidence=0.55, complexity=0.9
  |              escalate=True ("needs deeper analysis")
  |  ESCALADE ↓ (pass both responses as context)
  |
[Opus Lv3] → confidence=0.93, complexity=0.85
  |            escalate=False → ACCEPTED
  v
Response (built on context from all 3 levels)
```

Key insight: when Opus responds, it has access to both Haiku's and Sonnet's attempts. It doesn't start from scratch — it builds on their work, correcting errors and adding depth.

---

## Mechanism 2: GTO / Autogenic Inhibition (Overload Monitor)

### The Biology

The Golgi tendon organ (GTO) sits at the muscle-tendon junction. When it detects excessive tension that could damage the tendon, it inhibits the muscle contraction. This is a **protective mechanism** — it overrides the motor command to prevent injury.

### The Implementation

A separate Haiku agent analyzes every response after generation and checks for:

1. **Repetitions** — same concept appears >3 times
2. **Excessive length** — response >2x expected length
3. **Incoherence** — internal contradictions
4. **Saturation** — circular reasoning, hallucination signals

The monitor returns a structured analysis:

```json
{
  "overloaded": true,
  "signals": {"repetitions": true, "excessive_length": true, "saturation": true},
  "severity": 0.8,
  "subtasks": [
    "The pioneers of computing (Babbage, Lovelace, Turing)",
    "Hardware evolution (vacuum tubes to quantum)",
    "Software era and Internet (FORTRAN to generative AI)"
  ]
}
```

### Sequence Diagram

```
User: "Describe the complete history of computing"
  |
  v
[Haiku Lv1] → "Computing is vast. Computing started with calculations.
  |             Calculations have always been important. The history
  |             of calculations goes back far..."  (repetitive garbage)
  |             confidence=0.75 → no escalation (Haiku thinks it's fine)
  |
  v
[GTO Monitor] → OVERLOAD DETECTED!
  |               repetitions=true, saturation=true, severity=0.8
  |
  |  INHIBIT original response
  |  DECOMPOSE into 3 subtasks
  |
  +--→ [Haiku] "Pioneers of computing"     → clean, focused response
  +--→ [Haiku] "Hardware evolution"          → clean, focused response
  +--→ [Haiku] "Software and Internet era"   → clean, focused response
  |
  v
Combined response (3 clean parts instead of 1 messy whole)
```

Key insight: the agent **thought it did well** (confidence=0.75). Without the GTO, this bad response would have been shown to the user. The monitor catches what self-evaluation misses.

---

## Mechanism 3: Reciprocal Inhibition (Mode Switching)

### The Biology

When you flex your bicep, the tricep is automatically inhibited. Both muscles cannot contract simultaneously — it would lock the joint. This is reciprocal inhibition: activating one pathway suppresses the opposing pathway.

After a neuron fires, there's a **refractory period** where it cannot fire again. This prevents chaotic re-firing.

### The Implementation

Two mutually exclusive modes:

| | REFLEX | DELIBERATIVE |
|---|--------|-------------|
| Model | Haiku only | Haiku → Sonnet → Opus |
| Max tokens | 150 | 4096 |
| Chain-of-thought | No | Yes |
| GTO monitoring | No | Yes |
| Modulation | No | Yes |
| Latency | ~200ms | 1-10s |

A Haiku classifier (<100 tokens) determines the mode for each query. Once set, the mode is **locked** for a refractory period of 3 turns.

### Sequence Diagram

```
Turn 1: "Capital of France?" → Classifier: REFLEX
         Mode locked. Refractory = 3.

Turn 2: "Is it in Europe?" → Refractory = 2. LOCKED.
         (Even if this needed DELIBERATIVE, it stays REFLEX)

Turn 3: "What currency?" → Refractory = 1. LOCKED.

Turn 4: "Compare Kant and Nietzsche" → Refractory = 0. UNLOCKED.
         Classifier: DELIBERATIVE.
         Mode locked. Refractory = 3.

Turn 5: "History of computing" → Refractory = 2. LOCKED.
         (Stays DELIBERATIVE — which is correct here)
```

The refractory period prevents **mode thrashing** — a common problem in router-based systems where the mode flips every turn based on surface-level classification.

---

## Mechanism 4: Reflex Reversal (Phase Modulation)

### The Biology

During the swing phase of walking, touching the top of your foot triggers a flexion reflex (lift the foot higher to clear the obstacle). During the stance phase, the exact same stimulus triggers the **opposite** reflex — extension (press down to maintain balance).

Same sensory input, same neural circuit, opposite output. The behavior is determined by the **phase** of the locomotion cycle.

### The Implementation

One modulator agent with two opposite system prompts:

**EXPLORATION phase** (early in conversation):
> "Amplify divergent ideas, add unexpected connections, challenge assumptions, suggest unexplored angles"

**CONSOLIDATION phase** (later, or on keyword):
> "Inhibit divergence, force convergence, eliminate redundancies, structure actionable points"

Phase detection (`modulator.py:46-65`):

```python
# Keyword detection (priority)
for keyword in ["synthesize", "conclude", "summarize"]:
    if keyword in query → CONSOLIDATION

# Automatic turn-based detection
if turn_count >= phase_switch_turn → CONSOLIDATION

# Default
return EXPLORATION
```

### Sequence Diagram

```
Turn 4 (EXPLORATION phase):
  Agent response: "Kant vs Nietzsche analysis..."
  Modulator adds: "What if both converged on individual autonomy?
                   Neuro parallel: heuristics (Kant) + contextual learning (Nietzsche)?
                   Non-Western ethics dissolve this opposition entirely?"

Turn 6 (CONSOLIDATION phase, keyword "synthesize"):
  Agent response: "Session covered: France, philosophy, computing..."
  Modulator restructures: "1. France — Paris (factual, settled)
                           2. Morality — Kant vs Nietzsche (irreconcilable but productive)
                           3. Computing — 3 eras: pioneers → hardware → AI
                           Conclusion: Each topic reveals a structure/freedom tension."
```

Same agent. Same architecture. Opposite behavior. Context-dependent.

---

## Pipeline Flow

Complete flow for a DELIBERATIVE query:

```
orchestrator.process(query)
│
├─ 1. context.increment_turn()
│     turn_count++, refractory-- (if >0)
│
├─ 2. mode_switch.classify(query)
│     ├─ refractory > 0? → return current mode (LOCKED)
│     └─ refractory = 0? → Haiku classifier → REFLEX or DELIBERATIVE
│                           lock_mode(mode, refractory=3)
│
├─ 3a. [REFLEX] → recruiter.process_reflex()
│       Haiku, 150 tokens, direct response, done.
│
└─ 3b. [DELIBERATIVE] → _process_deliberative()
        │
        ├─ 4. recruiter.process(query)
        │     for level in [Haiku, Sonnet, Opus]:
        │       call agent → parse evaluation
        │       if should_escalate() and not last level → continue
        │       else → return (response, evaluation)
        │
        ├─ 5. monitor.analyze(response)
        │     Haiku checks for overload signals
        │     if overloaded:
        │       decompose → subtasks[]
        │       for each subtask:
        │         recruiter.process(subtask)  ← restart from Haiku
        │         monitor.analyze(sub_response)
        │       combine results
        │
        └─ 6. modulator.modulate(response, phase)
              detect_phase() → EXPLORATION or CONSOLIDATION
              apply corresponding system prompt
              return modulated response
```

---

## Shared State

`utils/context.py` maintains the session state accessible by all components:

```python
SharedContext:
  mode: REFLEX | DELIBERATIVE | None
  phase: EXPLORATION | CONSOLIDATION
  turn_count: int
  refractory_counter: int
  conversation: [{role, content}, ...]
  events: [BioEvent(timestamp, type, details), ...]
```

All biological events are logged to both console (colored) and file (`spinal_loop.log`), with token counts for cost tracking.
