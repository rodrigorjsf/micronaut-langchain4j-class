# Handoff: Curso `/teach` — Sistemas Agênticos com LangChain4j + Micronaut 5 + Java 25

**Created:** 2026-06-14 01:02 (-03 local; system clock UTC may differ)
**Branch:** `main` (everything untracked — nothing committed yet)
**Session Duration:** long, multi-phase (scheduled trigger → 8 teaching modules + skill retrofit)

> **NOTE:** This is a **teaching workspace**, not an app codebase. There is no build/test/dev-server. "Work" = durable learning artifacts (HTML lessons + markdown drafts + skill scaffolding). Treat the `/teach` skill at `.claude/skills/teach/SKILL.md` as the governing spec.

---

## Summary

Delivering a "basic→advanced", Foundation-First course (in **pt-BR**, code in English) on building a **production agentic banking assistant** with **LangChain4j 1.16.2 + Micronaut 5.0.x + Java 25**, targeting **Claude Sonnet (200K context window)**. Modules 1–7 are taught and persisted as both markdown drafts (`curso/*.md`) and skill-compliant HTML lessons (`lessons/*.html`, lessons 0001–0008). The `/teach` skill workspace (MISSION/GLOSSARY/RESOURCES/NOTES/learning-records/reference) was retrofitted into compliance. **Next: Module 8 / Lesson 9 — RAG in LangChain4j.**

---

## Initial Prompt

I want to learn about what the Langchain4j framework is, how to use it efficiently, best practices in large-scale distributed environments, its architecture and concepts, its main characteristics, and how to implement it properly and correctly. I also want to learn about points of attention, the major difficulties faced in the real world by this type of system, and best practices for maintaining a secure (especially in terms of prompt injection, output guardrails, and sanitization) and scalable agentic system. I want to cover best practices for defining tools, system prompts, skills, context window management (critical), and all the topics, from basic to advanced, that a software engineer with AI creating agentic applications needs to understand, know, and handle in the real world. Consider this integration with the Java Micronaut 5x framework with Java 25, always considering the use of the most modern APIs of the language and framework to provide the best results from this combination and architecture. Included in what I want to learn is the entire Langchain4j ecosystem, such as LangGraph, Deep Agents, LangServe, LangSmith Platform, LangFuse, OpenTelemetry instrumentation, and any other tool I may have forgotten but is important in the process of creating agentic systems. Always base your teachings using as an example a bank that provides a chat integration in its application where users ask any information about the products offered by the bank, and its agentic backend, through tools, retrieves the information and provides it to the agent for processing. Imagine a bank that has basically all possible financial products such as bill payment (scheduling, errors, payments, etc.), DDA, Pix, Super Statement, credit card and its invoices, purchases, shopping, financing, investments, national account (Brazil) and global account (and all the previous services available for both but with information originating from different backends) and any other product that can generate tools. Consider that I want to learn from basic to advanced concepts, and when I refer to basics I mean any concept that is necessary to understand and learn before actually starting to learn these frameworks. Apply the "Foundation First" guideline as a rule: "knowledge built on a weak foundation, no matter its size, is like a sandcastle, vulnerable and that can collapse at any moment."

## Work Completed

### Changes Made

- [x] Modules 1–7 written as detailed markdown drafts in `curso/`
- [x] Lessons 0001–0008 produced as Tufte-style HTML in `lessons/` (+ `index.html`)
- [x] 3 HTML reference docs in `reference/` (glossary, tool-api-cheatsheet, versoes)
- [x] `/teach` skill workspace created: `MISSION.md`, `GLOSSARY.md`, `RESOURCES.md`, `NOTES.md`, `learning-records/0001–0003`
- [x] Versions verified against primary sources → `curso/referencia-versoes-2026-06.md`
- [x] `@Tool` API verified byte-for-byte vs source tag 1.16.2 (Module 6 Part B)
- [x] ChatMemory + Anthropic prompt-caching verified vs 1.16.2 (Module 7 Part B)
- [x] pt-BR tokenization measured with real `tiktoken` in a venv at `/tmp/tokenv`

### Key Decisions

| Decision | Rationale | Alternatives Considered |
| --- | --- | --- |
| Target model = **Claude Sonnet, 200K window** | User confirmed explicitly | 1M tier (rejected by user) |
| Workflow grounds version-specific APIs in background; main context teaches | User instruction; keeps teaching context specialized | Inline research (pollutes context) |
| Verify every version/API in primary source before teaching | Foundation First; avoid stale/Python-vs-Java confusion | Trust parametric memory (rejected) |
| Keep `curso/*.md` as source drafts; `lessons/*.html` are canonical skill artifacts | Skill requires HTML lessons; drafts preserved | Delete drafts (rejected) |
| Detailed lessons (not the skill's "short" default) | User asked repeatedly for "Detalhado"; deviation logged in NOTES.md | Atomize into tiny lessons (rejected) |
| Gold-exemplar-first then parallel fan-out for HTML | Prevents 7 divergent styles; verified byte-identical `<style>` | Generate all in parallel cold (risky) |

---

## Files Affected (ALL untracked / uncommitted on `main`)

### Created — `/teach` skill workspace (root)
- `MISSION.md` — the "why": build a production agentic banking assistant; Sonnet 200K
- `GLOSSARY.md` — canonical pt-BR/EN terminology (fundamentos, LangChain4j, Micronaut/Java)
- `RESOURCES.md` — Knowledge + Wisdom + Gaps (official docs, source URLs, OWASP, langgraph4j)
- `NOTES.md` — learner prefs, **verified Claude facts**, documented skill deviations
- `learning-records/0001-learner-profile-and-mission.md`
- `learning-records/0002-langchain4j-not-python-and-version-reality.md`
- `learning-records/0003-modelo-alvo-claude-sonnet-200k.md`

### Created — HTML lessons (`lessons/`)
- `index.html` — trilha index (lessons 1–8 live; 9+ marked "em breve")
- `0001-modelo-mental.html` … `0008-chatmemory-contexto.html` — the gold exemplar is `0001`; all copy its `<style>`+`<script>` VERBATIM

### Created — HTML references (`reference/`)
- `glossary.html`, `tool-api-cheatsheet.html`, `versoes-2026-06.html`

### Created — markdown drafts (`curso/`)
- `README.md` (trail map), `modulo-01` … `modulo-07`, `modulo-02-aprofundamento-tokenizacao-ptbr.md`, `referencia-versoes-2026-06.md`

### Modified (this session)
- `lessons/0003-tokenizacao-ptbr.html` + `curso/modulo-02-aprofundamento-tokenizacao-ptbr.md` — appended Claude-tokenizer caveat (`tiktoken` undercounts Claude ~15–20%; pt-BR inflation is even higher; no offline Claude tokenizer → use `count_tokens`)
- `lessons/index.html` — activated Lesson 8, updated "next" pointer to Lesson 9
- `NOTES.md`, `learning-records/0003` — fixed 200K as confirmed fact (was flagged conflict)

### Read (Reference)
- `.claude/skills/teach/SKILL.md` + `*-FORMAT.md` (MISSION/RESOURCES/LEARNING-RECORD/GLOSSARY formats)
- `CLAUDE.md` (project: teacher role, pt-BR, Foundation First)

---

## Technical Context

### Verified facts to carry forward (DO NOT re-derive from memory)
- **Versions:** LangChain4j **1.16.2** (JDK min 17; use `langchain4j-bom`); Micronaut **5.0.0 GA 2026-05-20** (Java 25 baseline); `micronaut-langchain4j` **2.0.1** (compile-time DI); Java **25 LTS**.
- **Java 25 Loom:** Virtual Threads + Scoped Values **FINAL**; **Structured Concurrency still PREVIEW (JEP 505)** — do NOT teach as GA.
- **LangChain4j is NOT a Python port** (official docs, verbatim). Ecosystem maps differently (langgraph4j = community).
- **Claude Sonnet:** model `claude-sonnet-4-6`; **200K window / 64K max output**; **no offline tokenizer** (use `count_tokens` API); `tiktoken` undercounts Claude ~15–20%.
- **Prompt caching (Claude):** read ~0.1×, write 1.25× (5min)/2× (1h), min 2048 tokens on Sonnet 4.6; prefix-match (order tools→system→messages).
- **`langchain4j-anthropic` caching:** `AnthropicChatModel.builder().cacheSystemMessages(true)` / `.cacheTools(true)` (NOT @Experimental); observe via `AnthropicTokenUsage.cacheReadInputTokens()`. Caveats: cacheTools can blow the 4-block max (issue #3051).
- **`@Tool` gotchas:** `@Tool.value()` is the DESCRIPTION (`String[]`), name is `@Tool.name()`; every `@P` required by default; 1.x silent-null for missing required OBJECT args; defaults change in 2.0.
- **ChatMemory:** `TokenWindowChatMemory.withMaxTokens(int, TokenCountEstimator)` preferred for 200K; SystemMessage pinned/never-evicted; orphan tool results auto-evicted; `AiServices` retains every memory → extend `ChatMemoryAccess` + call `evictChatMemory()` (also serves LGPD); `AnthropicTokenCountEstimator` is REMOTE+@Experimental → don't use in live window.

### Dependencies / tooling
- Python venv with `tiktoken 0.13.0` at **`/tmp/tokenv`** (ephemeral — `/tmp`; recreate if gone: `python3 -m venv /tmp/tokenv && /tmp/tokenv/bin/pip install tiktoken`)
- HTML validator is an inline Python `HTMLParser` snippet (see Commands)

### Process pattern (user-mandated, keep using)
1. `Workflow` (background) grounds version-specific API vs primary source (tag 1.16.2 raw GitHub).
2. Main context teaches the version-agnostic part meanwhile.
3. On return: read full output, write Part B, generate HTML lesson, **validate vs disk**, update index.

---

## Things to Know

### Gotchas & Pitfalls
- **`ce-web-researcher` agentType is NOT valid in workflows** → use `general-purpose` (it has web tools). First grounding workflow failed because of `ce-web-researcher`; later ones used `general-purpose`.
- **Workflow synth agents can hallucinate confident output from empty findings** — always read the full persisted output and trust source-pinned (1.16.2) facts over loose docs paraphrase.
- **Iron law:** validate HTML against disk (the inline parser), never trust subagents' `ok:true`.
- Each lesson MUST keep: `.mission` banner, 3-question quiz (3 options each, length-balanced, `data-correct`+hidden `.explain`), one primary-source recommendation, `.nav` (prev/next/GLOSSARY), `.ask` "pergunte ao professor", `.fine` rascunho-fonte link, and `<style>`+`<script>` byte-identical to `0001`.

### Assumptions
- The course continues in pt-BR chat; durable artifacts in English (per global CLAUDE.md).
- Learner is an experienced Java/backend engineer (LR-0001) — don't re-teach Java basics.

### Known Issues / Open verification debt (for Module 10, Micronaut)
- Exact LangChain4j version **embedded in** `micronaut-langchain4j 2.0.1` (hint: ~1.14.x, behind standalone 1.16.2) — confirm in POM.
- Exact name of LangChain4j **agentic module** (`langchain4j-agentic` / `AgenticServices`) — confirm at Modules 12/17.
- `@P` parameter-name preservation under Micronaut compile-time DI (needs `-parameters`? or `@P(name=...)`) — confirm at Module 10.

---

## Current State

### What's Working
- Lessons 0001–0008 + index + 3 references: **all validated 0 structural errors, 3×3 quizzes, byte-identical CSS** (last full validation passed).
- Skill workspace structurally compliant with `SKILL.md`.

### What's Not Working / Pending
- Module 8+ not started. No git commits. No README at repo root tying it together (optional).

### Tests
- [x] HTML structural validation: PASS (10 artifacts + lesson 0008)
- [ ] Unit/integration tests: N/A (teaching workspace, no code project)
- [x] Manual: tokenization measured live with tiktoken

---

## Next Steps

### Immediate (Start Here)
1. **Teach Module 8 / Lesson 9 — RAG in LangChain4j.** Use the process pattern: launch a background `Workflow` (agentType `general-purpose`) to ground, vs tag **1.16.2**, the exact API: `EmbeddingModel`, `EmbeddingStore`, `EmbeddingStoreContentRetriever`, `ContentRetriever`, `RetrievalAugmentor` (+ `DefaultRetrievalAugmentor`), `EmbeddingStoreIngestor`, document splitters, and **metadata filtering** (`Filter`/`MetadataFilterBuilder`) — the key to nacional-vs-global separation from Module 4. Also confirm pgvector/other store modules and whether an Anthropic-compatible embedding path exists. Meanwhile teach the version-agnostic RAG-in-practice part (Module 4 → wiring).
2. On return: append **Part B** to a new `curso/modulo-08-rag-langchain4j.md`, then generate **`lessons/0009-rag-langchain4j.html`** (copy `<style>`+`<script>` from `0001` verbatim), validate vs disk, and activate it in `lessons/index.html` (move the "future" item, update footer "next").
3. Keep teaching in pt-BR with `★ Insight` blocks; anchor every example in the bank (conta nacional vs global from different backends).

### Subsequent (remaining trail — see `curso/README.md`)
- M9 structured output + guardrails + content moderation; M10 Micronaut 5 integration (+ resolve the 3 verification-debt items); M11 Java 25 concurrency for parallel tool calls; M12 multi-backend bank architecture (idempotency, confirmation, human-in-the-loop); M13 security (prompt injection, OWASP LLM Top 10); M14 context-window deep dive; M15 observability (OTel/LangFuse); M16 scale/resilience; M17 honest ecosystem.
- Optional: offer `dreamer` subagent for project-memory consolidation (per global CLAUDE.md) after this big session.

### Blocked On
- Nothing. User is responsive; last user message was "Sim" (proceed to Module 8).

---

## Related Resources

### Documentation
- Skill spec: `.claude/skills/teach/SKILL.md`
- Trail map: `curso/README.md` ; versions: `curso/referencia-versoes-2026-06.md`
- LangChain4j docs: https://docs.langchain4j.dev/ ; source tag: https://github.com/langchain4j/langchain4j/tree/1.16.2
- Anthropic prompt caching: https://platform.claude.com/docs/en/build-with-claude/prompt-caching

### Commands to Run
```bash
# Recreate tiktoken venv if /tmp was cleared
python3 -m venv /tmp/tokenv && /tmp/tokenv/bin/pip install tiktoken

# Validate all HTML lessons/refs against the gold exemplar (style + quiz + structure)
# (inline Python HTMLParser — see prior session; checks errs==0, .q==3, .opt==9, style==0001)

# Inventory the teaching workspace
ls -1 curso/ lessons/ reference/ learning-records/

# Open the trail in a browser (WSL2)
explorer.exe "$(wslpath -w lessons/index.html)"
```

### Search Queries
- `grep -rl "cacheSystemMessages" curso/` — finds the prompt-caching teaching
- `grep -n "★" curso/modulo-0*.md` — finds all insight blocks
- `grep -rn "200K\|200_000\|count_tokens" curso/ NOTES.md` — finds Claude/context facts

---

## Open Questions
- [ ] Does the user want a root `README.md` + a single git commit checkpoint of the course so far? (Currently everything is untracked.)
- [ ] Confirm the embedding model/store the bank will use (affects Module 8 concreteness) — or keep it vendor-neutral.

---

## Session Notes
- Originated from a **scheduled trigger** (the user agendou `/teach` para +2h12); the agent initially taught directly in `curso/*.md` before invoking the `/teach` skill, then **retrofitted** into skill compliance at the user's request — that retrofit is DONE.
- A background grounding `Workflow` for Module 8 was **NOT** launched yet — the very next action should launch it.
- Communication: pt-BR to user, English artifacts. Explanatory style (`★ Insight` blocks). Foundation First is a delivery constraint, not just a preamble.

---

_This handoff was generated to checkpoint the course. Start a new session, read this + `.claude/skills/teach/SKILL.md` + `MISSION.md` + `NOTES.md`, then execute "Immediate Next Steps"._
