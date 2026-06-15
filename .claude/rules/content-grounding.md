---
paths:
  - "lessons/**/*.html"
  - "lessons/index.html"
  - "curso/**/*.md"
---

# Content grounding & language (lessons + source drafts)

Cross-cutting doctrine for every learner-facing or draft content file. One home for the facts that the trail review caught regressing.

## pt-BR prose / English code split

Teaching prose is pt-BR. ALL code is English — identifiers, JSON keys, code comments (`//`, `#`), YAML keys. ONLY model-facing string literals (`@Tool` / `@P` / `@SystemMessage` values) may be pt-BR. (Review found pt-BR JSON keys `tipoConta/versao/vigencia` and pt-BR Java/YAML comments — those are code, must be English.)

## Acronym expansion (Foundation First)

Every acronym or technical term is expanded on first use with its pt-BR meaning. (Review caught ReAct, RAG, PII, IAM, SPI, GA used raw.)

## Grounding discipline — verify before teaching

Technical claims — API signatures, version numbers, model ids, "X does not exist" assertions — MUST be verified verbatim against PRIMARY SOURCE before they enter content (adversarial pass): langchain4j 1.16.2 raw source, AWS Bedrock docs, OWASP raw GitHub, OpenJDK JEPs, Maven Central. Code in lessons MUST compile/run against the pinned stack. Distinguish "verified" from "could not confirm" — soften or cite the latter, never badge it as verified. (Review found a broken-code cluster and grounding falsehoods: tiktoken folklore, Titan "in preview", `maxRetries` "total attempts", `seed` as Bedrock-controllable.)

## Platform directive — Bedrock, not direct Anthropic

The bank invokes Claude via AWS Bedrock (`BedrockChatModel`), NOT the direct Anthropic SDK. All chat / embeddings / prompt-caching examples come from Bedrock + `langchain4j-bedrock`. The few Anthropic-SDK surfaces that appear are framed as TRAPS, never as the bank's path.

## Version truths — point, never inline

Do NOT hardcode versions, model ids, or capability-enum values into content prose as facts to memorize — they go stale and re-introduce drift. Verify each against, and cite, the single in-repo sources of truth:
- `reference/versoes-2026-06.html` — learner-facing verified version table (LangChain4j core, the `micronaut-langchain4j` embedded-vs-standalone gap, Java 25 Loom status).
- `.grounding-agentic-1.16.2.md` — verified `langchain4j-agentic` notes (its beta coordinate, `AgenticServices` entry points, HITL is built-in).
