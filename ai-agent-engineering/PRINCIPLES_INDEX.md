# Principles Index — Lightweight Lookup Table
# Source: PRINCIPLES_v0.1.md (same directory)
# Usage: Read this file for quick reference. For full rationale + evidence, read the line range from PRINCIPLES_v0.1.md.

## I. Context Engineering (lines 15-90)
| ID | One-Liner | Lines |
|---|---|---|
| P-CTX-1 | Context engineering is the job | 19-25 |
| P-CTX-2 | Share full traces, not summaries | 27-33 |
| P-CTX-3 | Actions carry implicit decisions | 35-41 |
| P-CTX-4 | Design around the KV-cache (stable prefix, append-only, deterministic serialization) | 43-49 |
| P-CTX-5 | Mask tools at logit level, don't remove from prompt | 51-57 |
| P-CTX-6 | Filesystem as unbounded persistent memory | 59-65 |
| P-CTX-7 | Recite plan into recent context to prevent attention drift | 67-73 |
| P-CTX-8 | Preserve errors in context — don't hide or retry silently | 75-81 |
| P-CTX-9 | Warm-up problems prime complex reasoning | 83-90 |

## II. Tool Design (lines 92-143)
| ID | One-Liner | Lines |
|---|---|---|
| P-TOOL-1 | Rich descriptions > more scaffolding code | 97-103 |
| P-TOOL-2 | Reject ambiguous inputs, return actionable errors | 105-111 |
| P-TOOL-3 | Defer tool loading — "tool search tool" pattern | 113-119 |
| P-TOOL-4 | Programmatic orchestration for deterministic flows | 121-127 |
| P-TOOL-5 | Risk-rate every tool (low/med/high), gate high-risk | 129-135 |
| P-TOOL-6 | Scaffold (AGENTS.md, linters, test harness) matters as much as model | 137-143 |

## III. Architecture (lines 147-190)
| ID | One-Liner | Lines |
|---|---|---|
| P-ARCH-1 | Default to single agent; add agents only at measurable triggers | 151-157 |
| P-ARCH-2 | Parallelize through shared artifacts (git, files, DB) not messages | 159-165 |
| P-ARCH-3 | Manager for synthesis, handoffs for specialization | 167-173 |
| P-ARCH-4 | Code-first orchestration over declarative graphs | 175-181 |
| P-ARCH-5 | Compress history for long-duration agents | 183-190 |

## IV. Evaluation (lines 193-243)
| ID | One-Liner | Lines |
|---|---|---|
| P-EVAL-1 | Evaluate whole system (model+tools+harness+prompts) | 197-203 |
| P-EVAL-2 | Multi-turn evaluation: planning, tool use, error recovery | 205-211 |
| P-EVAL-3 | Infrastructure config is an experimental variable (3x headroom) | 213-219 |
| P-EVAL-4 | Prevent contamination: held-out data, pre-register criteria | 221-227 |
| P-EVAL-5 | Model difficulty ≠ human difficulty — use empirical data | 229-235 |
| P-EVAL-6 | Design for verification asymmetry (hard to produce, easy to verify) | 237-243 |

## V. Retrieval (lines 247-273)
| ID | One-Liner | Lines |
|---|---|---|
| P-RAG-1 | Hybrid retrieval: semantic + BM25 | 251-257 |
| P-RAG-2 | Prepend contextual header before embedding chunks | 259-265 |
| P-RAG-3 | Rerank after initial retrieval | 267-273 |

## VI. Safety (lines 277-303)
| ID | One-Liner | Lines |
|---|---|---|
| P-SAFE-1 | Defense-in-depth: rules + LLM classifiers + moderation APIs | 281-287 |
| P-SAFE-2 | Sandbox by default: filesystem + network isolation | 289-295 |
| P-SAFE-3 | Escalate on N retries or high-stakes actions | 297-303 |

## VII. Operations (lines 307-341)
| ID | One-Liner | Lines |
|---|---|---|
| P-OPS-1 | Overlapping failures are the default in production | 311-317 |
| P-OPS-2 | Capability failure ≠ routing failure (same symptoms, different fixes) | 319-325 |
| P-OPS-3 | Start narrow, validate, expand incrementally | 327-333 |
| P-OPS-4 | Observability: log every action, tool call, context state | 335-341 |

## VIII. Human Integration (lines 345-388)
| ID | One-Liner | Lines |
|---|---|---|
| P-HCI-1 | Review throughput is the bottleneck, not generation speed | 349-355 |
| P-HCI-2 | Vague instructions × N agents = N conflicting interpretations | 357-363 |
| P-HCI-3 | Anti-fragile: tolerate stable error rates, don't demand perfection | 365-371 |
| P-HCI-4 | System minimizes user prompt burden (boot files + skills + inference) | 373-379 |
| P-HCI-5 | Interpret-then-confirm: show execution plan, not rewritten prompt | 381-388 |

## IX. Meta-Principles (lines 391-441)
| ID | One-Liner | Lines |
|---|---|---|
| P-META-1 | Structural constraints > natural-language instructions | 395-401 |
| P-META-2 | Empirical over theoretical — test everything | 403-409 |
| P-META-3 | Architecture orthogonal to model — design for tomorrow's model | 411-417 |
| P-META-4 | Inject variation to prevent repetitive pattern lock-in | 419-425 |
| P-META-5 | Test-time compute is independently tunable (budget more for high-stakes) | 427-433 |
| P-META-6 | Platform absorbs infra; invest in domain-specific environment design | 435-441 |
