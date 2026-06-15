---
name: langchain4j-agentic-architect
description: >-
  Analyze the architecture of a LangChain4j (Java) agentic backend and decide
  which agentic flows should be migrated to activation-gated skills — the
  dev.langchain4j:langchain4j-skills module, an open agentskills.io SKILL.md
  implementation — to fight system-prompt and tool-surface bloat. Runs an
  interrogation to pin the real goal, maps the agentic flows, scores each against
  a migration scorecard and a lean architecture rubric, then reports grounded
  findings with before/after diagrams. Use when the user wants to create or
  update an agentic flow, audit an agentic backend's architecture, decide
  static-vs-skill gating, shrink a bloated system prompt, package a capability as
  a langchain4j skill, or scale an agent past a static tool set. Triggers include
  "migrate this to a skill", "should this be a skill", "my system prompt is too
  big", "agentic architecture review", "progressive disclosure for tools".
compatibility: >-
  Targets Java backends using LangChain4j (dev.langchain4j) with AiServices-style
  agents. The migration target is the dev.langchain4j:langchain4j-skills module;
  perishable identifiers in references/API-REFERENCE.md are grounded against
  langchain4j-skills 1.16.2-beta26 (core 1.16.2) and must be re-verified for the
  project's version (skills X.Y.Z-betaN is lockstep with core X.Y.Z). Needs read
  access to source and build files; ripgrep recommended for the flow scan.
metadata:
  version: "1.0"
  grounded-against: "langchain4j-skills 1.16.2-beta26 (core 1.16.2)"
  domain: "agentic-backend-architecture"
---

# LangChain4j Agentic Architect

Review the **architecture of a LangChain4j (Java) agentic backend** and turn the
analysis into one decision: **which agentic flows should be migrated to
activation-gated skills** so the agent stops paying for every capability on every
turn. The output is a grounded report of per-flow findings plus, on request, the
implemented migration.

Respond in the user's language. This skill is harness-, language-, and
provider-agnostic and portable across projects — assume no specific agent
harness, cloud provider, DI framework, or company convention unless the
project's own files prove it.

## Scope — and the line with tool-architect

This skill works at **flow and architecture altitude**: the agentic loop, the
system prompt, the *gating* of the tool surface, and the packaging of a
capability as a **skill**. It does **not** re-audit individual tool *contracts*
(granularity, parameter schema, return shape, per-tool security). When a finding
is really about one tool's contract, name it and **defer to the
`langchain4j-tool-architect` skill** rather than duplicating that analysis here.

Migration is the headline; the architecture rubric exists only to feed the
create / update / migrate decision.

## Vocabulary

Use these terms exactly. Full definitions in [references/GLOSSARY.md](references/GLOSSARY.md).

- **Agentic flow** — one end-to-end capability: the instructions + tools +
  knowledge to handle one kind of request (e.g. "simulate a financing").
- **Gating strategy** — how the visible tool surface is chosen: **static** (every
  tool every turn), **retrieval** (vector tool-search), or **activation**
  (skills). Three strategies over one `ToolProvider` substrate.
- **Skill** — a directory with a `SKILL.md` (name + description always visible;
  body + resources loaded on activation), packaged via
  `dev.langchain4j:langchain4j-skills`. The open agentskills.io format — **not** a
  vendor's managed-skills product.
- **Progressive disclosure** — show the skill catalog; load a skill's body and
  resources only when the model activates it.
- **Activation trigger** — the natural-language condition, declared in a skill's
  `description`, under which the model should activate it.

## The migration scorecard (the spine)

Score every candidate flow on signals **for** and counter-signals **against**
migrating it to a skill. Full rubric, with grounding, in
[references/SKILL-MIGRATION.md](references/SKILL-MIGRATION.md).

**Signals for migrating:** conditional relevance (the flow matters in a narrow
slice of conversations — the strongest signal); heavy procedural weight in the
system prompt; a cohesive cluster of instructions + tools + knowledge; reference
knowledge that could load on demand; a deterministic activation trigger.

**Counter-signals (keep static):** the capability is needed on (almost) every
turn; the latency budget can't absorb the extra activation round-trip; it is a
lone tool with no instructions or resources; no clean activation trigger exists;
the backend is small enough that there is no bloat to fight.

> **Non-negotiable caveat.** Activation-gating is a **context-management**
> mechanism, **not** an authorization boundary. Hiding a money-moving flow behind
> activation does not make it safer — authorization stays in code, enforced from
> server-side identity, whether or not the skill is active. Never migrate "for
> security."

## The architecture rubric (lean — the method)

Four whole-flow checks that feed the decision. Details in
[references/ARCHITECTURE-RUBRIC.md](references/ARCHITECTURE-RUBRIC.md).

1. **Loop-bounded** — is the agentic loop capped and terminating?
2. **System-prompt budget** — how much of the prompt is conditional procedure that
   could be activation-gated vs. always-relevant policy?
3. **Gating strategy** — is static / retrieval / activation the right fit for the
   tool count and the conditionality of the flows?
4. **Identity seam** — is caller identity / authorization derived server-side and
   enforced in code, independent of which flow or skill is active?

## Process

### Step 0 — Ground the environment (always first)

Read the build files (`pom.xml`, `build.gradle[.kts]`) and detect the
**LangChain4j version**, the **model provider**, the **DI / web framework**, and
whether agents are wired via `AiServices`.
[references/API-REFERENCE.md](references/API-REFERENCE.md) is ground truth for
**skills `1.16.2-beta26` / core `1.16.2` only**; a version the user may have named
(`1.15.1-beta25`) maps to core `1.15.1`. Skills are **lockstep** with core
(`X.Y.Z-betaN` ↔ core `X.Y.Z`). On any other version, treat every identifier as a
hypothesis and re-verify it against that version's source before emitting code.

### Step 1 — Frame the engagement (interrogation)

Pin the **mode** with one question (audit a backend for migration opportunities /
migrate one flow / design a new flow and choose its gating / update an existing
skill). Then walk the mode's decision tree from
[references/INTERROGATION.md](references/INTERROGATION.md), **one question at a
time, each with your recommended answer.** Golden rule: **if the codebase can
answer it, explore instead of asking.** Stop when no remaining branch changes the
recommendation. Leave no loose ends.

### Step 2 — Map the agentic flows

Identify each flow: its slice of the system prompt, the tools it needs, the
reference knowledge it leans on, where caller identity comes from, and how the
surface is gated today. Use a search subagent if your harness offers one;
otherwise read the source directly. In single-flow mode, scope to that flow.

### Step 3 — Score and analyze

Run the four rubric checks over the architecture, then score each candidate flow
on the migration scorecard. For each finding, name the check or the deciding
signal, and cite the durable rule. Separate **durable** structure findings from
**perishable** version-specific ones.

### Step 4 — Report

Write a portable **Markdown** report following
[references/REPORT-FORMAT.md](references/REPORT-FORMAT.md): one card per flow
(verdict: migrate / keep static / split / defer-to-tool-architect; the scorecard;
a before/after Mermaid diagram), ending with a **Top recommendation.** Save it to
a file and tell the user the path. Do not render HTML; do not assume a browser. In
audit mode, do **not** finalize migrations yet — ask which to pursue.

### Step 5 — Grill & implement

Once the user picks a flow, drop into a focused grilling conversation about that
migration — the activation trigger, what moves from the prompt into the skill
body, what becomes a loaded resource, the tools that get scoped to the skill, the
unchanged authorization seam. Then implement it with the migration playbook in
[references/SKILL-MIGRATION.md](references/SKILL-MIGRATION.md), grounding every API
identifier against the re-verified
[references/API-REFERENCE.md](references/API-REFERENCE.md). Re-run the rubric on
the result and confirm the static prompt actually shrank.

## References

- [references/GLOSSARY.md](references/GLOSSARY.md) — the exact vocabulary.
- [references/INTERROGATION.md](references/INTERROGATION.md) — the mode-aware
  decision-tree question bank.
- [references/ARCHITECTURE-RUBRIC.md](references/ARCHITECTURE-RUBRIC.md) — the four
  durable architecture checks, with fixes and sources.
- [references/SKILL-MIGRATION.md](references/SKILL-MIGRATION.md) — the migration
  scorecard and the step-by-step migration playbook.
- [references/API-REFERENCE.md](references/API-REFERENCE.md) — perishable
  `langchain4j-skills` API surface and the one-substrate gating model.
- [references/REPORT-FORMAT.md](references/REPORT-FORMAT.md) — the portable
  Markdown + Mermaid report scaffold.
