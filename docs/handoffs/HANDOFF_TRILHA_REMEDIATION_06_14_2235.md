# Handoff: Trail-review remediation — Waves 2 & 3 (LangChain4j banking course)

**Created:** 2026-06-14 ~22:35 America/Fortaleza (UTC-3) · **Branch:** `main` (everything untracked; single `Initial commit`)
**Supersedes:** `docs/handoffs/HANDOFF_WAVES_2_3_06_14.md` (now deleted — this is the canonical continuation doc).

> **Workspace type:** `/teach` teaching workspace, NOT an app. The unit of work is a self-contained HTML lesson in `lessons/00NN-*.html`. Spec: `.claude/skills/teach/SKILL.md`. Doctrine (auto-loads on file-match): `CLAUDE.md` + `.claude/rules/{lesson-authoring,content-grounding,source-drafts}.md`.

---

## Summary

A 19-lesson pt-BR course was audited; the audit found it "ship-blocked on correctness, not substance." **Wave 1 (correctness) is DONE and adversarially verified. Wave 2 medium fixes are mostly DONE.** Remaining: a few small medium fixes, the four missing deliverables (Wave 2), and the entire visual pass (Wave 3). Work resumes at **Wave 2 → badge-softening + deliverables**.

---

## ⭐ IMMEDIATE NEXT STEPS (start here)

1. **Re-derive state from disk first** (do not trust this doc blindly):
   ```bash
   cd /home/rodrigo/Workspace/micronaut-langchain4j-class
   python3 scripts/validate_lessons.py                 # must print ALL GREEN (19 lessons)
   grep -rn "Módulo [0-9]" lessons/*.html              # must be empty (renumber gate)
   grep -n "tipoConta\|versao\|vigencia" lessons/0005-rag.html   # must be empty
   ```
2. **Finish the remaining Wave 2 MEDIUM fixes** (small, safe — bank them before heavy authoring):
   - **Badge-softening (NOT yet done):** soften "verificado"/"verified" claims the audit flagged as unconfirmed — **L07** (`hallucinatedToolNameStrategy` default=`THROW_EXCEPTION`), **L08** (`~90% economia / 85% menos latência` figures → mark illustrative; add per-model TTL caveat: `VALUE_1_H` unsupported on Sonnet 4.6), **L10/L16** (Map-output warnings), **L15** (add a direct OWASP raw-source link). Soften or cite; never remove a *legitimately* verified badge.
   - **L05 residual (judgment call):** `lessons/0005-rag.html` line 205 §12-diagram metadata key list still reads `{produto, account_scope, version, validity, idioma}` — `produto`/`idioma` are pt-BR keys among English ones. Either rename to `product`/`language` (consistent with `content-grounding.md`) or leave as descriptive labels — decide and apply. (The medium-fix agent left them out of its enumerated scope and flagged the divergence with L09's pt-BR prose.)
3. **Author the four missing deliverables** (Wave 2). See "Deliverables plan" below. **APPEND as `0020+` — never insert.**
4. **Wave 3 visual** then **README last**. See plan below.

**HARD RULE for all new technical content:** route it through the **adversarial-verify workflow** before calling it "done" (see "Verification protocol"). Wave 1 proved the *audit itself* was wrong about an API (L11 `maxRetries`) and the fix inherited the error — only the skeptic workflow caught it.

---

## Work Completed

### Wave 1 — correctness (DONE, adversarially verified, ALL GREEN)
- [x] Broken-code cluster: **L07** (`ctx.rawError()`→bound `Throwable error`), **L13** (ScopedValue doesn't cross the `newVirtualThreadPerTaskExecutor`; identity via `@ToolMemoryId`), **L14** (honest "annotations sketch — does NOT auto-compose" caveat), **L17** (`.listeners(List.of(...))`), **L18** (dropped dead `credentialsProvider` param; model ids → Sonnet/Haiku 4.5).
- [x] Módulo→Lição renumber: L02–L06 + `index.html` (40+ refs, pt-BR gender agreement, L06 "fundação" table). 0 learner-facing `Módulo N` left.
- [x] Grounding falsehoods: L02 (`seed`), L03 (tiktoken folklore → Bedrock `CountTokens`), L09 (Titan GA/English-optimized), L11 (`maxRetries` = total invocation cap, default 2 → up to 2).
- [x] Verified by a 9-agent adversarial workflow; 2 refutations (L11, L17 comment) corrected. Recorded in `docs/reviews/2026-06-14-trilha-19-licoes-review.md` → "Wave 1 resolution".

### Wave 2 — medium fixes (PARTIAL — done this session)
- [x] **L05/L09 key unification:** L05 now uses `account_scope` (was `tipoConta`); quiz Q3 confirmed still `data-correct="a"` (answer is about the *mechanism*, unaffected by key name). L09 untouched (reference).
- [x] **English-code:** L05 JSON keys `versao→version`, `vigencia→validity`; L12 Java `//` and YAML `#` comments translated to English (model-facing `@Tool`/`@P`/`@SystemMessage` literals kept pt-BR).
- [x] **Acronyms:** L01 (ReAct, RAG, "janela de contexto"), L11 (PII, IAM, SPI, GA, RAG) expanded at first use.

### Key Decisions

| Decision | Rationale |
|---|---|
| **Append new lessons as `0020+` in a new "Parte 5"; freeze L1–L19 file numbers** | Inserting mid-sequence would re-break the cross-ref graph + every prev/next nav seam just repaired. `index.html` controls presentation order. |
| **Every new technical lesson passes the adversarial-verify workflow before "done"** | Wave 1 proved the audit itself can be wrong (L11). New lessons = fresh claims = higher risk. |
| **Wave 2 order: medium fixes → deliverables; README dead last** | Medium fixes are low-context/safe (bank progress); README must reflect the *final* lesson set (in-sync pillar). |
| **SANITIZATION = section; AVALIAÇÃO = lesson; SKILLS/SYSTEM-PROMPTS = decide after grounding** | "Misto" model: standalone lesson needs its own quiz+source+mission; reinforcing content = section. |

---

## Deliverables plan (Wave 2 — "Misto")

- **SANITIZATION (req 4)** → **section in L15** (`0015-seguranca-owasp.html`): input normalization, allow-listing, untrusted-content segregation, output encoding before render/execution.
- **AVALIAÇÃO / evaluation** → **new lesson** (`0020+`). Ground HONESTLY: LLM-as-judge / eval tooling is Python-heavy — state the Java/LangChain4j gap (same ecosystem-honesty spine as L19). Then repoint L02's softened "avaliação — tema à parte" forward-pointer to it.
- **SKILLS (req 5)** → **GROUND FIRST via the `claude-api` skill** (names a Claude feature — do not author from memory). Likely spine: *Anthropic Agent Skills (real feature) vs. no direct LangChain4j-Java primitive*. Decide section-vs-lesson after grounding.
- **SYSTEM PROMPTS (req 5)** → dedicated best-practices treatment; decide section (in L06) vs. short lesson after scoping.

## Wave 3 plan (visual) — README LAST
- **Template evolution:** add an *additive* CSS block (`figure`/`figcaption`/responsive `svg`) to `0001`'s `<style>`; **propagate byte-identical to ALL lessons** (incl. new `0020+`); re-validate.
- **Capstone lesson** (append, last in Parte 5): reference architecture — colored inline SVG (cliente→API→AiService→tools/RAG→backends nacional/global→Bedrock) + security/scale/resilience views. Colors via palette vars `var(--accent)`/`--gold`/`--warn`.
- **Inline colored SVG diagrams** in architecture lessons (L04 ReAct, L05/L09 RAG pipeline, L12 compile-time DI, L14 multi-backend routing, L15 OWASP surface, L17 observability flow, L18 retry layers) + wherever the review flagged "shallow".
- **README.md** → living front matter (mission, objective, how-to-use, full curriculum index incl. Parte 5, study glossary, status). Reflect the FINAL lesson set.

---

## Technical Context — verified facts (do NOT re-derive)
- **Model ids** (vs AWS model cards): Sonnet 4.5 = `us.anthropic.claude-sonnet-4-5-20250929-v1:0`; Haiku 4.5 = `us.anthropic.claude-haiku-4-5-20251001-v1:0` (launched 2025-10-01, Active).
- **L11 `maxRetries`** = total invocation cap (`maxAttempts = maxRetries`, no `+1`; initial call validated as iteration 0); default 2 → up to 2 invocations (initial + 1 reprompt); 0→1; negative→2.
- **L13:** `ScopedValue` inherited only by `StructuredTaskScope` forks, NOT by plain `newVirtualThreadPerTaskExecutor` (which `executeToolsConcurrently()` uses) → identity via `@ToolMemoryId`.
- **L14:** `AgenticServices.sequenceBuilder()` + `@SequenceAgent` exist at tag 1.16.2; `createAgenticSystem` over bare `@Agent` methods imposes no order. Agentic module = `1.16.2-beta26` only (see `.grounding-agentic-1.16.2.md`).
- **L17:** `BedrockChatModel.builder().listeners(...)` has BOTH `List<ChatModelListener>` and varargs overloads.
- **Bedrock `CountTokens`:** `POST /model/{modelId}/count-tokens`. `seed` is NOT a Bedrock/Claude param (OpenAI-only).
- `micronaut-langchain4j 2.0.1` embeds LangChain4j **1.15.1**; OWASP = LLM Top 10 **2025**; Java 25 VT+ScopedValues final, StructuredConcurrency preview.

---

## Things to Know

### Gotchas
- **Iron Law:** validate HTML against disk; never trust a subagent's `ok:true` — re-run `scripts/validate_lessons.py` + greps yourself.
- Every lesson keeps `<style>`/`<script>` **byte-identical to `0001`**; quiz 3×3 (`data-correct` ∈ {a,b,c}, hidden `.explain`); one PRIMARY SOURCE; `.mission`; `.ask`; `.nav`; `.fine` → `../curso/modulo-NN`.
- Inside `<pre>`, escape generics `&lt;`/`&gt;` (validator flags raw `<Xxx>`).
- The validator's tag-parity check does NOT cover inline `<em>`/`<strong>` — verify those manually on prose inserts.

### Verification protocol (for new content)
Run a Workflow: one skeptic agent **per claim**, instructed to **REFUTE** against primary source (langchain4j 1.16.2 raw GitHub — NOT Maven Central, it 403s; AWS Bedrock docs; OpenJDK JEPs/javadoc; `claude-api` skill for Claude features). Distinguish **refuted** (contrary evidence → fix) from **unconfirmable** (fetch blocked → don't treat as wrong). Reference scripts persisted under the session `workflows/scripts/` dir: `verify-wave1-fixes-*.js` and `review-trilha-19-licoes-*.js`.

---

## Current State
- **Working:** 19 lessons + index validate ALL GREEN; Wave 1 fully verified; Wave 2 medium (account_scope/English-code/acronyms) done.
- **Pending:** badge-softening (L07/L08/L10/L15/L16); L05 `produto`/`idioma` residual; 4 deliverables; Wave 3 visual; README.
- **Tests:** structural validator PASS. Content (3-axis) review PASS (recorded). New-content adversarial verification: pending per deliverable.

---

## Related Resources
- Review report + Wave 1 resolution: `docs/reviews/2026-06-14-trilha-19-licoes-review.md`
- Doctrine: `CLAUDE.md` (pillars) + `.claude/rules/{lesson-authoring,content-grounding,source-drafts}.md`
- Agentic grounding: `.grounding-agentic-1.16.2.md` · Versions: `reference/` · Skill spec: `.claude/skills/teach/SKILL.md`
- Validator: `scripts/validate_lessons.py`
- Skills/tools to use: **advisor** (before structural changes), **`claude-api`** skill (ground Skills/model-ids/Claude features), **Workflow** (adversarial verify + parallel authoring).

```bash
explorer.exe "$(wslpath -w lessons/index.html)"   # open the trail (WSL2)
ls -1 lessons/ curso/ docs/reviews/ docs/handoffs/
```

---

## Open Questions
- [ ] **Checkpoint commit?** Everything is untracked. A commit after Wave 1+2-medium (durable, verified) before deliverables would be prudent — awaiting explicit user go (do not commit/push unprompted).
- [ ] SKILLS and SYSTEM-PROMPTS: section vs. lesson — resolve after grounding.
- [ ] `produto`/`idioma` JSON keys: rename to English or treat as labels?

---

_Generated after the Wave 2 medium-fix agent completed and was re-verified on disk. Resume at "Immediate Next Steps". The earlier partial handoff has been superseded by this document._
