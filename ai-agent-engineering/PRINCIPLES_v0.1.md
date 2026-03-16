# Principles for AI Agent Engineering v0.1

**Author:** Julio | **Date:** 2026-03-12 | **Method:** Dalio-style synthesis from 40+ primary sources

> "The agent's future will be built one context at a time. Design them well."  — Manus

---

## How to Use This Document

This document distills hard-won lessons from Anthropic, Cognition, Cursor, Google DeepMind, LangChain, Manus, and OpenAI into a set of reusable principles. Each principle follows the pattern: **name → statement → rationale → source evidence**. They are organized into seven domains. Use them as a pre-flight checklist before building, a diagnostic tool when something breaks, and a teaching reference when onboarding collaborators.

---

## I. Context Engineering

*The single most important discipline in agent construction. Models rarely fail because they are incapable; they fail because they receive the wrong context.*

### P-CTX-1: Context Engineering Is the Job

**Statement:** Treat the assembly, ordering, and formatting of everything the model sees as the primary engineering task—not an afterthought.

**Rationale:** Every source in this archive converges on the same conclusion. Cognition calls it the reason not to build multi-agents. Manus rebuilt their framework four times around it. LangChain declares it the "#1 job of AI Engineers." Anthropic's building-effective-agents guide structures everything around what goes into the prompt.

**Evidence:** Cognition "Don't Build Multi-Agents" (Walden Yan, 2025-06); Manus "Context Engineering for AI Agents" (Yichao Ji, 2025-07); LangChain context-engineering docs; Anthropic "Building Effective Agents."

### P-CTX-2: Share Full Traces, Not Summaries

**Statement:** When an agent delegates to a sub-process, pass the full execution trace—not just the final answer or a summary message.

**Rationale:** Summaries lose the implicit decisions embedded in each action. When a sub-agent sees only the conclusion, it has no way to know *why* a choice was made and may make conflicting assumptions. Cognition elevates this to their Principle 1, observing that even Claude Code's subagents follow this discipline by limiting themselves to read-only questions rather than writing code without full context.

**Evidence:** Cognition Principle 1 ("Share context, and share full agent traces, not just individual messages"); Anthropic C-compiler parallel agent design (shared git repo as context surface); Cursor Planner→Executor→Worker hierarchy.

### P-CTX-3: Actions Carry Implicit Decisions

**Statement:** Recognize that every action an agent takes encodes assumptions. Parallel agents that cannot see each other's actions will make conflicting assumptions.

**Rationale:** Cognition's Principle 2. The Flappy Bird example is illustrative: two sub-agents building visual assets independently produce incompatible styles because neither can see the other's choices. This is why naive multi-agent parallelism fails—not because the individual agents are stupid, but because the decision space is implicitly partitioned without coordination.

**Evidence:** Cognition Principle 2 ("Actions carry implicit decisions, and conflicting decisions carry bad results"); Google "Towards a Science of Scaling Agent Systems."

### P-CTX-4: Design Around the KV-Cache

**Statement:** Structure your prompt so that the prefix is stable and append-only. A single changed token in the prefix invalidates all cached computation downstream.

**Rationale:** In production agents, the input-to-output token ratio can be 100:1 (Manus). Cache hits reduce cost by 10x (Anthropic Claude prompt caching: $0.30 vs. $3.00 per million tokens). Three rules follow: (a) never put volatile data like timestamps at the start of the system prompt, (b) make context append-only—never rewrite prior observations, (c) ensure serialization is deterministic (many JSON libraries don't guarantee key order).

**Evidence:** Manus "Context Engineering" (KV-cache section); Anthropic "Prompt Caching with Claude"; Anthropic "Contextual Retrieval."

### P-CTX-5: Mask, Don't Remove

**Statement:** When dynamically controlling which tools an agent can use, mask unavailable tools at the logit level rather than removing them from the tool list.

**Rationale:** Removing tools changes the prompt prefix and invalidates the KV-cache for everything that follows. It also confuses the model when prior conversation turns reference tools that are no longer defined. Manus uses a context-aware state machine that masks token logits at decode time, supporting three modes: auto, required, and specified.

**Evidence:** Manus "Context Engineering" (masking section); Anthropic "Advanced Tool Use" (Tool Search Tool with defer_loading).

### P-CTX-6: Use the Filesystem as Extended Context

**Statement:** For tasks that exceed the context window, treat the filesystem as unbounded, persistent, agent-writable memory.

**Rationale:** Even 128K-token windows are insufficient for real-world agents interacting with web pages, PDFs, and multi-step workflows. The filesystem is unlimited, naturally persistent, and directly operable by the agent. The model learns to write and read files on demand—not just for storage but as structured external memory. Compression strategies should be designed to be recoverable (e.g., store URLs so page content can be re-fetched).

**Evidence:** Manus "Context Engineering" (filesystem-as-context section); Cursor scratchpad.md pattern; Anthropic Claude Code's file-based planning.

### P-CTX-7: Recite to Remember

**Statement:** Have the agent periodically rewrite its current plan or goals into the recent context to avoid the "lost in the middle" problem.

**Rationale:** Manus creates a `todo.md` file and rewrites it after each major step. This is not cosmetic—it pushes the global plan into the model's recent attention window. With ~50 tool calls per task, goals stated only at the beginning drift out of effective attention. Cursor's scratchpad.md serves the same function.

**Evidence:** Manus "Context Engineering" (recitation section); Cursor scratchpad.md freshness mechanism.

### P-CTX-8: Preserve Errors in Context

**Statement:** Do not hide, retry silently, or erase failed actions. Leave the full error trace in the conversation.

**Rationale:** When the model sees a failed action and its stack trace, it implicitly updates its beliefs and avoids repeating the mistake. Erasing failures removes the evidence that would prevent the same error. Error recovery is one of the clearest indicators of genuine agent behavior.

**Evidence:** Manus "Context Engineering" (error preservation section); Anthropic SWE-Bench agent (error-proofing tools return errors as assistant-readable messages).

### P-CTX-9: Use Warm-Up Problems to Prime Complex Tasks

**Statement:** When facing a complex task, include a simplified version of the same problem structure in the prompt as a "warm-up" before presenting the full problem.

**Rationale:** In OpenAI's science acceleration experiments, GPT-5 failed to derive the hidden SL(2,ℝ) symmetry of the Kerr black hole wave equation when asked directly. But after being given a simpler flat-space version of the same structure as a warm-up, the model successfully derived the full result after 18 minutes of reasoning. This pattern generalizes: giving the model a tractable version of the target problem structure establishes the right reasoning patterns before tackling the hard case. This is distinct from few-shot examples—it's about building up the right conceptual scaffolding in context.

**Evidence:** OpenAI "Early Experiments in Accelerating Science with GPT-5" (Kerr black hole warm-up case); OpenAI "OpenAI for Science" (prompt strategies: "Prime the Model with a Warm-Up Problem").

---

## II. Tool Design

*Tools are how agents interact with the world. Their design determines the ceiling of agent capability.*

### P-TOOL-1: Invest in Tool Descriptions, Not More Code

**Statement:** The quality of a tool's name, description, and parameter schema matters more than additional scaffolding code.

**Rationale:** Anthropic's SWE-bench agent achieved top performance with minimal harness code. The key differentiator was rich, carefully written tool descriptions that gave the model enough information to self-correct. Similarly, OpenAI's guide emphasizes that tool overlap and similarity cause more failures than tool count—some systems manage 15+ well-defined distinct tools while others struggle with fewer than 10 overlapping ones.

**Evidence:** Anthropic "Claude's SWE-bench Performance"; OpenAI "A Practical Guide to Building Agents" (tool overload section); Anthropic "Building Effective Agents."

### P-TOOL-2: Error-Proof Tool Interfaces

**Statement:** Design tools to reject ambiguous inputs and return clear, actionable error messages rather than silent failures.

**Rationale:** Anthropic's SWE-bench agent enforces absolute paths (rejecting relative ones), requires exactly one match for text replacements, and returns errors as readable messages in the assistant turn. This lets the model self-correct without human intervention.

**Evidence:** Anthropic "Claude's SWE-bench Performance" (error-proofing section). OpenAI "GPT-5 Lowers Protein Synthesis Cost" adds a production example: all AI-designed experiments passed strict programmatic validation before robotic execution, preventing "paper experiments" that look plausible in text but can't be carried out physically.

### P-TOOL-3: Defer Tool Loading for Large Toolsets

**Statement:** When a system has dozens or hundreds of tools, use a "tool search tool" pattern—load tool definitions on demand rather than putting them all in the system prompt.

**Rationale:** Anthropic's Tool Search Tool reduced input tokens by 85% and improved accuracy by enabling the model to search for relevant tools rather than scanning a massive list. The `defer_loading` parameter lets tools be registered but not included in the prompt until explicitly requested.

**Evidence:** Anthropic "Introducing Advanced Tool Use" (Tool Search Tool section).

### P-TOOL-4: Prefer Programmatic Orchestration for Deterministic Flows

**Statement:** When a workflow has a known, deterministic structure, use code-based tool orchestration instead of letting the model decide each step.

**Rationale:** Anthropic's Programmatic Tool Calling showed 37% token reduction and 200KB→1KB context reduction by expressing deterministic tool chains in code rather than natural language. This removes the model from decisions it shouldn't be making—saving tokens, reducing latency, and eliminating a class of errors.

**Evidence:** Anthropic "Introducing Advanced Tool Use" (Programmatic Tool Calling section).

### P-TOOL-5: Assign Risk Levels to Every Tool

**Statement:** Classify each tool as low, medium, or high risk based on read-only vs. write access, reversibility, required permissions, and financial impact. Gate high-risk tools behind human confirmation.

**Rationale:** OpenAI's guardrails framework recommends risk ratings that trigger automated actions—pausing for guardrail checks before high-risk functions and escalating to humans when needed. This prevents the agent from taking irreversible actions without oversight.

**Evidence:** OpenAI "A Practical Guide to Building Agents" (tool safeguards section); Anthropic sandboxing architecture (filesystem + network isolation).

### P-TOOL-6: The Scaffold Matters as Much as the Model

**Statement:** Invest in agent scaffolding (harness, environment setup, tool descriptions, AGENTS.md) as seriously as model selection. The same model can vary dramatically in performance depending on its scaffold.

**Rationale:** MLE-bench showed that o1-preview with AIDE scaffolding achieved 16.9% Kaggle bronze medal rate, while the same model with other scaffolds performed far worse. Codex's harness-engineering experiment demonstrated that 3 engineers writing zero application code but investing heavily in environment design (AGENTS.md, custom linters, progressive disclosure docs) achieved 3.5 PRs per engineer per day with ~1M lines of AI-generated code. PaperBench found that Claude 3.5 Sonnet's replication score varied significantly with open-source scaffold choice. The scaffold includes: tool descriptions (P-TOOL-1), instruction files (AGENTS.md), validation mechanisms (linters), and feedback loops (test harnesses).

**Evidence:** OpenAI MLE-bench (AIDE vs. other scaffolds); OpenAI "Harness Engineering" (5-month Codex experiment); OpenAI PaperBench (scaffold-dependent performance); OpenAI "Introducing Codex" (AGENTS.md scope rules and citation system).

---

## III. Agent Architecture

*How you structure the relationship between agents determines reliability more than any individual agent's capability.*

### P-ARCH-1: Default to a Single Agent

**Statement:** Start with one agent with tools. Add agents only when you hit specific, measurable triggers: context overflow, complex branching logic, or tool overlap that defeats disambiguation.

**Rationale:** Every major source—Anthropic, Cognition, OpenAI, Google—converges on this. Cognition's title says it plainly: "Don't Build Multi-Agents." OpenAI recommends maximizing a single agent's capabilities first. Anthropic's building-effective-agents guide positions multi-agent as the last pattern to reach for. The overhead of coordinating multiple agents almost always exceeds the benefit unless the task genuinely requires it.

**Evidence:** Cognition "Don't Build Multi-Agents"; OpenAI guide ("maximize single agent first"); Anthropic "Building Effective Agents"; Google "Towards a Science of Scaling Agent Systems." Additionally, OpenAI's product evolution provides strong evidence: Operator and Deep Research were separate products, but users frequently sent queries to the wrong one. Merging them into ChatGPT Agent (single agent, multiple tools) resolved this—the model selects the optimal tool path, not the user. "Unify before multiplying."

### P-ARCH-2: When You Must Parallelize, Share State Through Artifacts

**Statement:** If tasks genuinely require parallel execution, coordinate through shared artifacts (files, git repos, databases) rather than message-passing between agents.

**Rationale:** Anthropic's C-compiler project ran 16 parallel Claude instances effectively because they shared a git repository—a durable, versioned artifact—rather than trying to pass context through agent-to-agent messages. File-based locking and specialized review roles (dedup, performance, code quality, docs) maintained coherence.

**Evidence:** Anthropic "Building a C Compiler" (~2000 sessions, $20K, 100K lines); Cursor worktree isolation pattern.

### P-ARCH-3: Manager Pattern for Centralized Control, Handoffs for Decentralized

**Statement:** Choose the manager pattern (agents-as-tools) when you need a single agent to maintain context and synthesize results. Choose the decentralized pattern (handoffs) when specialized agents should fully take over.

**Rationale:** OpenAI identifies these as the two fundamental multi-agent topologies. In the manager pattern, a central agent dispatches to specialist agents via tool calls and retains conversation context. In the decentralized pattern, agents hand off complete control to peers. The choice depends on whether you need central synthesis or full specialization transfer.

**Evidence:** OpenAI "A Practical Guide to Building Agents" (multi-agent systems section); LangChain multi-agent docs (router, handoffs, subagents, skills patterns).

### P-ARCH-4: Code-First Over Declarative Graphs

**Statement:** Express workflow logic in code rather than visual or declarative graph frameworks.

**Rationale:** OpenAI's guide explicitly argues that declarative graph frameworks become cumbersome as workflows grow dynamic, often requiring learning domain-specific languages. A code-first approach using familiar programming constructs is more flexible and adaptable. Cursor's evolution confirms this: they moved from static pipelines to dynamic planner→executor→worker hierarchies expressed in code.

**Evidence:** OpenAI guide (declarative vs. non-declarative graphs callout); Cursor "Towards Self-Driving Codebases."

### P-ARCH-5: Compress History for Long-Duration Agents

**Statement:** For agents that must run across many steps, build an explicit context compression layer—a dedicated model or process that distills conversation history into key details, events, and decisions.

**Rationale:** Simple linear agents work well but eventually overflow context windows. Cognition's solution is a dedicated compression model (potentially fine-tuned) whose sole job is summarizing action history into essential information. Manus uses filesystem-backed memory for the same purpose. This is hard to get right but enables much longer effective agent horizons.

**Evidence:** Cognition "Don't Build Multi-Agents" (compression architecture); Manus filesystem-as-context; Claude Code subagent pattern (limits subagents to questions to avoid context blowup).

---

## IV. Evaluation & Testing

*You cannot improve what you cannot measure. But naive measurement actively misleads.*

### P-EVAL-1: Evaluate the System, Not the Model

**Statement:** Always evaluate the complete agent system (model + tools + harness + prompts) as a unit. Isolated model benchmarks are misleading for agent performance.

**Rationale:** Anthropic's SWE-bench report shows that minimal scaffolding with good tool descriptions outperforms heavy frameworks. Google's scaling paper demonstrates that multi-agent systems sometimes degrade rather than improve performance. The system behavior emerges from the interaction of all components.

**Evidence:** Anthropic "Claude's SWE-bench Performance"; Google "Towards a Science of Scaling Agent Systems"; Cognition "Evaluating Coding Agents." OpenAI's benchmark evolution (MMLU → SWE-bench → MLE-bench → SWE-Lancer → GDPval) demonstrates the same trajectory: evaluations must assess the whole agent on real-world tasks, not just the model on academic questions. GDPval maps tasks to GDP-weighted occupations and real dollar value; SWE-Lancer tags each task with its Upwork payout.

### P-EVAL-2: Use Realistic, Multi-Turn Evaluation

**Statement:** Design evaluations that test the full agent loop—planning, tool use, error recovery, and multi-step reasoning—not just single-turn accuracy.

**Rationale:** Cognition's evaluation philosophy emphasizes that static benchmarks miss the behaviors that matter most in production: recovery from mistakes, adaptation to unexpected tool outputs, and coherence across many turns. Google's web agent research shows that composed sequential tasks cause dramatically different failure modes than individual steps.

**Evidence:** Cognition "Evaluating Coding Agents"; Google paper 46840 (web agent failure on composed tasks); Anthropic "Building Effective Agents" (evaluation section).

### P-EVAL-3: Infrastructure Is an Experimental Variable

**Statement:** Treat compute configuration (memory, CPU, network, disk) as a first-class variable in evaluation. A 6-percentage-point gap can come from resource configuration alone.

**Rationale:** Anthropic's infrastructure noise paper demonstrated that resource-starved runs produce systematically lower scores. Require ≥3x headroom on resources. Log hardware config alongside every eval run. Re-run experiments that land within the noise band.

**Evidence:** Anthropic "Quantifying Infrastructure Noise in Evaluations."

### P-EVAL-4: Prevent Contamination Religiously

**Statement:** Maintain strict separation between the data the agent trains/tunes on and the data used to evaluate it. Use held-out problems. Rotate eval sets.

**Rationale:** Anthropic's research-to-eval pipeline and Cognition's SWE-bench technical report both document how subtle contamination channels can inflate scores. Pre-registration of evaluation criteria and adversarial test design are necessities, not luxuries.

**Evidence:** Anthropic "Preventing Harms and Avoiding Misuse"; Cognition "SWE-bench Technical Report."

### P-EVAL-5: Model Difficulty ≠ Human Difficulty

**Statement:** Do not use human intuition about task difficulty to predict agent success rates. What models find hard differs fundamentally from what humans find time-consuming. Task assignment must be based on empirical agent performance data.

**Rationale:** GDPval evaluation across 44 occupations showed that agent pass rate correlates more strongly with the economic value of a task than with the estimated hours a human would need. Some tasks that take humans many hours are easy for models (e.g., large-scale data synthesis); some tasks that seem simple to humans are hard for models (e.g., tasks requiring physical-world common sense or nuanced judgment). Deep Research's expert-level task evaluation confirmed this: "the things that models find difficult are different to what humans find time-consuming."

**Evidence:** OpenAI GDPval (pass rate vs. economic value vs. estimated hours); OpenAI "Introducing Deep Research" (expert-level task evaluation charts).

### P-EVAL-6: Design for Asymmetry of Verification

**Statement:** When possible, structure agent tasks so that outputs are hard to produce but easy to verify. This asymmetry enables best-of-N strategies, self-evaluation, and automated quality gates.

**Rationale:** BrowseComp was deliberately designed with this property: questions where the answer is short, indisputable, and verifiable in minutes, but finding the answer may require browsing hundreds of websites. This design enabled best-of-N sampling (64 attempts, pick highest-confidence), which improved Deep Research's accuracy by 15-25% over single attempts. Best-of-N consistently outperformed majority voting because the model "knows when it's right." This principle applies beyond benchmarks: if you can design your agent's tasks so their outputs are automatically verifiable (e.g., code that must pass tests, calculations that must satisfy physical constraints), you unlock powerful scaling strategies.

**Evidence:** OpenAI BrowseComp (benchmark design philosophy, best-of-N vs. majority voting results); OpenAI "Introducing Deep Research" (aggregation strategies).

---

## V. Retrieval & Knowledge

*How agents access external knowledge determines the quality ceiling of their outputs.*

### P-RAG-1: Hybrid Retrieval Beats Any Single Method

**Statement:** Combine embedding-based semantic search with BM25 keyword search. Neither alone covers the full query distribution.

**Rationale:** Anthropic's Contextual Retrieval paper showed that combining contextual embeddings with contextual BM25 reduced retrieval failure rates by 67% compared to either method alone. Semantic search captures meaning but misses exact terms; keyword search captures exact terms but misses paraphrases.

**Evidence:** Anthropic "Introducing Contextual Retrieval."

### P-RAG-2: Prepend Chunk-Level Context Before Embedding

**Statement:** Before embedding a document chunk, prepend a short (50-100 token) contextual header that situates the chunk within the whole document.

**Rationale:** Anthropic's contextual retrieval technique uses a prompt like "Given the document, provide a short context for this chunk" to generate situating text. This gives the embedding model access to document-level meaning that would otherwise be lost after chunking. The improvement is dramatic: 49% reduction in retrieval failures for embeddings, 67% when combined with BM25.

**Evidence:** Anthropic "Introducing Contextual Retrieval" (contextual embeddings section).

### P-RAG-3: Rerank Before Presenting

**Statement:** After initial retrieval, apply a reranking step (model-based or cross-encoder) to filter the top results down to the most relevant subset.

**Rationale:** Initial retrieval casts a wide net; reranking sharpens precision. This two-stage pipeline—cheap recall followed by expensive precision—is more cost-effective than trying to be precise in the first stage.

**Evidence:** Anthropic "Introducing Contextual Retrieval" (reranking section); Anthropic "Building Effective Agents."

---

## VI. Safety & Guardrails

*The reliability of an agent is bounded by the strength of its guardrails, not the capability of its model.*

### P-SAFE-1: Layer Guardrails as Defense-in-Depth

**Statement:** No single guardrail is sufficient. Combine rules-based protections (regex, blocklists, input limits), LLM-based classifiers (relevance, safety, hallucination), and moderation APIs.

**Rationale:** OpenAI's guardrails architecture shows a multi-layer pipeline: rules-based protections catch known threats cheaply, LLM-based classifiers handle nuanced attacks, and moderation APIs provide broad coverage. Each layer catches what the others miss.

**Evidence:** OpenAI "A Practical Guide to Building Agents" (guardrails section); Anthropic sandboxing (filesystem + network isolation as defense-in-depth). OpenAI "Introducing ChatGPT Agent" adds a production five-layer stack: explicit user confirmation → watch mode → proactive risk refusal → privacy controls → secure browser takeover. The ChatGPT Agent System Card also documents preemptive High bio-safety classification—applying maximum safety tier even without definitive evidence of harm capability.

### P-SAFE-2: Sandbox by Default

**Statement:** Run agent code in an isolated environment with filesystem restrictions and network allowlists. Require both layers—filesystem isolation alone is insufficient.

**Rationale:** Anthropic's sandboxing paper demonstrates that bubblewrap (Linux) and seatbelt (macOS) for filesystem isolation, combined with a SOCKS proxy for network allowlisting, achieved 84% reduction in permission prompts while maintaining security. Neither layer alone is complete: filesystem access without network control allows exfiltration, and network control without filesystem access prevents basic operations.

**Evidence:** Anthropic "Making Claude Code More Secure with Sandboxing."

### P-SAFE-3: Escalate on Failure and High Stakes

**Statement:** Define explicit thresholds for human intervention: (a) when the agent exceeds N retries on the same action, and (b) when the action is irreversible, high-value, or touches sensitive data.

**Rationale:** OpenAI's guide identifies two primary triggers: exceeding failure thresholds and high-risk actions. Anthropic's human-in-the-loop patterns in building-effective-agents recommend graduated autonomy—start with human approval for everything, then selectively remove gates as confidence grows.

**Evidence:** OpenAI guide (human intervention section); Anthropic "Building Effective Agents" (human-in-the-loop patterns).

---

## VII. Production Operations

*What works in a notebook will fail in production. These principles govern the transition.*

### P-OPS-1: Treat Overlapping Infrastructure Failures as the Default

**Statement:** Assume production incidents will involve multiple simultaneous root causes. Design monitoring and debugging workflows that test for compounding failures, not single-fault models.

**Rationale:** Anthropic's postmortem of three August-September 2025 incidents revealed overlapping bugs: context window routing errors, TPU output corruption from XLA:TPU approximate top-k miscompilation, and mixed bf16/fp32 precision issues. Each masked the other. Single-fault debugging would have missed the interaction.

**Evidence:** Anthropic "A Postmortem of Three Recent Issues."

### P-OPS-2: Precision and Routing Are Separate Failure Modes

**Statement:** Distinguish between model capability failures (wrong answers) and infrastructure routing failures (wrong model version, wrong context size, wrong precision). The symptoms look identical but the fixes are completely different.

**Rationale:** Anthropic's context window routing bug meant users requesting large context windows were served by a model provisioned for smaller ones—producing degraded responses that looked like model capability issues but were actually infrastructure misconfigurations.

**Evidence:** Anthropic "A Postmortem of Three Recent Issues" (context window routing section).

### P-OPS-3: Start Small, Validate with Real Users, Grow Incrementally

**Statement:** Deploy agents on narrow, well-defined tasks first. Expand scope only after observing real-world performance and failure modes.

**Rationale:** OpenAI's conclusion emphasizes that successful deployment isn't all-or-nothing. Anthropic's building-effective-agents guide recommends starting with the simplest architecture that could work—augmented LLM, then workflows, then agents. Cursor's evolution took years: from autocomplete to background agents to parallel multi-agent systems. Each step was validated empirically.

**Evidence:** OpenAI guide (conclusion); Anthropic "Building Effective Agents"; Cursor "Towards Self-Driving Codebases" (3-year evolution).

### P-OPS-4: Observability Is Non-Negotiable

**Statement:** Every agent action, tool call, context state, and model response must be logged and traceable. Invest in observability before scaling.

**Rationale:** Cognition's Agent Trace maps code changes back to the context that produced them. LangChain's LangSmith provides trace-level observability. Without these, debugging production agents is impossible—you cannot reason about a system whose intermediate states you cannot observe.

**Evidence:** Cognition "Agent Trace"; LangChain LangSmith integration; Anthropic postmortem (diagnosis required deep infrastructure traces). OpenAI Codex reinforces this: every task produces citation-linked terminal logs and test outputs (format: `【F:path†Lstart-Lend】`), making each agent step traceable. The Agents SDK ships with tracing as a first-class feature. OpenAI also confirms that stateless architectures (Responses API replacing Assistants API; Codex sending full conversation each call) support better observability because every request is self-describing and reproducible.

---

## VIII. Human Integration

*Agents don't operate in a vacuum. The interface between agent output and human judgment is where reliability is ultimately determined.*

### P-HCI-1: Review Is the Bottleneck, Not Generation

**Statement:** In production agent systems, the constraint shifts from generation speed to human review throughput. Design agent output to be reviewable, not just correct.

**Rationale:** Cognition's Devin Review explicitly redesigned their product around this insight: the bottleneck isn't how fast the agent writes code—it's how fast humans can verify it. This led to structured review interfaces, confidence estimates, and change summaries designed for rapid human assessment. As agent throughput scales, review quality degrades unless explicitly addressed.

**Evidence:** Cognition "Devin Review"; Cognition "Closing the Agent Loop" (reviewer + writer agents in autonomous repair loop); Cursor code review workflow (diff view, Review → Find Issues, Bugbot for PRs).

### P-HCI-2: Specify Clearly or Scale Broken

**Statement:** Vague instructions don't just produce vague outputs—they multiply errors at scale. Treat instruction quality as a first-class engineering concern.

**Rationale:** Cursor's multi-agent research documents that underspecified instructions amplify nonlinearly when distributed across many agents. A slightly ambiguous directive to one agent is manageable; the same directive to 10 parallel agents produces 10 different interpretations that conflict on merge.

**Evidence:** Cursor "Towards Self-Driving Codebases"; Cursor "Best Practices" ("Write specific prompts" as top trait of effective developers).

### P-HCI-3: Accept Stability Over Perfection

**Statement:** Design agent systems to be anti-fragile—tolerating small, stable error rates and allowing other parts of the system to recover—rather than demanding zero errors.

**Rationale:** Cursor explicitly states their multi-agent system is designed to be "anti-fragile," accepting that individual agents will sometimes fail. A system that tolerates a 2% error rate and runs 1000 commits/hour produces more value than one demanding perfection at 10 commits/hour. Graceful degradation at the system level matters more than perfection at the component level.

**Evidence:** Cursor "Towards Self-Driving Codebases" (anti-fragile design); OpenAI guide (human intervention as recovery mechanism).

### P-HCI-4: Minimize User Prompt Burden

**Statement:** Design the system so users specify less, not more. Boot files supply context defaults, skills encode procedures, and the agent assembles execution context from minimal input. If the user must write a detailed prompt for the system to work, the context and skill layers are under-designed.

**Rationale:** Manus's core insight—"the future of agents will be built one context at a time"—implies that context assembly is the system's responsibility, not the user's. When a user has to write a long, structured prompt to get correct behavior, the system is offloading its own job back to the human. The correct architecture is: (1) boot files supply persistent context defaults (project state, definitions, current defaults), (2) skills encode reusable procedures (step-by-step workflows), (3) the agent infers execution context from a short user signal by loading the right boot files and skills. This inverts the usual "prompt engineering" advice: instead of teaching users to write better prompts, design the system so short prompts work. Analogous to good API design—sensible defaults mean callers specify only what's non-default.

**Evidence:** Manus "Context Engineering for AI Agents" (filesystem-as-memory, agent-managed context); Cognition COGNITION_SESSION_PROMPT.md (startup protocol that loads state files so user doesn't re-explain); Anthropic "Building Effective Agents" (tool descriptions carry the specification burden, not user prompts); Fieldwork on DCID climate innovation mapping project (user's natural-language instructions were sufficient when boot file + data schema existed, but required extensive elaboration without them).

### P-HCI-5: Interpret-Then-Confirm, Not Rewrite-Then-Execute

**Statement:** When receiving an underspecified user instruction, the agent outputs a short execution plan (what it understood, what it will do, what it will produce) and waits for confirmation. This is cheaper for the user to verify than reviewing a rewritten prompt or auditing a completed output.

**Rationale:** There are three possible responses to an underspecified instruction: (a) ask clarifying questions (slow, shifts cognitive burden to user), (b) rewrite the prompt into a detailed version and show it to the user (the user now has to parse AI-generated text to verify alignment—often harder than writing the prompt themselves), (c) interpret and show a concrete execution plan (the user verifies intent against planned actions, which is fast and unambiguous). Option (c) is optimal because it leverages P-EVAL-6 (verification asymmetry): it is easier for a human to verify "I will extract 40 startups from NEN 2024 and fill them into the Data Template" than to verify a rewritten prompt or audit 40 rows of output. The execution plan also serves as a contract—if the user approves, subsequent output can be trusted to match the plan. This principle complements P-HCI-1 (review is the bottleneck) by front-loading the review to the cheapest possible moment.

**Evidence:** Cognition "Closing the Agent Loop" (reviewer agent checks plan before execution); Cursor "Best Practices" (structured diffs for human review); Anthropic "Building Effective Agents" (human-in-the-loop at decision points, not at output review); Fieldwork observation that users can approve/reject a 5-line execution plan in seconds, but reviewing a rewritten paragraph-length prompt takes minutes and still leaves ambiguity.

---

## IX. Meta-Principles

*Principles about how to apply principles.*

### P-META-1: Constraints Beat Instructions

**Statement:** When you want the agent to avoid a behavior, use a structural constraint (tool masking, sandbox restriction, schema enforcement) rather than a natural-language instruction.

**Rationale:** Cursor's research found that constraints expressed as structural limits outperform instructions expressed as natural-language rules. The model can ignore instructions; it cannot bypass a masked logit, a removed file permission, or a Pydantic schema validator.

**Evidence:** Cursor "Towards Self-Driving Codebases"; Manus logit masking; Anthropic sandboxing.

### P-META-2: Empirical Over Theoretical

**Statement:** Test every architectural decision empirically. Do not trust intuition about what will help agent performance.

**Rationale:** Cursor explicitly names "empirical over assumption-driven" as a core operating principle. Manus rebuilt their framework four times. Anthropic's research-to-eval pipeline exists to catch the gap between expected and actual performance. Agent behavior is emergent and unpredictable; the only reliable signal is measurement.

**Evidence:** Cursor "Towards Self-Driving Codebases"; Manus "Context Engineering" ("stochastic grad student descent"); Anthropic eval infrastructure.

### P-META-3: Design for the Model You'll Have Tomorrow

**Statement:** Keep your agent architecture orthogonal to the underlying model. If model progress is a rising tide, your system should be the boat, not a pole fixed to the seabed.

**Rationale:** Manus chose context engineering over fine-tuning specifically because it lets them ship improvements in hours rather than weeks and benefit automatically from better foundation models. Anthropic's SWE-bench agent demonstrated that minimal scaffolding ages better than heavy frameworks because it relies on model capability rather than working around limitations.

**Evidence:** Manus "Context Engineering" (introduction); Anthropic "Claude's SWE-bench Performance."

### P-META-4: Add Structured Variation to Prevent Rigidity

**Statement:** When the agent processes many similar items sequentially, introduce small structural variations in serialization format, wording, or order to prevent pattern lock-in.

**Rationale:** Manus discovered that when reviewing 20 resumes, the agent falls into a repetitive rhythm—mimicking the pattern it sees rather than reasoning about each item. Injecting variation (alternative phrasings, reordered fields, different templates) breaks the pattern and restores independent reasoning.

**Evidence:** Manus "Context Engineering" (few-shot trap section).

### P-META-5: Test-Time Compute Is a Tunable Variable

**Statement:** Treat inference-time reasoning budget (number of steps, thinking tokens, tool calls allowed) as an independent, adjustable parameter. For high-value tasks, allocate more reasoning time; for routine tasks, constrain it.

**Rationale:** This is perhaps the most pervasively supported finding from OpenAI's literature. It appears across nearly every article: CUA's performance improves with more allowed steps on OSWorld. Deep Research's pass rate scales smoothly with max tool calls. BrowseComp accuracy scales with test-time compute budget. FrontierScience accuracy improves with longer thinking time. An internal GPT-5.2 spent 12 hours of continuous reasoning to derive and prove a gluon amplitude formula. o1/o3 papers show that RL training compute and inference compute are independent scaling axes—"more compute = better performance" applies to both. The practical implication is that system designers should budget inference compute like they budget money: more for high-stakes decisions, less for routine ones.

**Evidence:** OpenAI CUA (test-time scaling on OSWorld); OpenAI "Introducing Deep Research" (Pass Rate vs. Max Tool Calls); OpenAI BrowseComp (test-time compute scaling plot); OpenAI FrontierScience ("longer thinking time leads to improved accuracy"); OpenAI "GPT-5.2 Derives a New Result in Theoretical Physics" (12-hour reasoning); OpenAI "Introducing o3 and o4-mini" (dual scaling laws: train-time + test-time).

### P-META-6: Platform Absorbs Infrastructure, Focus on Domain

**Statement:** As AI platforms mature, previously custom-built infrastructure (RAG pipelines, search integration, browser automation, observability) gets absorbed into platform-level tools. Invest your engineering time in domain-specific environment design—tool descriptions, constraints, feedback loops, and safety policies—not in infrastructure that platforms will commoditize.

**Rationale:** OpenAI's Responses API now includes built-in web search, file search (with vector store, chunking, and reranking), and computer use—capabilities that previously required custom implementation. The Assistants API (stateful, platform-managed) is being deprecated in favor of the Responses API (stateless, developer-managed), signaling that platforms will handle tool infrastructure but give developers more control over state and logic. Meanwhile, Codex's harness-engineering experiment showed that the highest-value engineering work was domain-specific: writing AGENTS.md files, designing custom linters with agent-readable error messages, and building progressive disclosure documentation structures.

**Evidence:** OpenAI "New Tools for Building Agents" (Responses API built-in tools, Assistants API deprecation); OpenAI "Harness Engineering" (domain-specific environment design as core engineering work); OpenAI "Introducing Codex" (AGENTS.md as agent-facing documentation).

---

## Appendix A: Principle Quick-Reference

| Domain | ID | One-Liner |
|---|---|---|
| Context | P-CTX-1 | Context engineering is the job |
| Context | P-CTX-2 | Share full traces, not summaries |
| Context | P-CTX-3 | Actions carry implicit decisions |
| Context | P-CTX-4 | Design around the KV-cache |
| Context | P-CTX-5 | Mask, don't remove |
| Context | P-CTX-6 | Filesystem as extended context |
| Context | P-CTX-7 | Recite to remember |
| Context | P-CTX-8 | Preserve errors in context |
| Context | P-CTX-9 | Warm-up problems prime complex tasks |
| Tools | P-TOOL-1 | Invest in descriptions, not code |
| Tools | P-TOOL-2 | Error-proof tool interfaces |
| Tools | P-TOOL-3 | Defer tool loading for large sets |
| Tools | P-TOOL-4 | Programmatic orchestration for deterministic flows |
| Tools | P-TOOL-5 | Assign risk levels to every tool |
| Tools | P-TOOL-6 | Scaffold matters as much as model |
| Architecture | P-ARCH-1 | Default to a single agent |
| Architecture | P-ARCH-2 | Parallelize through shared artifacts |
| Architecture | P-ARCH-3 | Manager for control, handoffs for specialization |
| Architecture | P-ARCH-4 | Code-first over declarative graphs |
| Architecture | P-ARCH-5 | Compress history for long durations |
| Evaluation | P-EVAL-1 | Evaluate the system, not the model |
| Evaluation | P-EVAL-2 | Realistic multi-turn evaluation |
| Evaluation | P-EVAL-3 | Infrastructure is an experimental variable |
| Evaluation | P-EVAL-4 | Prevent contamination religiously |
| Evaluation | P-EVAL-5 | Model difficulty ≠ human difficulty |
| Evaluation | P-EVAL-6 | Design for asymmetry of verification |
| Retrieval | P-RAG-1 | Hybrid retrieval beats any single method |
| Retrieval | P-RAG-2 | Prepend chunk-level context |
| Retrieval | P-RAG-3 | Rerank before presenting |
| Safety | P-SAFE-1 | Layer guardrails as defense-in-depth |
| Safety | P-SAFE-2 | Sandbox by default |
| Safety | P-SAFE-3 | Escalate on failure and high stakes |
| Operations | P-OPS-1 | Overlapping failures are the default |
| Operations | P-OPS-2 | Precision ≠ routing failures |
| Operations | P-OPS-3 | Start small, grow incrementally |
| Operations | P-OPS-4 | Observability is non-negotiable |
| Human | P-HCI-1 | Review is the bottleneck, not generation |
| Human | P-HCI-2 | Specify clearly or scale broken |
| Human | P-HCI-3 | Accept stability over perfection |
| Human | P-HCI-4 | Minimize user prompt burden |
| Human | P-HCI-5 | Interpret-then-confirm, not rewrite-then-execute |
| Meta | P-META-1 | Constraints beat instructions |
| Meta | P-META-2 | Empirical over theoretical |
| Meta | P-META-3 | Design for tomorrow's model |
| Meta | P-META-4 | Structured variation prevents rigidity |
| Meta | P-META-5 | Test-time compute is a tunable variable |
| Meta | P-META-6 | Platform absorbs infrastructure; focus on domain |

---

## Appendix B: Source Bibliography

### Anthropic
- "Building Effective Agents" — Agent design patterns and orchestration
- "Prompt Caching with Claude" — KV-cache mechanics and optimization
- "Introducing Contextual Retrieval" — Hybrid RAG with contextual embeddings
- "Claude's SWE-bench Performance" — Minimal scaffolding philosophy
- "Building a C Compiler with Parallel Claudes" — Multi-agent coordination via shared artifacts
- "Making Claude Code More Secure with Sandboxing" — Dual-layer isolation
- "Introducing Advanced Tool Use" — Tool Search Tool, Programmatic Tool Calling, Tool Use Examples
- "Claude Desktop Extensions" — .mcpb packaging for MCP servers
- "A Postmortem of Three Recent Issues" — Overlapping infrastructure failures
- "Quantifying Infrastructure Noise in Evaluations" — Resource config as eval variable
- "Preventing Harms and Avoiding Misuse" — Evaluation integrity
- "Research to Product Pipeline" — Structured eval design

### Cognition (Devin)
- "Don't Build Multi-Agents" (Walden Yan) — Context engineering principles
- "Evaluating Coding Agents" — Realistic eval design
- "Agent Trace" — Observability and provenance
- "SWE-bench Technical Report" — Benchmark evaluation constraints

### Cursor
- "Towards Self-Driving Codebases" — Multi-agent evolution, anti-fragile design
- "Best Practices for Coding with Agents" — Harness components, plan mode, TDD

### Google DeepMind
- "Towards a Science of Scaling Agent Systems" — When multi-agent helps vs. hurts
- Paper 46840 — Web agent failure on composed sequential tasks

### LangChain
- Context Engineering docs — Context as #1 engineering priority
- Agent architecture docs — Middleware, dynamic tools, structured output
- Philosophy — Evolution from chains to graph-based agents

### Manus
- "Context Engineering for AI Agents" (Yichao Ji) — KV-cache, masking, filesystem memory, recitation, error preservation, variation

### OpenAI

#### Engineering & Product
- "A Practical Guide to Building Agents" (32pp PDF) — Tool design, orchestration patterns, seven-layer guardrails, optimistic execution, tripwire pattern, graduated autonomy
- "Unrolling the Codex Agent Loop" — Prompt construction order, KV-cache mechanics, compaction, stateless-by-design for ZDR compliance
- "Unlocking the Codex Harness" — App Server architecture, JSON-RPC protocol, Item/Turn/Thread primitives, bidirectional approval flow
- "Harness Engineering" — 5-month experiment (0 human code, ~1M AI-generated lines), progressive disclosure, agent legibility, constraints via linters, entropy/garbage collection
- "Introducing ChatGPT Agent" — Unified agent (CUA + Deep Research + ChatGPT), virtual computer as cross-tool context layer, five-layer safety, preemptive bio-safety classification
- "Computer-Using Agent (CUA)" — GUI as universal interface, perception-reasoning-action loop, test-time scaling, three-class safety risk taxonomy
- "New Tools for Building Agents" — Responses API, Agents SDK, built-in tools (web search, file search, computer use), platform absorbs infrastructure
- "Introducing Codex" — Cloud sandbox (fully offline execution), AGENTS.md scope rules, citation system, async multi-agent vision
- "Introducing Deep Research" — End-to-end RL training, test-time scaling (Pass Rate vs Max Tool Calls), model difficulty ≠ human difficulty
- "ChatGPT Agent System Card" — High bio-safety classification, four-component architecture

#### Research & Benchmarks
- "MLE-bench" — 75 Kaggle ML tasks, scaffold dramatically affects performance
- "PaperBench" — 20 ICML paper replications, 8,316 gradable sub-tasks, hierarchical rubric decomposition
- "SWE-Lancer" — 1,400+ Upwork tasks worth $1M, economic value mapping
- "BrowseComp" — 1,266 hard-to-find info tasks, asymmetry of verification, best-of-N > majority voting
- "GDPval" — 44 occupations, 1,320 tasks, frontier models approaching expert quality, 100x faster/cheaper
- "Introducing o3 and o4-mini" — Dual scaling laws (train-time + test-time), tool use learned through RL
- "Learning to Reason with LLMs" (o1) — Chain-of-thought as safety monitoring tool, reward hacking observations

#### Science
- "Early Experiments in Accelerating Science with GPT-5" — Warm-up problem pattern, attribution failure warning, GPT-5 as research partner
- "FrontierScience" — Olympiad (77%) vs Research (25%) benchmark split, rubric-based open-ended grading
- "GPT-5.2 Derives a New Result in Theoretical Physics" — 12-hour continuous reasoning, extreme test-time scaling
- "GPT-5 Lowers the Cost of Cell-Free Protein Synthesis" — Lab-in-the-loop, programmatic validation of AI-designed experiments
- "Our First Proof Submissions" — 5/10 research-level math proofs likely correct

---

*v0.2.0 — Updated with 2 new principles (P-HCI-4, P-HCI-5) from DCID climate innovation mapping fieldwork. Total: 47 principles across 9 domains. Backup of v0.1.1 saved as PRINCIPLES_v0.1_backup.md.*
