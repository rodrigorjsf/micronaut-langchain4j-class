# Best Practices — the rubric

Durable, provider- and version-agnostic design rules for LLM-callable tools.
These do not rot when LangChain4j ships a new version: they are about the **tool
contract** the model reasons over, not the Java identifiers that implement it.
Exact, perishable identifiers (annotation attributes, enum constants, defaults,
method names) live in [API-REFERENCE.md](API-REFERENCE.md) — keep them out of
here on purpose.

Each test below is: the **question**, **why** it matters, the **smell** that
fails it, the **fix**, and the **source** to re-ground against.

---

## 1. Intention test

**Question:** Does the tool mirror a *user intention* or a *backend endpoint*?

**Why:** Tools are a façade for the model, not a 1:1 export of your REST layer.
The model reasons in user intentions ("what's my current invoice?"), not in
service boundaries. A surface shaped like the backend forces the model to
orchestrate plumbing it shouldn't know about.

**Smells:**
- One coarse tool returning a giant blob (`getCardEverything`) so the model
  wades through thousands of tokens to find one field.
- A spray of micro-tools (`getLimitTotal`, `getLimitUsed`, `getLimitAvailable`)
  that forces sequential round-trips and floods the surface with near-duplicate
  descriptions.
- Tool names that match controller methods, not things a user would ask for.

**Fix:** One tool ≈ one user-facing capability. Consolidate two backend calls
into one tool when the user thinks of them as one action; split a fat endpoint
into two focused tools when the user thinks of them separately. Aim for the
"Goldilocks" granularity between coarse-blob and micro-tool.

**Source:** Anthropic, "Writing tools for agents" (anthropic.com/engineering) —
"more tools don't always lead to better outcomes; consolidate rather than map
1:1." LangChain4j tools tutorial (docs.langchain4j.dev/tutorials/tools).

---

## 2. Description test

**Question:** Could a competent new hire — or the model — pick the right tool,
use it correctly, and know *when not to use it*, from the name and description
alone?

**Why:** The description is **executable logic**: it is the single biggest lever
on which tool the model calls and how it fills the arguments. In practice the
large majority of agent tuning is rewriting descriptions, not changing the model
or its hyperparameters. Treat descriptions as code.

A strong description states four things:
1. **What** the tool does.
2. **When** to use it — and explicitly **when not to** (point at the right
   alternative).
3. **Units and formats** — currency, date format, timezone, ID scheme.
4. **Side effects** — if it moves money or mutates state, say so.

**Smells:** `"Returns invoice."` Bare restatement of the method name. No "when
not to use." Ambiguous units. Two tools whose descriptions are near-duplicates
(the model will confuse them).

**Fix:** Rewrite to the four-part shape. Name tools verb+noun and keep them
mutually distinct. When two tools are easily confused, either merge them or
sharpen the "when not to use this one" line in each.

**Source:** Anthropic, "Writing tools for agents" — "describe the tool like you'd
describe it to a new hire." OpenAI function-calling guide
(platform.openai.com/docs/guides/function-calling).

---

## 3. Identity test

**Question:** Can the model supply *any* identity or authorization argument
(user id, account id, tenant, role)?

**Why:** If identity is a tool parameter, the model — or anything that can inject
text into the model, including a poisoned document or tool result — can set it.
That is the confused-deputy vulnerability behind OWASP LLM06 (Excessive Agency)
and LLM02 (Sensitive Information Disclosure). The model must never be the thing
that decides *whose* data is touched.

**Smell:** `getInvoice(String customerId, ...)`, `transfer(String fromAccount,
...)` — any signature where the model fills an identity or scope field.

**Fix:** Split **intention** from **identity**. The model supplies intention
(which month, which product, which action). The server injects identity from the
authenticated session — in LangChain4j via the memory-id mechanism (see
API-REFERENCE) — and authorizes the action in code, downstream, before
executing. Identity arguments simply do not appear on the contract.

**Source:** OWASP LLM Top 10, LLM06 & LLM02 (genai.owasp.org/llm-top-10) —
"implement authorization in downstream systems rather than relying on an LLM."
See [SECURITY-OWASP.md](SECURITY-OWASP.md).

---

## 4. Blast-radius test

**Question:** What is the worst outcome if this tool executes with hallucinated
or adversarial arguments?

**Why:** Read and write tools carry different risk. A wrong read wastes a turn; a
wrong write moves real money or destroys state. The contract should make the two
classes obvious and gate the dangerous one.

**Smells:** A money-moving or state-mutating tool that auto-executes with no
confirmation; a write tool with no idempotency key (a retried loop double-pays);
a destructive action named like a query (`processAccount` that actually closes
it).

**Fix:**
- **Classify** every tool read vs write; let the name signal it (`get…` /
  `list…` vs `transfer…` / `schedule…` / `close…`).
- **Gate writes** behind a deterministic HITL confirmation in code, not a prompt.
- **Make writes idempotent** (client-supplied idempotency key) so a retried
  agentic loop can't double-execute.
- **Cap the loop** so a misbehaving agent can't call tools indefinitely (the
  per-version knob is in API-REFERENCE).

**Source:** OWASP LLM06 Excessive Agency (least privilege, complete mediation,
human-in-the-loop). Anthropic & OpenAI tool guides on confirming consequential
actions.

---

## 5. Return-shape test

**Question:** Does the tool return small, shaped, PII-minimized data — or raw
backend JSON?

**Why:** The return value re-enters the model's context and its logs. Raw backend
payloads are expensive (tokens), noisy (the model hunts for the relevant field),
and leaky (internal fields and PII land in context and transcripts). Data
minimization here is both a quality and a security control.

**Smell:** `return backendResponse;` (the whole DTO). Returning a raw map/dict.
Returning more fields than the user's intention needs.

**Fix:** Return a small, explicitly-shaped object with only what the model needs,
in a stable structure: e.g. `{ amount: 2310.55, currency: "BRL", dueDate:
"2026-06-20", status: "OPEN" }`. Prefer a concrete record/POJO over a raw map
(map returns have a serialization trap — see API-REFERENCE). Keep the shape
stable across calls so the model can rely on it.

**Source:** Anthropic, "Writing tools for agents" — "return high-signal
information." OWASP LLM02 (data minimization reduces disclosure surface).

---

## 6. Failure-as-data test

**Question:** When the tool fails, does it return structured data the model can
act on — or throw an exception that leaks internals and aborts the loop?

**Why:** By default, an uncaught exception's message is often handed back to the
model and surfaced to the user — leaking stack traces, backend hostnames, or
PII, and giving the model nothing structured to recover from. A well-shaped error
lets the model apologize, retry, or escalate gracefully.

**Smell:** Tool throws on a downstream outage and the raw exception text reaches
the conversation. No distinction between "retryable" and "terminal" failures.

**Fix:** Catch expected failures inside the tool and **return them as data**:
`{ error: "BACKEND_UNAVAILABLE", message: "Temporarily unavailable, try again" }`.
Log the real cause server-side with full detail; send the model only a sanitized,
actionable summary. Where the framework offers a tool-execution error handler,
use it to enforce this globally (identifier in API-REFERENCE).

**Source:** OWASP LLM05 Improper Output Handling & LLM02. LangChain4j tools
tutorial on tool-execution error handling.

---

## 7. Surface-budget test

**Question:** How many tool contracts does the model see per turn, and is the
gating strategy right for that count?

**Why:** Every exposed tool spends tokens (its description, every turn) and
competes for the model's attention. Above roughly 30–50 tools, selection
precision degrades sharply — the model starts confusing similar options. The fix
is rarely "a better model"; it's shrinking what the model has to choose from.

**Smell:** Dozens of tools statically exposed on every turn. Many near-duplicate
descriptions. One monolith agent owning every domain.

**Fix (in escalating order):**
1. **Consolidate** by domain and prune descriptions (often enough on its own).
2. **Specialize** — split into several agents, each with its own small tool
   subset (cards / payments / investments).
3. **Retrieve** — expose only the turn-relevant tools via tool-search /
   RAG-over-tools (mechanisms in API-REFERENCE).
4. **Activate** — load domain bundles on demand via skills (progressive
   disclosure; mechanism in API-REFERENCE).
5. **Namespace** tools (`cards.getInvoice`, `payments.send`) to keep selection
   unambiguous.

**Source:** Anthropic, "Writing tools for agents" — precision degrades past
~30–50 tools; use tool search. OpenAI function-calling guide — "aim for fewer
than ~20 functions at the start of a turn."

---

## Cross-cutting rules

- **Control lives in code, never in the prompt.** Auth, authz, idempotency,
  rate-limiting, and confirmation are deterministic server concerns. A system
  message is not a control surface.
- **The tool contract is the model's test surface.** If you have to test *past*
  the contract to know the tool behaves, the contract is the wrong shape.
- **Ground every emitted identifier against the project's version.** The durable
  rules above are stable; the names that implement them are not. Re-verify
  API-REFERENCE for the project's LangChain4j version before writing code.

---

## Create checklist (new tool)

When designing a new tool, walk these in order — it is the seven tests applied
forward:

1. **Intention** — name the single user-facing capability this tool serves.
2. **Contract** — verb+noun name; four-part description (what / when / when-not /
   units+side-effects).
3. **Parameters** — intention only; no identity or authz fields; typed and
   constrained (enums close the value space); each one described; each one a
   chance for hallucination, so keep them few.
4. **Identity** — confirm identity/authz come from the server session, not a
   parameter.
5. **Blast radius** — read or write? If write: HITL gate + idempotency +
   downstream authz.
6. **Return** — small, shaped, stable, PII-minimized; concrete type, not a raw
   map.
7. **Failure** — structured error data; sanitized message to the model, full
   cause to the server log.
8. **Budget** — does adding this tool push the surface past its precision
   budget? If so, revisit the gating strategy.
9. **Observe** — emit a span/metric for the call (name, sanitized args, latency,
   outcome) without blocking the model thread.

Re-run tests 1–7 on the finished tool before declaring it done.

---

## Primary sources

Full, resolvable URLs behind the rules above — re-ground against these before
relying on any specific claim. They are durable, provider-neutral references.

- Anthropic — "Writing effective tools for agents — with agents":
  https://www.anthropic.com/engineering/writing-tools-for-agents
- OpenAI — Function calling guide:
  https://platform.openai.com/docs/guides/function-calling
- LangChain4j — Tools tutorial:
  https://docs.langchain4j.dev/tutorials/tools
- OWASP — Top 10 for LLM Applications (2025):
  https://genai.owasp.org/llm-top-10/
