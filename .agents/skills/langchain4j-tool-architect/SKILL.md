---
name: langchain4j-tool-architect
description: >-
  Design, review, harden, and scale the tools an LLM agent can call in a
  LangChain4j (Java) agentic backend — the @Tool methods, ToolProvider /
  ToolSpecification definitions, and how they are wired into AiServices. Runs an
  interrogation to pin the real goal, maps the tool surface, then reports
  grounded findings against a portable best-practice rubric (granularity,
  description quality, identity injection, read-vs-write safety, return shaping,
  error-as-data, tool retrieval at scale) and the OWASP LLM Top 10. Use when the
  user wants to create or update a LangChain4j tool, audit a backend's tool
  definitions, fix an agent that picks the wrong tool, cut tool token cost,
  secure tool execution, or scale past ~30 tools. Triggers include "review my
  tools", "design a langchain4j tool", "@Tool best practices", "tool
  architecture", "my agent calls the wrong tool".
compatibility: >-
  Targets Java backends using LangChain4j (dev.langchain4j @Tool /
  ToolProvider). Needs read access to the project's source and build files
  (pom.xml / build.gradle); ripgrep recommended for the optional tool-surface
  scan. Perishable API identifiers in references/API-REFERENCE.md are grounded
  against LangChain4j 1.16.2 and must be re-verified for the project's version.
metadata:
  version: "1.0"
  grounded-against: "langchain4j 1.16.2"
  domain: "agentic-backend-tools"
---

# LangChain4j Tool Architect

Improve the **tools** an LLM agent can call in a LangChain4j (Java) backend:
design new ones, refine existing ones, audit a whole tool surface, harden it
against the OWASP LLM Top 10, or scale it past the point where the model starts
picking the wrong tool. The output is a grounded report of findings plus, on
request, the implemented changes.

Respond in the user's language. This skill is harness- and language-agnostic and
portable across projects — do not assume any specific agent harness, cloud
provider, DI framework, or company convention unless the project's own files
prove it.

## Vocabulary

Use these terms exactly — consistency is the point. Full definitions in
[references/GLOSSARY.md](references/GLOSSARY.md).

- **Tool** — a capability the model can invoke; a `@Tool` method or a
  programmatic `ToolSpecification` + executor.
- **Tool contract** — everything the *model* sees and reasons over: the name,
  the description, the parameter schema, and the shape of the return value. Not
  the Java body. The contract is the model's test surface.
- **Tool surface** — the set of tool contracts exposed to the model in one turn.
  It has a token cost and a precision cost.
- **Gating strategy** — how the surface is chosen: static (all tools every
  turn), retrieval (tool-search / RAG-over-tools), or activation (skills).
- **Intention vs Identity** — the model supplies *intention* (which month, which
  product); the server supplies *identity* and *authorization*. Mixing them is
  the root security defect.
- **Read tool vs Write tool** — read is idempotent and safe; write moves money
  or state and needs a human-in-the-loop (HITL) gate, idempotency, and
  reinforced authorization.

## The seven tests

These named heuristics are the analytical spine. Every finding in the report
should name the test it fails. Details and fixes in
[references/BEST-PRACTICES.md](references/BEST-PRACTICES.md).

1. **Intention test** — Does the tool mirror a *user intention* or a *backend
   endpoint*? Tools are a façade for the model, not a 1:1 mirror of REST.
2. **Description test** — Could a new hire (or the model) pick the right tool,
   use it correctly, and know *when not to* — from the name + description alone?
3. **Identity test** — Can the model supply *any* identity or authorization
   argument? If yes, that is a vulnerability (OWASP LLM06 / LLM02).
4. **Blast-radius test** — What is the worst outcome if this executes with
   hallucinated or adversarial arguments? Drives the read/write split and HITL.
5. **Return-shape test** — Does it return small, shaped, PII-minimized data, or
   raw backend JSON that wastes tokens and leaks fields?
6. **Failure-as-data test** — On failure, does it return structured data the
   model can act on, or throw an exception that leaks internals and aborts?
7. **Surface-budget test** — How many tool contracts does the model see per
   turn, and is the gating strategy right for that count (consolidate /
   specialize / retrieve / skills past ~30–50)?

## Process

### Step 0 — Ground the environment (always first)

Read the build files (`pom.xml`, `build.gradle[.kts]`) and detect: the
**LangChain4j version**, the **model provider** (Bedrock, OpenAI, Anthropic,
Ollama, …), the **DI / web framework** (Micronaut, Quarkus, Spring, plain), and
whether tools are wired via `AiServices` or the low-level API.

[references/API-REFERENCE.md](references/API-REFERENCE.md) is ground truth for
**1.16.2 only**. If the project is on another version, treat every identifier
there as a hypothesis and **re-verify it against that version's javadoc /
changelog before emitting any code**. Never paste an API name you have not
confirmed for the project's version. Flag any deviation to the user.

### Step 1 — Frame the engagement (interrogation)

First, pin the **mode** with one question (audit a whole surface / refine one
tool / design a new tool / harden security / scale past N tools). Then walk the
mode's decision tree from [references/INTERROGATION.md](references/INTERROGATION.md),
**one question at a time, each with your recommended answer**.

Golden rule: **if the codebase can answer it, explore instead of
asking.** In *audit* and *refine* modes, run the light ripgrep scan in the
interrogation reference *before or alongside* the questions, so you never ask
"do any tools move money?" when a `transfer(...)` tool is sitting in the source.
In *greenfield create* mode, the interrogation leads.

Stop interrogating only when every branch that changes the recommendation is
resolved. Leave no loose ends.

### Step 2 — Explore the tool surface

Map the surface: every `@Tool` method, every `ToolProvider` /
`ToolSpecification`, the `AiServices` wiring, any guardrails, **where caller
identity comes from**, and how many tools are exposed per turn. Use a dedicated
search subagent if your harness offers one (e.g. an `Explore` agent); otherwise
read the source directly. In single-tool mode, scope to that tool and its
neighbors.

### Step 3 — Analyze against the rubric

Run the seven tests over the surface, cross-referenced with
[references/BEST-PRACTICES.md](references/BEST-PRACTICES.md) and
[references/SECURITY-OWASP.md](references/SECURITY-OWASP.md). For each finding,
name the failing test, cite the durable rule, and (for security) the OWASP LLM
ID. Separate *durable* design findings from *perishable* version-specific ones.

### Step 4 — Report

Write a portable **Markdown** report following
[references/REPORT-FORMAT.md](references/REPORT-FORMAT.md): one card per finding
(test failed, severity, files/tool, problem, grounded recommendation, before /
after Mermaid diagram, citation), ending with a **Top recommendation**. Save it
to a file and tell the user the path. Do not render HTML and do not assume a
browser. In audit mode, do **not** finalize new tool contracts yet — ask the
user which findings to pursue.

### Step 5 — Grill & implement

Once the user picks a finding, drop into a focused grilling conversation about
that change — constraints, the authorization seam, confirmation and idempotency
for writes, the return shape, what the tool contract becomes. Then implement it,
**grounding every API identifier against the re-verified
[references/API-REFERENCE.md](references/API-REFERENCE.md)**. When creating a new
tool, follow the create checklist in BEST-PRACTICES.md and re-run the seven
tests on the result.

## References

- [references/GLOSSARY.md](references/GLOSSARY.md) — the exact vocabulary.
- [references/INTERROGATION.md](references/INTERROGATION.md) — the mode-aware
  decision-tree question bank.
- [references/BEST-PRACTICES.md](references/BEST-PRACTICES.md) — durable,
  provider- and version-agnostic rubric (the seven tests, with fixes + sources).
- [references/API-REFERENCE.md](references/API-REFERENCE.md) — perishable
  LangChain4j 1.16.2 tool API surface and hallucination traps.
- [references/SECURITY-OWASP.md](references/SECURITY-OWASP.md) — the OWASP LLM
  Top 10 mapped to tool-specific threats and mitigations.
- [references/REPORT-FORMAT.md](references/REPORT-FORMAT.md) — the portable
  Markdown + Mermaid report scaffold.
