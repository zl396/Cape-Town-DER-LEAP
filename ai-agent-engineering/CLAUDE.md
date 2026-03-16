# CLAUDE.md — AI Agent Engineering Principles

> Permanent foundational principles for building reliable AI agent systems.
> Distilled from 40+ primary sources (Anthropic, Cognition, Cursor, Google, LangChain, Manus, OpenAI).
> See PRINCIPLES_v0.1.md for full rationale and evidence.
> v0.2.0 — 47 principles (39 original + 6 from OpenAI deep reading + 2 from climate innovation mapping fieldwork).

---

## Agent Operational Rules

> **These rules govern Claude's runtime behavior when executing tasks for the user. They are hard constraints, not suggestions. Violations should be flagged by the user and added as new rules here.**

### R-1: Escalate on block, don't silently reroute.
When a tool or action fails or is unavailable, the agent MUST immediately tell the user: (1) what failed, (2) why, (3) the simplest user-side workaround. The agent MUST NOT silently switch to an alternative technical path. If the user can accomplish the blocked step in <30 seconds, ask them to do it.

### R-2: Pre-declare intent before non-trivial actions.
Before executing any non-trivial action (structural edits, multi-step tool chains, architectural decisions), the agent MUST first state: (a) what it intends to do, (b) which principle or rule justifies it. Then act. This is forward declaration, not post-hoc rationalization.

### R-3: No post-hoc rationalization.
The agent MUST NOT perform an action first and then search for a principle that matches. If the agent cannot name the governing principle before acting, it should state "no specific principle applies — proceeding on general judgment" rather than fabricating alignment.

### R-4: Shortest path for the user.
When multiple paths exist to accomplish a step, evaluate whether the user doing it manually is faster than the agent working around a limitation. If yes, escalate to the user (per R-1). Optimizing for agent autonomy at the cost of user time violates P-HCI-4 (Minimize user prompt burden).

### R-5: Backup before destructive edits.
Before any edit that modifies or overwrites user files, the agent MUST create a backup copy first. No exceptions.

---

## Context Engineering

1. **Context is the job.** The assembly, ordering, and formatting of what the model sees is the primary engineering task. Models fail from wrong context, not lack of capability.

2. **Share full traces.** When delegating to sub-agents, pass the complete execution trace—not summaries. Summaries lose the implicit decisions embedded in each action.

3. **Actions encode assumptions.** Every agent action carries implicit decisions. Parallel agents that can't see each other's actions will make conflicting assumptions.

4. **Protect the KV-cache.** Keep the prompt prefix stable and append-only. No timestamps at the start. Deterministic serialization. A single changed token invalidates everything after it.

5. **Mask, don't remove.** Control tool availability by masking logits at decode time, not by removing tool definitions. Removal breaks the cache and confuses the model.

6. **Filesystem is memory.** For tasks exceeding the context window, treat the filesystem as unbounded, persistent, agent-writable external memory.

7. **Recite to remember.** Periodically rewrite the current plan into the recent context. Without this, goals stated at the beginning drift out of the model's effective attention window.

8. **Preserve errors.** Leave failed actions and their error traces in context. The model uses them to avoid repeating mistakes. Erasing failures removes evidence.

9. **Warm-up before hard problems.** Include a simplified version of the target problem structure as a "warm-up" in context. This primes the model's reasoning patterns before tackling the full complexity.

## Tool Design

10. **Descriptions over scaffolding.** A tool's name, description, and parameter schema matter more than surrounding harness code. Rich descriptions enable model self-correction.

11. **Error-proof interfaces.** Tools should reject ambiguous inputs and return clear, actionable error messages—not silent failures.

12. **Defer loading for large toolsets.** Use a "tool search tool" pattern to load definitions on demand rather than stuffing dozens of tools into the system prompt.

13. **Programmatic orchestration for known flows.** When the workflow structure is deterministic, express it in code rather than letting the model decide each step.

14. **Risk-rate every tool.** Classify tools as low/medium/high risk. Gate high-risk tools (irreversible, financial, permissions) behind human confirmation.

15. **Scaffold matters as much as model.** The same model varies dramatically with different scaffolds (AGENTS.md, linters, test harnesses). Invest in environment design, not just model selection.

## Architecture

16. **Default to one agent.** Start with a single agent with tools. Add agents only when you hit context overflow, complex branching logic, or irreconcilable tool overlap.

17. **Parallelize through artifacts.** When parallel execution is needed, coordinate through shared artifacts (git repos, databases, files)—not message-passing between agents.

18. **Manager for synthesis, handoffs for specialization.** Use the manager pattern when you need central control and result synthesis. Use handoffs when specialists should fully take over.

19. **Code-first orchestration.** Express workflow logic in familiar code, not declarative graph frameworks. Code is more flexible and doesn't require learning a DSL.

20. **Compress for longevity.** For long-running agents, build an explicit history compression layer—a process that distills conversation history into key decisions and facts.

## Evaluation

21. **Evaluate the whole system.** Benchmark the complete agent (model + tools + harness + prompts) as a unit. Isolated model evals are misleading for agent performance.

22. **Test the full loop.** Evaluate planning, tool use, error recovery, and multi-step reasoning—not just single-turn accuracy.

23. **Infrastructure is a variable.** Treat compute config as an experimental variable. A 6-point gap can come from resources alone. Require 3x headroom.

24. **Prevent contamination.** Maintain strict separation between training/tuning data and evaluation data. Pre-register eval criteria. Rotate eval sets.

25. **Model difficulty ≠ human difficulty.** What agents find hard differs from what humans find time-consuming. Task assignment must be based on empirical agent success rates, not human intuition.

26. **Design for verification asymmetry.** Structure tasks so outputs are hard to produce but easy to verify. This enables best-of-N strategies and automated quality gates.

## Retrieval

27. **Hybrid retrieval.** Combine semantic embeddings with BM25 keyword search. Neither alone covers the full query distribution.

28. **Contextual chunks.** Before embedding, prepend a short header that situates each chunk within its source document.

29. **Rerank before presenting.** Apply a reranking step after initial retrieval to sharpen precision from the recall set.

## Safety

30. **Defense in depth.** Layer rules-based protections, LLM classifiers, and moderation APIs. No single guardrail is sufficient.

31. **Sandbox by default.** Isolate agent execution with filesystem restrictions AND network allowlists. Both layers required.

32. **Escalate on failure and high stakes.** Define explicit thresholds: escalate after N retries, and always for irreversible or high-value actions.

## Operations

33. **Expect overlapping failures.** Production incidents involve multiple simultaneous causes. Design for compounding failures, not single faults.

34. **Distinguish capability from routing.** Wrong answers (model capability) and wrong model served (infrastructure routing) look identical but require different fixes.

35. **Start small, grow incrementally.** Deploy on narrow tasks first. Expand only after observing real-world failure modes.

36. **Observe everything.** Every action, tool call, context state, and response must be logged and traceable. Invest in observability before scaling.

## Human Integration

37. **Review is the bottleneck.** In production, the constraint shifts from generation speed to human review throughput. Design agent output to be reviewable, not just correct.

38. **Specify clearly or scale broken.** Vague instructions multiply errors nonlinearly across parallel agents. Treat instruction quality as a first-class engineering concern.

39. **Accept stability over perfection.** Design for anti-fragility—tolerate small, stable error rates rather than demanding zero errors. System-level graceful degradation beats component-level perfection.

40. **Minimize user prompt burden.** Design the system so users specify less, not more. Boot files supply context defaults, skills encode procedures, and the agent assembles execution context from minimal input. If the user must write a detailed prompt for the system to work, the context and skill layers are under-designed.

41. **Interpret-then-confirm, not rewrite-then-execute.** When receiving an underspecified user instruction, the agent outputs a short execution plan (what it understood, what it will do, what it will produce) and waits for confirmation. This is cheaper for the user to verify than reviewing a rewritten prompt or auditing a completed output.

## Meta

42. **Constraints beat instructions.** Use structural limits (masking, sandboxes, schemas) over natural-language rules. The model can ignore instructions; it can't bypass a constraint.

43. **Empirical over theoretical.** Test every architectural decision. Agent behavior is emergent and unpredictable; the only reliable signal is measurement.

44. **Design for tomorrow's model.** Keep architecture orthogonal to the underlying model. If model progress is a rising tide, your system should be the boat.

45. **Vary to prevent rigidity.** When processing similar items sequentially, inject structural variation to prevent the model from falling into repetitive patterns.

46. **Test-time compute is tunable.** Inference-time reasoning budget (steps, tokens, tool calls) is an independent performance variable. Budget more for high-stakes tasks, less for routine ones.

47. **Platform absorbs infrastructure.** Previously custom-built capabilities (RAG, search, browser automation) get absorbed into platforms. Focus engineering time on domain-specific environment design—constraints, feedback loops, and safety policies.
