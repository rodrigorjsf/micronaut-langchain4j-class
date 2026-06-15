# Módulo 15 — Observabilidade (ChatModelListener → OpenTelemetry GenAI → LangFuse)

> **Rascunho-fonte da Lição 17** (`lessons/0017-observabilidade.html`). Aterrado na fonte
> 1.16.2 (`ChatModelListener`, `ChatModel.chat`), nas convenções OTel GenAI e na doc LangFuse.

"Você não opera o que não enxerga." Num banco, observar custo, latência e falhas do modelo é
requisito de produção. O LangChain4j dá um **hook**; o padrão é o **OpenTelemetry GenAI**; o
destino pode ser o **LangFuse**.

## 1 · O hook: `ChatModelListener`

Interface `dev.langchain4j.model.chat.listener.ChatModelListener` (core) com **três métodos
default vazios**: `onRequest(ChatModelRequestContext)`, `onResponse(ChatModelResponseContext)`,
`onError(ChatModelErrorContext)` — implemente só o que precisar. O `attributes()` é um **Map
mutável compartilhado** entre `onRequest`→`onResponse`/`onError`: use-o para carregar span,
timestamp de início e o **txn id** da operação bancária.

**Onde dispara:** os callbacks são disparados pelo **template `ChatModel.chat()` do core**
(antes/depois do `doChat`), **não** pelo `BedrockChatModel.doChat`. O Bedrock herda esse
comportamento; `provider()` retorna `ModelProvider.AMAZON_BEDROCK`. Registre via
`BedrockChatModel.builder().listeners(...)`.

## 2 · A armadilha de latência (e a do onError)

`★ Insight ─────────────────────────────────────`
**Listeners rodam SÍNCRONOS e SEQUENCIAIS na thread chamadora.** Um export bloqueante (uma
chamada HTTP ao LangFuse) **dentro** do listener adiciona latência a **toda** chamada do modelo
— crítico em operações que movem dinheiro. Exporte **fora da thread** (ex.: OTel
`BatchSpanProcessor` / OTLP assíncrono). E mais: em 1.16.2, o `ChatModelErrorContext` **não
expõe resposta parcial** no erro (o javadoc menciona, a classe não tem) — não conte com isso.
`─────────────────────────────────────────────────`

## 3 · O padrão: OpenTelemetry GenAI

- **Provedor:** `gen_ai.provider.name = "aws.bedrock"` (atributo **Required**) — substitui o
  **deprecado** `gen_ai.system`.
- **Span:** nome `"{gen_ai.operation.name} {gen_ai.request.model}"` (ex.: `chat ...`); Required:
  `gen_ai.operation.name` + `gen_ai.provider.name`.
- **Tokens:** `gen_ai.usage.input_tokens` / `gen_ai.usage.output_tokens` (entrada inclui cache).
- **Métricas (Histogramas):** `gen_ai.client.operation.duration` (**Required**, `s`) e
  `gen_ai.client.token.usage` (**Recommended**, `{token}`) — não são "duas obrigatórias".
- **Status:** as convenções GenAI estão em **Development/experimental** (não estáveis — fixe a
  versão). Opt-in: `OTEL_SEMCONV_STABILITY_OPT_IN=gen_ai_latest_experimental`.

## 4 · LangFuse: não há SDK Java → é um backend OTel

`★ Insight ─────────────────────────────────────`
**Não existe SDK Java/JVM oficial do LangFuse** (só Python e JS/TS). Para um app
Java/Micronaut, **não procure um `langfuse-java`** — o LangFuse age como **backend
OpenTelemetry**: aponte um exporter OTLP padrão para o endpoint
`/api/public/otel` (cloud: `https://cloud.langfuse.com/api/public/otel`; self-host:
`<host>/api/public/otel`; Basic auth) e emita spans `gen_ai.*`. (LangSmith é gerenciado/Python-first —
detalhe no ecossistema, Lição 19.)
`─────────────────────────────────────────────────`

## 5 · Fiação no Micronaut

- O **micronaut-langchain4j não tem hook de observabilidade próprio**. O escape documentado é
  um bean `BeanCreatedEventListener` que customiza o builder do modelo (para chamar
  `.listeners(...)` quando o modelo vem de config). Definir o `BedrockChatModel` como `@Factory`
  e passar `.listeners(...)` é DI **padrão do Micronaut** (válido, mas não é feature documentada
  do micronaut-langchain4j).
- Métricas/tracing vêm do **Micrometer + Tracing (OTel)** do próprio Micronaut.
- Módulo opcional `langchain4j-micrometer-metrics`: `MicrometerMetricsChatModelListener(meterRegistry)`
  (um `ChatModelListener` que grava as métricas GenAI); `langchain4j-observation` faz a ponte com a
  Observation API. Ambos `@Experimental`.

## 6 · O listener do banco (esboço)

```java
public class BankObservabilityListener implements ChatModelListener {
    private static final Object KEY_TXN = "bankTxnId";
    private static final Object KEY_T0  = "startNanos";

    @Override public void onRequest(ChatModelRequestContext ctx) {
        ctx.attributes().put(KEY_T0, System.nanoTime());
        ctx.attributes().put(KEY_TXN, java.util.UUID.randomUUID().toString());
        // inicie a span OTel: gen_ai.operation.name=chat, gen_ai.provider.name=aws.bedrock
    }
    @Override public void onResponse(ChatModelResponseContext ctx) {
        long t0 = (long) ctx.attributes().get(KEY_T0);
        // grave gen_ai.client.operation.duration (s) + input/output tokens; encerre a span OK
    }
    @Override public void onError(ChatModelErrorContext ctx) {
        // ctx.error() é Throwable; SEM resposta parcial em 1.16.2. Encerre a span com erro.
    }
}
// Registro: BedrockChatModel.builder().listeners(new BankObservabilityListener())...
// EXPORTE fora da thread (BatchSpanProcessor/OTLP async) — listeners são síncronos.
```

## Quiz

1. **O que torna perigoso exportar telemetria dentro de um `ChatModelListener`?**
   (a) nada: rodam num pool assíncrono dedicado · (b) ✅ **rodam síncronos na thread chamadora**;
   bloqueio vira latência · (c) só disparam em erro
2. **Qual atributo OTel identifica o provedor numa span de Bedrock?**
   (a) `gen_ai.system = "bedrock"` (padrão atual) · (b) ✅ **`gen_ai.provider.name = "aws.bedrock"`**
   (gen_ai.system é deprecado) · (c) `aws.service = "bedrock-runtime"`
3. **Como integrar LangFuse num app Java/Micronaut?**
   (a) pela dependência oficial `langfuse-java` · (b) ✅ **não há SDK Java: exporte via OTLP** para
   `/api/public/otel` · (c) só via SDK Python num sidecar

## Vá mais fundo

- **Doc:** https://docs.langchain4j.dev/tutorials/observability/ ; OTel GenAI (repo
  `open-telemetry/semantic-conventions-genai`); LangFuse OTel (`/api/public/otel`).
- **Aberto:** corpo char-exato de `ChatModel.chat()` e coordenadas do `langchain4j-micrometer-metrics`
  alinhadas a 1.16.2 — confirmar antes de fixar dependência.
- **Próximo (Lição 18):** escala e resiliência.
