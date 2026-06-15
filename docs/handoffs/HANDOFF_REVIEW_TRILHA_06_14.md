# Handoff: Re-executar a revisão da trilha (19 lições) interrompida pelo limite de sessão

**Created:** 2026-06-14 (~13:xx America/Fortaleza, UTC-3)
**Branch:** `main` (tudo untracked — nada commitado nesta sessão)
**Session:** longa — entregou Lições 9–19 + retrofit da 8 + diretriz Bedrock; terminou ao lançar a revisão, que **falhou no limite de sessão**.

> **NOTE:** workspace de ensino (`/teach`), não app. "Trabalho" = artefatos de aprendizado (HTML em `lessons/`, rascunhos em `curso/`, mais MISSION/NOTES/RESOURCES/learning-records). A skill `/teach` em `.claude/skills/teach/SKILL.md` é a spec.

---

## Summary

A **trilha base está COMPLETA: 19 lições** (`lessons/0001`–`0019`), todas validadas (style/script byte-idênticos ao `0001`, quiz 3×3, HTML balanceado), índice reestruturado em Partes 0–4. O usuário pediu, ao fechar a trilha, um **Workflow de revisão** das 19 lições (3 eixos: aderência ao prompt inicial / embasamento na fonte / profundidade). Ele foi lançado (`review-trilha-19-licoes`, task `w10fu6c4s`) mas **TODOS os 20 agentes falharam com "session limit · resets 5pm (America/Fortaleza)"** — resultado `null`, nenhum scorecard. **Próximo passo: re-executar a revisão após o reset (17h Fortaleza / 20:00 UTC).**

---

## Work Completed (esta sessão)

- [x] **Diretriz Bedrock** fixada (MISSION/NOTES/RESOURCES + `learning-records/0004-integracao-via-aws-bedrock.md`): banco invoca Claude **via AWS Bedrock** (`BedrockChatModel`), não a SDK direta.
- [x] **Lição 9** RAG no LangChain4j sobre Bedrock (`0009` + `curso/modulo-08`).
- [x] **Lição 10** Saída estruturada (`0010` + `curso/modulo-09`).
- [x] **Lição 11** Guardrails + moderação (`0011` + `curso/modulo-09b`).
- [x] **Retrofit da Lição 8** (`0008` + `curso/modulo-07`): `AnthropicChatModel.cacheSystemMessages` → `BedrockChatModel` + `promptCaching(cachePoint)`; dívida marcada RESOLVIDA em NOTES.
- [x] **Lições 12–19** (`0012`–`0019` + `curso/modulo-10`..`17`): Micronaut, Java 25, multi-backend agêntica, OWASP, contexto a fundo, observabilidade, escala, ecossistema.
- [x] **Índice** (`lessons/index.html`) reestruturado (Partes 0–4, 19 lições, sem placeholder; rodapé "trilha base completa").
- [x] **Suite revalidada: ALL GREEN** (19 lições + índice).
- [x] **Memória de projeto** consolidada por `dreamer` (3 arquivos em `memory/` + MEMORY.md): diretriz Bedrock, padrão de aterramento, armadilhas da API 1.16.2.
- [ ] **Revisão das 19 lições** — LANÇADA mas FALHOU (limite de sessão). **PENDENTE.**

### Key Decisions

| Decisão | Rationale |
| --- | --- |
| Aterrar Lições 12–19 num **único Workflow de 8 clusters** antes de escrever | "verificar antes de ensinar"; 1 run em background grounda tudo |
| **Dividir** Módulo 9 em Lição 10 (saída estruturada) + 11 (guardrails) | co-iguais num banco; ponte "tipado mas não-confiável" → "defenda-o" |
| Ensinar a **verdade de versão** (2.0.1→1.15.1; agentic só beta26) | Foundation First; honestidade de ecossistema |
| Revisão = **auditoria** (confronta o escrito vs critérios), não nova pesquisa | os 3 eixos do usuário |

---

## ⭐ IMMEDIATE NEXT STEP — re-executar a revisão

O script da revisão está **persistido** (sobrevive ao reset):

```
/home/rodrigo/.claude/projects/-home-rodrigo-Workspace-micronaut-langchain4j-class/052774ee-97db-46ce-971d-0bc88275d95f/workflows/scripts/review-trilha-19-licoes-wf_fcbd2629-5b9.js
```

**Após o reset (17h America/Fortaleza ≈ 20:00 UTC), re-invocar via `scriptPath`:**

```
Workflow({ scriptPath: "/home/rodrigo/.claude/projects/-home-rodrigo-Workspace-micronaut-langchain4j-class/052774ee-97db-46ce-971d-0bc88275d95f/workflows/scripts/review-trilha-19-licoes-wf_fcbd2629-5b9.js" })
```

- **NÃO** usar `resumeFromRunId` — todos os agentes falharam (zero cache útil); um run novo é mais simples.
- O Workflow **lê os 19 HTML do disco** (`lessons/00NN-*.html`) e faz WebFetch das fontes — **não depende de `/tmp`**.
- Estrutura: 19 revisores em paralelo (`agentType general-purpose`, schema `SCORECARD_SCHEMA`) → 1 sintetizador (`REPORT_SCHEMA`). Eixos: **aderência ao prompt inicial** (matriz de cobertura 1–10), **embasamento** (spot-check adversarial de claims vs fonte primária), **profundidade**, + pedagogia + consistência Bedrock.
- Se o limite ainda morder, **reduzir concorrência/escopo**: rodar a revisão em 2 lotes (ex.: L01–L10, depois L11–L19) editando o array `LESSONS` no script, ou revisar só as 11 lições novas/retrofitadas desta sessão (L08–L19) primeiro.

**Ao concluir:** ler o output (`/tmp/.../tasks/<taskid>.output`, campo `result`), trazer ao usuário **veredito + matriz de cobertura + `prioritizedFixes`**, e **só então** aplicar correções (ordem do usuário: "depois nós vemos questões de revisão").

---

## Files Affected

### Created (lições HTML — `lessons/`)
`0009-rag-langchain4j.html`, `0010-saida-estruturada.html`, `0011-guardrails-moderacao.html`, `0012-micronaut-integracao.html`, `0013-java25-concorrencia.html`, `0014-arquitetura-multibackend.html`, `0015-seguranca-owasp.html`, `0016-contexto-a-fundo.html`, `0017-observabilidade.html`, `0018-escala-resiliencia.html`, `0019-ecossistema-honesto.html`

### Created (rascunhos — `curso/`)
`modulo-08-rag-langchain4j.md`, `modulo-09-saida-estruturada.md`, `modulo-09b-guardrails-moderacao.md`, `modulo-10-micronaut-integracao.md`, `modulo-11-java25-concorrencia.md`, `modulo-12-arquitetura-multibackend.md`, `modulo-13-seguranca-owasp.md`, `modulo-14-contexto-a-fundo.md`, `modulo-15-observabilidade.md`, `modulo-16-escala-resiliencia.md`, `modulo-17-ecossistema-honesto.md`

### Created (outros)
`learning-records/0004-integracao-via-aws-bedrock.md`

### Modified
- `lessons/0008-chatmemory-contexto.html` + `curso/modulo-07-chatmemory-contexto.md` — retrofit Bedrock (caching/token-count).
- `lessons/index.html` — Partes 0–4, 19 lições ativas, missão cita Bedrock.
- `MISSION.md`, `NOTES.md`, `RESOURCES.md` — diretriz Bedrock; NOTES também tem "Estado da trilha" + pendência da revisão.

---

## Technical Context — fatos verificados (NÃO re-derivar)

- **`micronaut-langchain4j 2.0.1` → LangChain4j 1.15.1** (Micronaut 5.0.1), NÃO 1.16.2. Para 1.16.2, sobrescrever o `langchain4j-bom`.
- **`langchain4j-agentic` só existe como `1.16.2-beta26`** (assimetria: `langchain4j-bedrock` é 1.16.2 puro).
- **Bedrock chat:** `BedrockChatModel implements ChatModel`; embedding pt-BR = `BedrockCohereEmbeddingModel`+`cohere.embed-multilingual-v3` (2 instâncias: SEARCH_DOCUMENT/SEARCH_QUERY); caching = `BedrockChatRequestParameters.promptCaching(BedrockCachePointPlacement.AFTER_SYSTEM, CacheTTL.VALUE_5_M)`; model id = inference profile `us.anthropic.claude-sonnet-4-5-20250929-v1:0`.
- **Java 25:** Virtual Threads final (JEP 444, desde 21); Scoped Values final (JEP 506); Structured Concurrency **ainda preview** (JEP 505). LangChain4j tools são **sequenciais por padrão** (`executeToolsConcurrently()` opt-in; executor default = virtual-thread-per-task).
- **OWASP LLM Top 10 = edição 2025 (v2.0)**; "2026" é o ASI/Agentic Top 10 (projeto separado). Novos em 2025: LLM07 System Prompt Leakage, LLM08 Vector/Embedding Weaknesses.
- **Guardrails LangChain4j são `@Experimental`** em 1.16.2; `reprompt/retry` são métodos **default da interface** `OutputGuardrail` (não estáticos). Bedrock Guardrails = `BedrockGuardrailConfiguration` (guardrailIdentifier/guardrailVersion/streamProcessingMode).
- **Sem sumarização nem RAG-de-histórico embutidos**; **sem `ModerationModel` Bedrock**; **sem SDK Java do LangFuse** (use OTel); `gen_ai.provider.name="aws.bedrock"`.
- **Escala:** `maxRetries` default 2 (sync-only) **empilha** sobre o retry do AWS SDK (max_attempts=3); sem `FallbackChatModel`/rate limiter no framework.

---

## Things to Know

### Gotchas
- **Iron law:** validar HTML contra disco; nunca confiar em `ok:true` de subagente.
- Cada lição mantém: `.mission`, quiz 3×3 (data-correct + `.explain` oculto), 1 fonte primária, `.nav` (prev/index/glossary), `.ask`, `.fine` rascunho-fonte, e `<style>`+`<script>` **byte-idênticos ao `0001`**.
- `/tmp/lg/L12.json`..`L19.json` (aterramento) e `/tmp/validate_lesson.py` são **efêmeros** — provavelmente perdidos pós-reset. **Não são necessários** para a revisão (que lê os HTML do disco). Para aplicar fixes, as fontes verificadas estão em cada lição ("Vá mais fundo") e nos `curso/*.md`.
- Workflow: TypeScript não parseia (sem generics/anotações de tipo fora de string); cuidado com balanceamento de parênteses (o 1º lançamento da revisão falhou por 1 `)` a menos).

### Re-criar o validador (se `/tmp` foi limpo)
Validador Python por lição: parse HTMLParser (balanceamento), conta `.q`==3 / `.opt`==9 / `.explain`==3, `data-correct` ∈ {a,b,c}, e `<style>`/`<script>` byte-idênticos a `lessons/0001-modelo-mental.html`, + checagens de scaffold (`.mission`, `Fonte primária recomendada`, `../curso/modulo-\d\d`, link de lição prev, `index.html`, `GLOSSARY.md`) e ausência de genéricos crus (`<[A-Z]\w*>`) em `<pre>`. Rodar a varredura da suite sobre `lessons/0*.html`.

---

## Current State

### Working
- 19 lições + índice: validados ALL GREEN (última varredura desta sessão).
- Diretriz Bedrock aplicada e consistente; memória de projeto consolidada.

### Not working / pending
- **Revisão das 19 lições não rodou** (limite de sessão). Re-executar (ver Immediate Next Step).
- Nenhum commit git (tudo untracked).

### Tests
- [x] Validação estrutural HTML: PASS (19 lições + índice)
- [ ] Revisão de conteúdo (3 eixos): **PENDENTE** (workflow a re-rodar)

---

## Next Steps

### Immediate
1. Após reset (17h Fortaleza), **re-invocar a revisão** via `scriptPath` (comando acima). Se falhar, rodar em lotes (L08–L19 primeiro).
2. Ler `result` do output; sintetizar veredito + matriz de cobertura + `prioritizedFixes` ao usuário.
3. Triar fixes com o usuário; aplicar; **re-validar a suite**.

### Subsequent
- Atualizar `curso/README.md` (ainda mostra 🔒 nos módulos) e talvez `reference/versoes-2026-06.html` (refletir 1.15.1 sob Micronaut, agentic beta26, OWASP 2025).
- Oferecer o esqueleto do projeto Micronaut do banco unindo as 19 lições.
- Rodar `dreamer` para consolidar as correções de versão (2.0.1→1.15.1, agentic beta26) na memória.

### Blocked On
- **Limite de sessão** até 17h America/Fortaleza (≈20:00 UTC). Só isso.

---

## Related Resources

- Skill: `.claude/skills/teach/SKILL.md` · Trilha: `curso/README.md` · Versões: `curso/referencia-versoes-2026-06.md`
- Script da revisão: `…/workflows/scripts/review-trilha-19-licoes-wf_fcbd2629-5b9.js`
- Outputs de aterramento (efêmeros): `/tmp/claude-1000/-home-rodrigo-Workspace-micronaut-langchain4j-class/64b2a56b-…/tasks/{w0fxd3j4u,wjzd2sh9y,waoqdvr7x}.output`

### Commands
```bash
# Abrir a trilha (WSL2)
explorer.exe "$(wslpath -w lessons/index.html)"
# Inventário
ls -1 lessons/ curso/ learning-records/
```

---

## Open Questions
- [ ] Sobrescrever o `langchain4j-bom` para 1.16.2 sob micronaut-langchain4j 2.0.1 é viável? Quais deltas vs 1.15.1?
- [ ] O stack (Micronaut 5.0.1 / LC 1.15.1 / agentic beta26) compila/roda sob **Java 25**? (toolchain não verificada.)
- [ ] Usuário quer um `README.md` na raiz + 1 commit de checkpoint? (Tudo untracked.)

---

_Gerado ao fim de uma sessão interrompida pelo limite. Em nova sessão: leia este doc + `NOTES.md` ("Estado da trilha") e execute "Immediate Next Step" — re-rodar a revisão._
