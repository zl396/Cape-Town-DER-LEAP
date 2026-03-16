# Reading Progress — AI Agent Engineering Archive

> Status file for multi-session reading project. Update after each session.

## Completed Sources

### Anthropic (ALL DONE — 20+ articles across 4 tiers)
- Building Effective Agents, Prompt Caching, Contextual Retrieval, Extended Thinking, Tool Use Best Practices, Building MCP Servers, Prompt Engineering Guide, Research-to-Eval Pipeline, Preventing Harms, Evaluations Design, Quantifying Infrastructure Noise, Building C Compiler, Sandboxing, Advanced Tool Use, Desktop Extensions, SWE-bench Performance, Postmortem of Three Issues, Claude Course (MCP Advanced Topics, Claude Code in Action)

### Cognition (PARTIAL — 2 of 16 articles read)
- **Read:** "Don't Build Multi-Agents" (full), INDEX.md
- **Unread:** DeepWiki, Devin Review, Agent Trace, Closing the Agent Loop, SWE-bench Technical Report, Evaluating Coding Agents, and ~10 others (see Cognition/INDEX.md)

### Cursor (PARTIAL — 2 of 19 articles read)
- **Read:** "Towards Self-Driving Codebases" (full), "Best Practices for Coding with Agents" (full)
- **Unread:** ~17 others (see folder listing)

### Google Gemini (PARTIAL — INDEX only)
- **Read:** INDEX.md only
- **Unread:** All articles + handbook PDF. INDEX lists articles across Agent Architecture, Evaluation, RAG, and Safety categories.

### LangChain (PARTIAL — 3 of 45 docs read)
- **Read:** context-engineering.md, philosophy.md, agents.md
- **Unread:** guardrails, human-in-the-loop, long-term-memory, multi-agent/*, retrieval, and ~38 others

### Manus (PARTIAL — 1 of 16 articles read)
- **Read:** "Context Engineering for AI Agents" (full, Chinese)
- **Unread:** ~15 others

### OpenAI (ALL DONE — 31 files across 4 subdirectories)

#### Overview & Index (3 files)
- openai-for-science.md, research-overview.md, research-index.md — Browsed for context

#### Engineering & Product (8 files, ALL deeply read)
- **a-practical-guide-to-building-agents.pdf** (32pp) — Deep read with combined-style notes. Seven-layer guardrail taxonomy, optimistic execution, tripwire pattern, tool three-way classification, graduated autonomy. 9 existing principles confirmed, 5+ new candidates.
- **unrolling-the-codex-agent-loop.md** — Codex agent loop internals: prompt construction order, caching mechanics, compaction, stateless-by-design for ZDR compliance.
- **unlocking-the-codex-harness.md** — App Server architecture: JSON-RPC, Item/Turn/Thread primitives, bidirectional approval flow, MCP rejected for App Server protocol.
- **harness-engineering.md** — Most principle-dense article. 5-month experiment: 0 lines human code, ~1M lines generated. Progressive disclosure, agent legibility, constraints via linters, entropy/garbage collection. 5 new principle candidates.
- **introducing-chatgpt-agent.md** — Unified agent: CUA + Deep Research + ChatGPT. Virtual computer as cross-tool context layer. Five-layer safety architecture. Preemptive bio-safety classification.
- **computer-using-agent.md** — CUA technical details: GUI as universal interface, perception-reasoning-action loop, test-time scaling evidence. Three-class safety risk taxonomy.
- **new-tools-for-building-agents.md** — Responses API, Agents SDK, built-in tools (web search, file search, computer use). Platform absorbs infrastructure. Assistants API deprecated mid-2026.
- **introducing-codex.md** — Cloud sandbox (fully offline during execution), AGENTS.md scope rules, citation system, codex-1 vs o3 patch comparison, async multi-agent workflow vision.
- **introducing-deep-research.md** — End-to-end RL training, test-time scaling evidence (Pass Rate vs Max Tool Calls), model difficulty ≠ human difficulty finding, MCP support added Feb 2026.
- **chatgpt-agent-system-card.md** — Summary page. Confirmed High bio-safety classification.

#### Research (12 files, ALL read)
- **MLE-bench** — 75 Kaggle ML tasks. Scaffold dramatically affects performance (AIDE best).
- **PaperBench** — 20 ICML paper replication, 8,316 gradable sub-tasks. Best agent 21%.
- **SWE-Lancer** — 1,400+ Upwork tasks worth $1M. Internet variability as primary noise source.
- **BrowseComp** — 1,266 hard-to-find info tasks. Asymmetry of verification. Best-of-N > majority voting. Deep Research 51.5%.
- **GDPval** — 44 occupations, 1,320 tasks. Frontier models approaching expert quality. 100x faster/cheaper. Performance tripled GPT-4o→GPT-5 in one year.
- **introducing-o3-and-o4-mini** — Dual scaling laws (train-time + test-time). Tool use learned through RL. o-series and GPT-series converging.
- **learning-to-reason-with-llms** — o1 foundational paper. CoT as safety tool (monitoring hidden reasoning). Reward hacking observations.
- **Full papers** (MLE-bench, PaperBench, SWE-Lancer PDFs) — Skimmed via md summaries, PDFs available for deeper reference.

#### Science (6 files, ALL read)
- **accelerating-science-with-gpt-5** — Warm-up problem pattern. Attribution failure warning (Clique-Avoiding Codes case). GPT-5 as research partner, not autonomous researcher.
- **introducing-prism** — LaTeX-native AI writing workspace. Less relevant to agent engineering.
- **frontierscience** — New benchmark: Olympiad (77%) vs Research (25%) split. Rubric-based open-ended grading.
- **gpt-5-2-theoretical-physics** — 12-hour continuous reasoning for gluon amplitude proof. Extreme test-time scaling.
- **gpt-5-lowers-protein-synthesis-cost** — Lab-in-the-loop: GPT-5 + Ginkgo Bioworks cloud lab. Programmatic validation of AI-designed experiments.
- **first-proof-submissions** — 5/10 research-level math proofs likely correct. Model getting tangibly smarter day by day during training.

### ByteDance
- **Status:** Folder exists but was empty at time of check

## Key Deliverables Produced

1. **CLAUDE.md** — 45 distilled principles in compact format (auto-loads as project context)
2. **PRINCIPLES_v0.1.md** — Full version with Statement / Rationale / Evidence for each principle, plus quick-reference table and bibliography

## Recommended Reading Priority for Next Sessions

1. **Cognition** — "Devin Review", "Agent Trace", "Closing the Agent Loop", "Evaluating Coding Agents". Core evidence for review bottleneck, observability, and eval principles. Strongest next source for agent engineering.
2. **Google Gemini** — Handbook PDF + scaling paper. Only source with empirical data on when multi-agent hurts performance. Thinnest evidence base in current principles.
3. **Manus** — Remaining ~15 articles. First article already contributed heavily; rest may have more implementation detail.
4. **Cursor** — ~17 remaining, mostly product updates. Skim for novel insights.
5. **LangChain** — Pick 3: guardrails.md, human-in-the-loop.md, long-term-memory.md. Rest is implementation docs.

## New Principle Candidates from OpenAI Reading

> **Integration status (v0.1.1):** 6 of the 14 candidates below were promoted to independent principles in PRINCIPLES_v0.1.md: #4 → P-META-5, #5 → P-META-6, #7 → P-EVAL-5, #10 → P-EVAL-6, #11 → P-TOOL-6, #13 → P-CTX-9. The remaining 8 were folded as supplementary evidence into existing principles (#1 → P-ARCH-1, #2 → P-SAFE-1, #14 → P-TOOL-2, #9 → P-EVAL-1) or deferred to v0.2 (#3, #6, #8, #12). The list below is preserved as a reference for the original candidates.

### From Engineering & Product
1. **"Unify before multiplying"** — Consolidate capabilities into one agent before splitting into multiple. Evidence: OpenAI merged Operator + Deep Research + ChatGPT into unified agent after users confused the separate tools.
2. **"Preemptive safety classification"** — Apply highest risk tier proactively even without confirmed evidence of harm. Evidence: ChatGPT Agent classified as High bio-risk without definitive evidence.
3. **"Universal interfaces trade efficiency for generality"** — GUI (screenshot+mouse) covers the long tail; API covers the common path. Mature systems mix both. Evidence: CUA at 38.1% OSWorld vs 72.4% human; useful despite low accuracy.
4. **"Test-time compute is a tunable variable"** — Agent performance improves with more reasoning steps/time, independent of model size. Evidence: CUA, Deep Research, BrowseComp, FrontierScience, and 12-hour physics proof all show smooth scaling.
5. **"Platform absorbs infrastructure"** — Previously custom-built infrastructure (RAG, search, browser automation) gets absorbed into platform-level tools. Agent engineers shift focus to business logic and safety. Evidence: Responses API with built-in web search, file search, computer use.
6. **"Stateless over stateful"** — Give developers state control rather than managing it in the platform. Evidence: Assistants API (stateful) deprecated in favor of Responses API (stateless).
7. **"Model difficulty ≠ human difficulty"** — Tasks models find hard differ from tasks humans find time-consuming. Task assignment should be based on empirical agent success rates. Evidence: GDPval pass rate correlated with economic value, not estimated hours.
8. **"Learned strategies over programmed strategies"** — End-to-end RL lets models learn when/how to use tools, vs hand-coded orchestration. Evidence: Deep Research's RL-trained search strategy; o3/o4-mini tool use through RL.

### From Research
9. **"Evaluate economic value, not just accuracy"** — Benchmarks should map to real-world dollar value. Evidence: SWE-Lancer ($1M in Upwork tasks), GDPval (GDP-weighted occupations).
10. **"Asymmetry of verification enables scaling"** — Design tasks that are hard to solve but easy to verify; this enables best-of-N and self-evaluation strategies. Evidence: BrowseComp design philosophy.
11. **"Scaffolding amplifies model capability"** — Same model + different scaffold = dramatically different performance. Evidence: MLE-bench (AIDE vs others), PaperBench scaffolding comparison.
12. **"Dual scaling laws: train-time + test-time"** — Both pre-training compute and inference compute independently improve performance. Evidence: o1/o3 papers showing smooth scaling on both axes.

### From Science
13. **"Warm-up scaffolds unlock capability"** — Providing a simplified version of the target problem as context significantly improves performance on the full problem. Evidence: Kerr black hole symmetry case.
14. **"Validate outputs programmatically before execution"** — AI-designed actions must pass programmatic feasibility checks before real-world execution. Evidence: CFPS lab-in-the-loop with strict validation preventing "paper experiments".

## Open Questions

- Should principles be organized differently (e.g., by workflow stage instead of domain)?
- How to handle contradictions between sources (e.g., Cognition says "don't build multi-agents" vs. Cursor runs 1000 commits/hour with multi-agents)?
- V0.2 should consider adding domain-specific principles for energy system modeling / policy analysis applications
- ~~Several OpenAI candidates overlap with existing principles~~ **RESOLVED in v0.1.1**: Deduplication completed. 6 promoted, 4 folded as evidence, 4 deferred.
- ~~Should "test-time compute scaling" be elevated to a top-level principle?~~ **RESOLVED in v0.1.1**: Yes, promoted as P-META-5.
- Deferred candidates (#3 universal interfaces, #6 stateless over stateful, #8 learned strategies, #12 dual scaling laws) — worth revisiting when more evidence accumulates from other sources.
