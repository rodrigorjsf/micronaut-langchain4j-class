# Glossary

Shared vocabulary for every finding and recommendation this skill makes. Use
these terms exactly — don't drift into "function," "endpoint," "API," or
"permission" when a term below is meant. Consistent language is what makes the
report navigable.

## Terms

**Tool**
A capability the model can invoke during the agentic loop. In LangChain4j it is
either a method annotated `@Tool` or a programmatic `ToolSpecification` paired
with an executor. Scale-agnostic: a tool can wrap one backend call or several.
_Avoid_: "function" (too low-level), "endpoint" (that's the backend, not the tool).

**Tool contract**
Everything the *model* sees and reasons over: the **name**, the **description**,
the **parameter schema**, and the **shape of the return value**. It is the
model-facing surface — *not* the Java implementation behind it. This is the
analog of an "interface": the model only ever crosses the contract, so the
contract is where agent quality is won or lost.
_Avoid_: "signature" (too narrow — the description and return shape are part of
the contract, and they carry most of the weight).

**Tool implementation**
The Java body behind the contract — validation, authorization, the backend
call, the shaping of the result. The model never sees it. A small contract can
sit in front of a large implementation (good: deep) or a large contract in
front of a thin pass-through (smell: shallow).

**Tool surface**
The set of tool contracts exposed to the model in a single turn. It has two
costs: a **token cost** (every description is re-sent each turn) and a
**precision cost** (the more similar contracts compete, the more often the model
picks the wrong one).

**Gating strategy**
How the surface is chosen for a turn:
- **Static** — all tools, every turn. Simple; fine for a handful of tools.
- **Retrieval** — only the tools relevant to this turn are exposed
  (tool-search / RAG-over-tools). For large surfaces.
- **Activation** — domain bundles loaded on demand (skills). For many domains.

**Intention vs Identity**
The split that governs tool security. The **model** supplies *intention* — what
the user wants done (which month's invoice, which account to *view*). The
**server** supplies *identity* and *authorization* — who the caller is and what
they may touch. Identity is derived from the authenticated session, never from a
model-provided argument. Mixing the two is the root cause of the worst tool
vulnerabilities.

**Read tool vs Write tool**
- **Read tool** — idempotent and side-effect-free (`getBalance`, `getInvoice`).
  Safe to auto-execute when the model asks.
- **Write tool** — moves money or mutates state (`transfer`, `schedulePayment`,
  `openAccount`). Requires a HITL gate, idempotency, and reinforced
  authorization at the server.

**HITL gate**
A deterministic human-confirmation checkpoint enforced in code before a write
tool executes. It is a control, not a sentence in the system prompt.

**Guardrail vs Authorization**
- **Guardrail** — a probabilistic, best-effort filter (input/output validation,
  content moderation). Defense-in-depth.
- **Authorization** — a deterministic check in code (does this caller own this
  account?). A guardrail *never* replaces an authorization check.

**Façade-not-mirror**
The design stance for the whole surface: tools are a *façade* shaped around the
model's intentions, not a *mirror* of the backend's REST endpoints.

## Principles

- **The tool contract is the model's test surface.** The model only ever sees
  the contract, so ambiguity, missing units, or a vague "when to use" line are
  bugs in the contract — not user error.
- **Identity is never a model input.** The model proposes intention; the server
  decides identity and authorization.
- **Control lives in code, never in the prompt.** Authentication, authorization,
  idempotency, rate-limiting, and confirmation are deterministic server
  concerns. A system message that says "only access your own accounts" is not a
  control — it can be talked around.
- **A description is executable logic, not documentation.** It drives which tool
  the model calls. Treat it like code: version it, review it, test it.
