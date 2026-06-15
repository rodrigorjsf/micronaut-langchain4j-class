# Architecture Rubric (durable)

Four whole-flow checks. They are deliberately **lean** — their only job is to feed
the create / update / migrate decision. They do **not** cover individual tool
contracts; when a finding is about one tool's granularity, schema, return shape, or
per-tool authorization, name it and **defer to the `langchain4j-tool-architect`
skill.** Perishable identifiers (API names, default values) live in
API-REFERENCE.md, not here — these rules do not rot when the version moves.

## 1. Loop-bounded

**Question:** Is the agentic loop capped and guaranteed to terminate?

**Why it matters:** An uncapped loop is a cost and reliability hazard — a
misbehaving or adversarial turn can spin tool calls indefinitely. This is
orthogonal to migration, but it is the cheapest production defect to catch while
you have the architecture open.

**Fix:** Cap the max tool-calling round-trips to a small production value; the
default is large (see API-REFERENCE.md). Treat exhaustion as a handled outcome, not
a crash.

**Source:** the tools / AI Services tutorials at https://docs.langchain4j.dev.

## 2. System-prompt budget

**Question:** How much of the system message is **conditional procedure** — a
manual for one scenario — versus **always-relevant policy**?

**Why it matters:** Conditional procedure parked in the system prompt is paid for on
every turn: tokens, latency, and signal-to-noise. A prompt that is mostly
per-scenario manuals is the textbook case progressive disclosure was built for — and
the primary input to the migration scorecard.

**Fix:** Tag each block of the prompt as policy (stays) or procedure (a skill
candidate). The procedure blocks become skill bodies; the reference data they cite
becomes loaded resources.

**Source:** the progressive-disclosure rationale at https://agentskills.io and the
langchain4j-skills tutorial at https://docs.langchain4j.dev.

## 3. Gating strategy

**Question:** Is the surface gated **statically**, by **retrieval**, or by
**activation** — and does that fit the tool count and the conditionality of the
flows?

**Why it matters:** Static gating is correct while the surface is small. As tools
grow and many become conditional, static gating wastes budget and erodes tool-pick
precision. Retrieval and activation are the two ways out, and they compose.

**Fix (rule of thumb, not a hard line):**

- Small surface, mostly always-relevant tools → **static**.
- Many tools, no clean scenario clusters → **retrieval** (vector tool-search).
- Conditional, cohesive scenario clusters with their own instructions and knowledge
  → **activation (skills)**.

Document the deciding signal; do not migrate a surface that has no bloat.

**Source:** the tool-provider / tool-search tutorials at
https://docs.langchain4j.dev; the scorecard in SKILL-MIGRATION.md.

## 4. Identity seam

**Question:** Does caller identity / authorization enter the request **server-side**
(session, token, the memory-id injection mechanism) and get enforced **in code**,
independent of which flow or skill is active?

**Why it matters:** Migration changes *what the model sees*, never *what the model is
allowed to do*. If authorization is assumed from a prompt instruction or read from a
model-supplied argument, activation-gating will appear to "hide" the capability
while leaving it fully exploitable. Activation is context management, not an
authorization boundary.

**Fix:** Keep identity injected server-side; enforce authorization downstream in code
for every flow, activated or not. For the deep per-tool fix, defer to the
tool-architect skill (its Identity test; OWASP LLM06 / LLM02).

**Source:** https://genai.owasp.org/llm-top-10/ (LLM06 Excessive Agency, LLM02
Sensitive Information Disclosure).
