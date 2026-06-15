# Security — OWASP LLM Top 10, mapped to tools

How the OWASP Top 10 for LLM Applications (2025) shows up specifically in the
**tool** layer, and the deterministic mitigations that belong in code. Provider-
and version-agnostic. Primary source: <https://genai.owasp.org/llm-top-10/>.

> Note on scope: this is the **LLM Applications** Top 10 (2025). OWASP also
> publishes a separate "Agentic Applications" threats list — if the project is
> heavily multi-agent, cross-reference that too, but the items below are the core
> tool risks.

## The one principle

**Control lives in code, never in the prompt.** Authentication, authorization,
idempotency, rate-limiting, and confirmation are deterministic backend
enforcement. A system message that says "only access the caller's own accounts"
is not a control — it can be socially engineered or overwritten by injected
text. Authorize **downstream**, in the tool implementation, every time.

## Threat → tool vector → mitigation

| OWASP ID | Tool-layer vector | Deterministic mitigation | Related test |
|---|---|---|---|
| **LLM01 Prompt Injection** | A jailbreak (direct) or an instruction hidden in a RAG document / tool *result* (indirect) drives the model to call a tool it shouldn't, or with hostile arguments. | Input guardrails at entry; **segregate untrusted content** (JSON-encode tool results, mark their source) so instructions inside data aren't followed; allow-list validation of arguments before execution. | Description, Failure-as-data |
| **LLM02 Sensitive Info Disclosure** | A tool returns another tenant's data, or raw payloads leak PII/internal fields into context and logs. | **Authorize by server-side identity**, never a model argument; **minimize the return shape**; partition multi-tenant data by a hard server-side filter. | Identity, Return-shape |
| **LLM05 Improper Output Handling** | Model output (echoing a tool result or an injected instruction) is consumed downstream as SQL/HTML/shell → SQLi, XSS, SSRF, RCE. | Treat all model output as untrusted; parameterized queries; context-aware encoding; typed/validated output, never string-concatenation into a sink. | Return-shape |
| **LLM06 Excessive Agency** | The model triggers a consequential action (transfer, deletion) with no confirmation or idempotency, or with authority it shouldn't have. | **Least privilege** per tool; **complete mediation** (authorize every call downstream); **HITL gate** + **idempotency** on writes; cap the tool-calling loop. | Identity, Blast-radius |
| **LLM07 System Prompt Leakage** | A secret, credential, or authorization rule placed in the system prompt leaks to the model and out. | **Never put secrets or authz rules in the prompt.** They live server-side; the prompt is not a vault. | Identity |
| **LLM08 Vector / Embedding Weaknesses** | In a shared vector store backing tool-retrieval or RAG, one tenant retrieves another's content. | **Partition by metadata with a hard filter**, enforced in code — not model-enforced. | Identity, Surface-budget |
| **LLM09 Misinformation** | The model states a hallucinated balance/fact as if it came from a tool. | Ground answers in tool/RAG results; output guardrails; don't let the model invent fields the tool didn't return. | Return-shape, Failure-as-data |
| **LLM10 Unbounded Consumption** | "Denial-of-wallet": a loop of tool calls / inferences spirals cost. | Rate-limit per caller; cap the tool-calling loop; budget/timeout the agent. | Blast-radius, Surface-budget |

(LLM03 Supply Chain and LLM04 Data & Model Poisoning matter for the broader
system — pin dependencies, curate ingested data — but are less tool-contract
specific.)

## The two flagship tool risks

Most tool security failures collapse into two of the above. Lead with these:

### LLM06 Excessive Agency + LLM02 Disclosure — the identity confusion
The single highest-leverage fix is the **Identity test**: no identity or
authorization argument on any tool contract. The model supplies intention; the
server derives identity from the authenticated session and authorizes in code.
This one rule defeats "trick the model into passing another customer's id" and
contains the blast radius of any successful prompt injection.

### LLM01 Prompt Injection — direct and indirect
Direct injection (user jailbreak) is caught at the entry guardrail. **Indirect**
injection is harder: an instruction smuggled inside a document the RAG tool
retrieves, or inside a tool's own returned data. Defend by treating all
tool-returned and retrieved content as **data, not instructions** — encode it,
attribute its source, and never let it widen the model's authority. Identity-by-
server (above) ensures that even a successful injection cannot escalate *whose*
data is reachable.

## Guardrail vs Authorization — don't confuse them

- A **guardrail** (input/output validation, content moderation) is probabilistic
  defense-in-depth. It *reduces* residual risk.
- **Authorization** is a deterministic check in code. It *is* the control.
- A guardrail that catches a PII leak is a useful backstop; it never replaces the
  `caller.owns(account)` check. Build both, but never let one stand in for the
  other.

## Audit questions (fold into the interrogation)

1. Can the model set any identity/scope argument on any tool? (→ LLM06/LLM02)
2. Is every consequential tool authorized downstream, in code? (→ LLM06)
3. Do write tools have a HITL gate and idempotency? (→ LLM06)
4. Are tool results and retrieved documents treated as data, not instructions?
   (→ LLM01)
5. Do tool returns leak more than the intention needs? (→ LLM02)
6. Are secrets/authz rules kept out of the system prompt? (→ LLM07)
7. In multi-tenant retrieval, is partitioning a hard server-side filter? (→ LLM08)
8. Is the tool-calling loop capped and the caller rate-limited? (→ LLM10)
