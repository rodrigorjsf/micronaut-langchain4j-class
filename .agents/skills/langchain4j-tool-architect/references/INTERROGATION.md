# Interrogation

A relentless-but-targeted interview that pins the user's *real* goal before any
analysis or code. Modeled on grill-me, scoped to agentic-backend tools.

## Rules

1. **One question at a time.** Never dump a checklist. Ask, get the answer, let
   it steer the next question.
2. **Always recommend an answer.** For every question, give your recommended
   answer and a one-line reason, so the user can simply confirm.
3. **Explore before you ask.** If the codebase can answer a question, read the
   code instead of asking. Only ask what the code cannot settle (intent,
   constraints, priorities, risk tolerance).
4. **Walk the tree, resolve dependencies.** Later questions depend on earlier
   answers — don't ask about a gating strategy before you know the tool count.
5. **Stop when no remaining branch changes the recommendation.** Leave no loose
   ends; do not over-interrogate once the path is determined.

## Phase 0 — Pin the mode (one question, always first)

> "What do you want out of this? (a) audit a whole backend's tool surface;
> (b) refine or fix one existing tool; (c) design a new tool from scratch;
> (d) harden tool security; (e) scale past N tools / fix wrong-tool selection."

Infer a recommended mode from what the user already said. The mode decides the
ordering of Steps 1–2 in SKILL.md:

- **(a) audit / (b) refine / (d) harden / (e) scale** → run the **light scan
  first**, then ask only what code can't answer.
- **(c) greenfield create** → interrogation leads; little or no code to scan yet.

## Light scan (run first in modes a/b/d/e)

Best-effort ripgrep patterns to answer questions before asking them. Adjust to
the project's language/layout; treat hits as leads, not proof.

```bash
# Every tool and its declared name/description
rg -n "@Tool" --type java -A3

# Tools that move money / mutate state (blast-radius candidates)
rg -ni "@Tool" -A4 | rg -i "transfer|pay|payment|withdraw|delete|cancel|create|open|close|update|send|schedul"

# Identity / authorization leaking into the model as parameters (Identity test)
rg -ni "@P\b.*\b(userId|customerId|clientId|accountId|account_id|tenant|owner)\b"

# Programmatic / dynamic surfaces
rg -n "ToolProvider|ToolSpecification|toolProvider|ToolSearchStrategy|VectorToolSearchStrategy"

# Guardrails present?
rg -n "InputGuardrail|OutputGuardrail|@InputGuardrails|@OutputGuardrails|Guardrail"

# Loop / safety knobs
rg -n "maxToolCallingRoundTrips|toolExecutionErrorHandler|hallucinatedToolName"

# Raw map / unshaped returns (Return-shape test)
rg -n "@Tool" -A8 | rg -i "Map<|return .*toString|getRaw|RawResponse"

# How many tools, roughly, and how they are wired
rg -c "@Tool" --type java
rg -n "\.tools\(|\.toolProvider\(" --type java
```

## Decision tree (ask only the branches the scan left open)

### A. Criticality & domain
- Does any tool **move money or mutate state**? *(Rec: assume yes until proven
  otherwise — it changes the whole risk posture.)*
- Does any tool touch **PII** or run **multi-tenant**? *(Rec: if multi-tenant,
  partition + authorize by server-side identity, never by a model argument.)*

### B. Current pain (skip in greenfield)
- What's actually wrong: **wrong tool picked**, **too many tools**, **token
  cost**, **a security worry**, **hallucinated arguments**, or **errors leaking**
  to the user? *(Rec: name the dominant symptom; it selects which of the seven
  tests to lead with.)*

### C. Identity & authorization
- Where does **caller identity** come from today — session/JWT, or a tool
  parameter? *(Rec: session-derived, injected server-side; a tool parameter is a
  red flag — see Identity test / LLM06.)*
- Is authorization enforced **in code** (downstream), or assumed from a system
  prompt instruction? *(Rec: in code, always.)*

### D. Write-tool safety (only if any write tool exists)
- Is there a **HITL confirmation** gate and an **idempotency** key before a write
  executes? *(Rec: both, enforced server-side; confirmation is not a prompt.)*

### E. Scale & gating
- How many tools are exposed **per turn**, and what is the **gating strategy**
  (static / retrieval / skills)? *(Rec: static under ~20–30; introduce retrieval
  or skills as the count climbs and precision drops.)*

### F. Constraints (mostly answerable from build files)
- LangChain4j **version**? Model **provider**? **AiServices** or low-level API?
  **Streaming** or sync? **DI framework**? *(Rec: read `pom.xml` /
  `build.gradle`; only confirm what's ambiguous. These drive which API names are
  valid — see Step 0 grounding.)*

### G. Return contract
- Do tools return **shaped** data or **raw backend JSON**? Are failures returned
  as **structured data** or thrown as exceptions? *(Rec: shaped + structured
  errors — see Return-shape and Failure-as-data tests.)*

### H. Target
- Do you want **a report only**, or should I **implement** the agreed changes?
  *(Rec: report first, then implement the picks one at a time.)*

## Exit

When the remaining branches no longer change your recommendation, summarize the
resolved decisions in two or three lines and confirm before moving to Explore /
Analyze. That summary is the brief the rest of the skill works from.
