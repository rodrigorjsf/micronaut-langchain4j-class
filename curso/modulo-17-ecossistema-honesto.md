# Módulo 17 — O ecossistema honesto: Java vs. Python

> **Rascunho-fonte da Lição 19** (`lessons/0019-ecossistema-honesto.html`). Aterrado em Maven
> Central + GitHub (releases, contribuidores) + docs oficiais. Contagens de stars são ordem de
> grandeza (variam diariamente).

A lição de fechamento: separar **o que existe de verdade em Java** do que é **só Python** — sem
hype. Num banco, escolher dependência por **maturidade + bus-factor**, não por moda.

## 1 · O mapa honesto

| Peça | Realidade em Java | Recomendação p/ o banco |
| --- | --- | --- |
| **LangChain4j** | **GA** (1.16.x) | base do curso |
| **langchain4j-agentic** | **oficial, mas só BETA** (1.16.2-beta26) | use, com pin de versão; espere quebras |
| **LangGraph** | **só Python** (~34.7k★); Java = `langgraph4j` **comunitário** | prefira o agentic oficial |
| **langgraph4j** | comunitário, ~1.7k★, **single-maintainer** | vendor/fork se adotar |
| **Deep Agents** | **só Python** (~24.6k★); `langgraph4j-deepagents` embrionário (31★) | não dependa em produção |
| **LangServe** | **ARQUIVADO** (até em Python); sem Java | sirva via Micronaut/Spring |
| **LangSmith** | `langsmith-java` **beta** (0.1.0-beta.7) | use **OTel** |
| **LangFuse** | **sem SDK Java** (só Python/JS); `langfuse-java` é só client de API | use **OTel** |
| **Spring AI** | **GA** (v2.0.0) | par Java alternativo ao LangChain4j |

## 2 · Orquestração: oficial-beta vs. comunitário

`★ Insight ─────────────────────────────────────`
**"Oficial" ≠ "GA"; "popular em Python" ≠ "disponível em Java".** O `langchain4j-agentic` é
**oficial** (mantido pelo time) mas **só existe em beta** — pin a versão e espere quebras. O
`langgraph4j` é **comunitário** (org `langgraph4j`, não `langchain-ai`) e **efetivamente de um
mantenedor** (top contribuidor 3431 commits vs. 13 do segundo) — **risco de bus-factor** para um
sistema bancário. Prefira o agentic oficial; se adotar o langgraph4j por um recurso específico,
**faça vendor/fork-mirror**. Ambos são **model-agnostic** → o `BedrockChatModel` (que `implements
ChatModel`) pluga direto.
`─────────────────────────────────────────────────`

## 3 · Serving: o "LangServe do Java" não existe

`LangServe` está **arquivado** (até em Python) e **não tem equivalente Java**. Sirva o app
LangChain4j com **controllers do Micronaut** (ou Spring) — você já tem um framework HTTP de
primeira classe; não precisa de uma camada estilo LangServe.

## 4 · Observabilidade: OTel é o caminho (recap da Lição 17)

`★ Insight ─────────────────────────────────────`
**Nem LangFuse nem LangSmith têm SDK Java de produção.** LangFuse **não tem SDK Java** algum
(o `langfuse-java` é um *client de API auto-gerado*, não instrumenta a app); o `langsmith-java`
está **só em beta**. O caminho de produção, vendor-neutral e **auditável**, é o
**OpenTelemetry/OTLP** — ambos ingerem OTLP (LangFuse em `/api/public/otel`; LangSmith em
`api.smith.langchain.com/otel`), e o Micronaut tem OTel nativo. Para um banco que precisa rastrear
operações que movem dinheiro, OTel > SDK beta de vendor.
`─────────────────────────────────────────────────`

## 5 · O outro framework Java: Spring AI (GA)

`spring-projects/spring-ai` é **GA** (v2.0.0, Apache-2.0) — um **par/alternativa** ao LangChain4j
no espaço de AI-engineering em Java. Saber que existe (e que é GA) é honestidade de ecossistema;
a escolha entre os dois é de stack/time, não de capacidade.

## 6 · O esboço (orquestração oficial + Bedrock + OTel)

```java
// dev.langchain4j:langchain4j-agentic:1.16.2-beta26 (BETA → pin)  + langchain4j-bedrock
ChatModel bedrock = BedrockChatModel.builder()
        .modelId("us.anthropic.claude-sonnet-4-5-20250929-v1:0").region(Region.US_EAST_1).build();

interface AccountAssistant {
    @UserMessage("Resolva: {{request}}")
    String handle(@V("request") String request);
}
AccountAssistant a = AgenticServices.agentBuilder(AccountAssistant.class)
        .chatModel(bedrock)          // model-agnostic → Bedrock pluga aqui
        .build();
// Observabilidade: exporte via OTel/OTLP para LangFuse/LangSmith (sem SDK Java de produção).
```

## Quiz

1. **O `langgraph4j` é o LangGraph oficial para Java?**
   (a) sim, mantido pelo time langchain-ai · (b) ✅ **não**: porta comunitária, efetivamente de um
   mantenedor · (c) sim, é o módulo agêntico oficial do LangChain4j
2. **Como servir um app LangChain4j em HTTP (o "LangServe do Java")?**
   (a) pelo LangServe oficial portado · (b) ✅ por **controllers do Micronaut (ou Spring)** —
   LangServe está arquivado · (c) por um sidecar Python LangServe
3. **Caminho de produção para traços em LangFuse/LangSmith em Java?**
   (a) os SDKs Java GA oficiais de cada plataforma · (b) ✅ **OpenTelemetry/OTLP** — não há SDK
   Java de produção · (c) o `langfuse-java`, que instrumenta a app

## Vá mais fundo

- **Fontes:** Maven Central (`langchain4j-agentic`, `langsmith-java`), GitHub (`langgraph4j`,
  `langchain-ai/langgraph`, `langserve`, `spring-ai`), docs LangFuse/LangSmith OTel.
- **Fim da trilha base.** Próximo passo prático: montar o projeto Micronaut do banco unindo as 19
  lições (Bedrock + tools + RAG + memória + guardrails + segurança + observabilidade + resiliência).
