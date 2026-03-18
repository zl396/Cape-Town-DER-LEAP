# WRITING_AGENT_PIPELINE.md

> Cognition-inspired multi-agent writing workflow for long-form research and white paper writing.
> Designed for high-citation, high-structure, mixed-audience documents.

## Purpose

This pipeline separates:

- structural thinking
- prose generation
- evaluation
- claim verification
- final humanization

It is designed for writing tasks where:

- section logic matters
- citations must be accurate
- claims must be verifiable
- local project files contain important evidence
- some facts may require up-to-date web confirmation

## Governing Principles

This workflow is aligned with:

- `R-2`: Pre-declare intent before non-trivial actions
- `P-CTX-1`: Context engineering is the job
- `P-CTX-6`: Filesystem as persistent memory
- `P-ARCH-1`: Default to single agent; add agents only at measurable triggers
- `P-ARCH-2`: Parallelize through shared artifacts, not messages
- `P-EVAL-1`: Evaluate the whole system
- `P-EVAL-6`: Design for verification asymmetry
- `P-HCI-1`: Review throughput is the bottleneck
- `P-HCI-4`: Minimize user prompt burden
- `P-HCI-5`: Interpret-then-confirm
- `P-META-1`: Structural constraints beat natural-language instructions

## Precedence Rule

If this file conflicts with:

- `CLAUDE.md`
- `PRINCIPLES_INDEX.md`
- `PRINCIPLES_v0.1.md`

those files override this workflow document. This pipeline is a derived operating layer, not a higher-order authority.

## Stage-To-Principle Crosswalk

### `spec builder`

- `R-2`: Pre-declare intent before non-trivial actions
- `P-CTX-1`: Context engineering is the job
- `P-HCI-5`: Interpret-then-confirm
- `P-HCI-4`: Minimize user prompt burden

### `writer`

- `P-CTX-1`: Context engineering is the job
- `P-CTX-7`: Recite plan into recent context
- `P-HCI-1`: Review throughput is the bottleneck
- `P-META-1`: Structural constraints beat natural-language instructions

### `evaluator`

- `P-EVAL-1`: Evaluate the whole system
- `P-EVAL-6`: Design for verification asymmetry
- `P-HCI-1`: Review throughput is the bottleneck
- `P-HCI-5`: Interpret-then-confirm

### `local claim check`

- `P-CTX-6`: Filesystem as persistent memory
- `P-EVAL-6`: Design for verification asymmetry
- `P-ARCH-2`: Parallelize through shared artifacts

### `web confirmation`

- `P-EVAL-6`: Design for verification asymmetry
- `P-SAFE-3`: Escalate on retries or high-stakes actions
- `P-ARCH-2`: Parallelize through shared artifacts

### `merge findings`

- `P-EVAL-1`: Evaluate the whole system
- `P-META-1`: Structural constraints beat natural-language instructions
- `P-HCI-1`: Review throughput is the bottleneck

### `writer revision`

- `R-2`: Pre-declare intent before non-trivial actions
- `P-EVAL-6`: Design for verification asymmetry
- `P-CTX-8`: Preserve errors in context

### `final human polish`

- `P-HCI-1`: Review throughput is the bottleneck
- `P-HCI-4`: Minimize user prompt burden
- `P-META-4`: Inject variation to prevent repetitive pattern lock-in

## Pipeline Overview

1. `spec builder`
2. `writer`
3. `evaluator`
4. `parallel checks`
   - `local claim check`
   - `web confirmation`
5. `merge findings`
6. `writer revision`
7. `final human polish`

## Stage 1: Spec Builder

### Role

Define what the section is supposed to do before anyone writes prose.

### Inputs

- chapter and section title
- report objective
- target audience
- relevant writing principles
- prior and next section context
- known source base

### Output

A short writing spec that defines:

- section function
- what the section must do
- what it must not do
- key claims
- evidence needed
- transition target
- citation expectations

### Rules

- Do not write full prose.
- Do not over-specify style at the expense of logic.
- Make the section's job explicit.

## Stage 2: Writer

### Role

Write the section body from the spec.

### Inputs

- section spec
- local source set
- writing constraints
- audience profile

### Output

A draft section with:

- paragraph-level logic
- in-text citations
- provisional references
- clearly expressed claims

### Rules

- Follow the section spec, not generic template writing.
- Write for the target audience, not for specialists alone.
- Keep prose concise and direct.
- Avoid empty summary sentences.
- Do not invent citations.
- Do not perform hidden fact substitution.

## Stage 3: Evaluator

### Role

Evaluate the draft against a fixed rubric before any claim checking begins.

### Inputs

- section spec
- current draft
- neighboring sections if needed for transition quality

### Output

A structured evaluation covering:

- logic and structure
- paragraph function
- transition quality
- overclaim or underclaim
- repetition
- audience fit
- citation sufficiency
- AI-sounding or template-heavy phrasing

The evaluator should also produce a `claim map` with each major claim tagged as:

- `local-only`
- `web-needed`
- `dual-check`

### Rules

- Evaluate, do not rewrite the whole section.
- Flag the weakest paragraph and weakest transition explicitly.
- Treat verification as separate from style critique.

## Stage 4: Parallel Checks

Two checking roles run in parallel against the evaluator's claim map.

### 4A. Local Claim Check

#### Role

Verify whether claims are supported by the project's local files.

#### Inputs

- current draft
- claim map
- local folder or source corpus

#### Output

For each claim:

- `supported locally`
- `partially supported locally`
- `not supported locally`
- source file path
- relevant page, section, or table if available

#### Rules

- Check claims, not just sources in the abstract.
- Prefer primary local sources over summaries.
- Do not rewrite prose.
- Flag claim-source mismatch separately from missing citation.

### 4B. Web Confirmation

#### Role

Confirm claims that may be time-sensitive, unstable, missing locally, or high-risk.

#### Inputs

- current draft
- claim map
- list of `web-needed` and `dual-check` claims

#### Typical Use Cases

- current policy changes
- legal or regulatory updates
- ITC status
- recent tariff reforms
- latest deployment figures
- market or adoption statistics that may have changed

#### Output

For each checked claim:

- `confirmed on web`
- `partially confirmed on web`
- `not confirmed on web`
- source link
- source date
- recommended claim strength

#### Rules

- Only check unstable or high-stakes claims.
- Use primary or official sources whenever possible.
- Record dates explicitly.
- Do not broaden the claim beyond what the source supports.

## Stage 5: Merge Findings

### Role

Combine evaluator feedback, local checking, and web confirmation into one revision brief.

### Output

A revision brief with:

- prose issues
- unsupported claims
- overstated claims
- claims requiring downgrade
- claims requiring stronger citation
- issues requiring human decision

### Merge Rules

- If a claim is supported locally and not time-sensitive, local support is sufficient.
- If a claim is time-sensitive, web confirmation takes priority on recency.
- If local and web evidence conflict, lower the claim strength or rewrite.
- If neither checker can support a claim, remove or soften it.

## Stage 6: Writer Revision

### Role

Revise the draft using the merged findings.

### Rules

- Fix unsupported or overstated claims before polishing style.
- Preserve the section's original function.
- Do not add new claims without evidence.
- Do not silently ignore checker findings.

## Stage 7: Final Human Polish

### Role

Perform a final anti-AI and readability pass after the draft is already logically sound and fact-checked.

### Focus Areas

- AI-sounding topic sentences
- overly balanced or generic phrasing
- repetitive sentence rhythm
- awkward transitions
- over-signposted roadmap language
- filler summaries

### Rules

- This is a polishing pass, not a restructuring pass.
- Human review has final authority over tone and naturalness.

## Recommended Operating Rules

- Use the full pipeline for introductions, synthesis chapters, policy arguments, and high-stakes sections.
- Use a lighter version for low-stakes background paragraphs.
- Keep shared artifacts in files, not in informal summaries.
- Run local and web checks in parallel only after the evaluator has produced a claim map.
- Do not let checkers rewrite the section.
- Do not skip the merge stage.

## Minimal Workflow Template

Use this when running the pipeline on a single section:

1. Build a section spec.
2. Draft the section.
3. Evaluate the draft and tag claims.
4. Run:
   - local claim check
   - web confirmation
5. Merge findings.
6. Revise the section.
7. Humanize the prose.

## Why This Pipeline Works

- The writer optimizes for prose.
- The evaluator optimizes for argument quality.
- The local checker optimizes for project-grounded evidence.
- The web checker optimizes for temporal accuracy.
- The merge stage prevents fragmented feedback.
- The final human pass restores naturalness.

This division of labor reduces a common failure mode in long-form model writing: prose that is structurally fluent but weakly grounded, or well-sourced writing that still sounds generic and machine-made.
