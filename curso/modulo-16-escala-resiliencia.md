# Módulo 16 — Escala e resiliência (Claude-on-Bedrock)

> **Rascunho-fonte da Lição 18** (`lessons/0018-escala-resiliencia.html`). Aterrado na fonte
> 1.16.2 (`BedrockChatModel`, `RetryUtils`, `ExceptionMapper`) + docs AWS (quotas, retry, PT).

Produção bancária = picos, throttling e falhas inevitáveis. Esta lição mostra o que o
LangChain4j+Bedrock fazem por você em resiliência — e o que **fica por sua conta**.

## 1 · Retries: duas camadas EMPILHADAS

`★ Insight ─────────────────────────────────────`
**Toda chamada atravessa DOIS retries empilhados.** (1) O do **LangChain4j**:
`BedrockChatModel.maxRetries` (default **2** → até 3 tentativas), via `withRetryMappingExceptions`
(backoff base 500ms). (2) O do **AWS SDK v2** por baixo: `retry_mode=standard`,
`max_attempts=3` — o `createClient` **não** sobrescreve a estratégia do SDK. Sob throttling
sustentado, as tentativas **multiplicam** e a latência **compõe**. (Os números do "retry 2026"
da AWS — base 1000ms, token bucket 500/14/5 — são **opt-in**, atrás de `AWS_NEW_RETRIES_2026=true`.)
`─────────────────────────────────────────────────`

O que é **retriado** (estende `RetriableException`): **429** ThrottlingException →
`RateLimitException`; **5xx** → `InternalServerException`; **408** → `TimeoutException`. O que
**falha rápido** (`NonRetriableException`): 404 (model id errado), 400 (validação), 401/403
(auth). **Streaming não tem retry no LangChain4j** (só o do SDK).

## 2 · A armadilha do timeout

`apiCallTimeout` (default 1 min) cobre **uma** chamada `converse()` (com os retries internos do
SDK) — **não** o loop externo do LangChain4j. Logo o pior caso é **~3 × 60s + backoff**, não
60s totais. Para limitar o tempo **total**, imponha o teto na **camada da app** (ou reduza
`maxRetries`).

## 3 · Capacidade: on-demand vs. cross-region vs. Provisioned Throughput

| Modo | O que é | Quando |
| --- | --- | --- |
| **On-demand** | capacidade compartilhada por Região; cota **por tokens/min (TPM)**; throttla com 429 | tráfego variável |
| **Inference profile cross-region** (`us./eu./apac./global`) | roteia entre Regiões; **cota TPM separada** | absorver picos |
| **Provisioned Throughput** | reserva **Model Units** (hora; termos no-commit/1m/6m); capacidade garantida | baseline estável (e obrigatório p/ modelo custom) |

Cotas do `bedrock-runtime` são **por modelo, por Região, por token** (input+output somados);
"dia" = TPM × 1440; **RPM é específico por modelo** (alguns, como Claude Opus, não têm RPM).
**No banco:** baseline da conta-nacional → PT; tráfego global esporádico → on-demand + perfil.

## 4 · O que o framework NÃO dá

`★ Insight ─────────────────────────────────────`
**Não há `FallbackChatModel`, `RateLimiter` nem circuit breaker no LangChain4j 1.16.2** — só a
**exceção** `RateLimitException`. Fallback (primário → alternativo: outro modelId/Região/modelo
mais barato) e rate limiting são padrões **da app/infra** (interceptor Micronaut, semáforo, API
gateway). O modo **adaptive** do AWS SDK adiciona um rate limiter client-side, mas é
**por instância de client** — num design multi-tenant de client compartilhado, ele atrasa
**todos** os tenants. Resiliência avançada é arquitetura sua.
`─────────────────────────────────────────────────`

(Auto-config do micronaut-langchain4j 2.0.1 **não** expõe `maxRetries` → mantém o default 2;
para ajustar, forneça um `BedrockRuntimeClient` próprio ou um `@Factory`. E lembre da
**assimetria de versão** da Lição 12: 2.0.1 fixa 1.15.1.)

## 5 · Idempotência sob retries empilhados (a joia)

`★ Insight ─────────────────────────────────────`
**Os retries empilhados podem REEXECUTAR uma transferência.** Uma única ação do usuário pode
disparar várias tentativas (LangChain4j × SDK). Portanto operações que movem dinheiro **têm**
de carregar **idempotency key** + **confirmação explícita**, para que um retry **nunca**
debite duas vezes (cf. Lições 12/14). Resiliência sem idempotência, num banco, é duplicar dinheiro.
`─────────────────────────────────────────────────`

```java
@Factory class BankResilienceFactory {
    @Singleton @Named("primary") BedrockChatModel primary(AwsCredentialsProvider creds) {
        return BedrockChatModel.builder().region(Region.US_EAST_1)
            .modelId("us.anthropic.claude-3-5-sonnet-20240620-v1:0") // perfil cross-region
            .maxRetries(2).timeout(Duration.ofSeconds(20)).build();
    }
    @Singleton @Named("fallback") BedrockChatModel fallback(AwsCredentialsProvider creds) {
        return BedrockChatModel.builder().region(Region.US_EAST_1)
            .modelId("us.anthropic.claude-3-haiku-20240307-v1:0")    // mais barato/rápido
            .maxRetries(1).timeout(Duration.ofSeconds(15)).build();
    }
}

ChatResponse ask(ChatRequest req) {
    try { return primary.chat(req); }
    catch (RateLimitException e) { return fallback.chat(req); }  // fallback app-level
}

TransferResult confirmTransfer(TransferCommand cmd, String idempotencyKey) {
    if (repo.alreadyExecuted(idempotencyKey)) return repo.resultFor(idempotencyKey); // sem débito duplo
    return repo.executeOnce(idempotencyKey, cmd);                // após confirmação explícita
}
```

## Quiz

1. **Quantas camadas de retry uma chamada Bedrock atravessa no LangChain4j?**
   (a) uma só (o `maxRetries` do `BedrockChatModel`) · (b) ✅ **duas, empilhadas**: a do LangChain4j
   sobre a do AWS SDK · (c) nenhuma por padrão
2. **O 1.16.2 traz classe de fallback de modelo e rate limiter?**
   (a) sim: `FallbackChatModel` e `RateLimiter` no core · (b) ✅ **não**: só a exceção
   `RateLimitException`; fallback/limite é seu · (c) sim, só no `langchain4j-bedrock`
3. **Por que uma transferência precisa de idempotency key mesmo com confirmação?**
   (a) ✅ porque os **retries empilhados** podem reexecutar a chamada · (b) porque o Bedrock cobra
   em dobro · (c) porque o virtual thread duplica a tarefa

## Vá mais fundo

- **AWS:** quotas runtime, inference profiles, Provisioned Throughput, retry behavior (sdkref).
- Fonte 1.16.2: `BedrockChatModel` (`maxRetries`), `RetryUtils`, `ExceptionMapper` (mapa 429→RateLimit).
- **Aberto:** disponibilidade atual do perfil `global`; endpoint `bedrock-mantle` (cotas separadas) — confirmar.
- **Próximo (Lição 19):** o ecossistema honesto (Java vs. Python).
