# Módulo 20 — Arquitetura de referência: o backend agêntico do banco, ponta a ponta

> **Rascunho-fonte da Lição 22** (`lessons/0022-arquitetura-referencia.html`), o **capstone**. Não
> traz API nova — **monta** o que a trilha aterrou. Cada peça aponta para a lição que a verificou;
> nada de API solta de memória. Fonte primária: Anthropic — *Building Effective Agents* (relida com
> a trilha inteira na mão).

## 1 · Macro — componentes e integrações

A requisição entra pela borda, desce pela camada agêntica e pela camada determinística de tools, e
se integra ao Bedrock, ao *core* bancário, ao RAG e à observabilidade. Camadas centrais (caminho da
requisição):

1. **Cliente** (app / web).
2. **API HTTP — Micronaut**: TLS, authN/authZ, *rate limit*, **identidade da sessão** (🔒).
3. **Camada agêntica — `AiServices` (loop ReAct)**: guardrail de entrada · *tool gating*
   (static / tool-search / skills, Lições 7 e 20) · guardrail de saída. É a parte **não-confiável**.
4. **Tools determinísticas** (🔒): auth, validação, roteamento nacional/global, idempotência,
   erro como dado.
5. **Resposta moldada ao cliente**.

Integrações (à direita): **AWS Bedrock** (Claude Sonnet 200K — chat, *prompt caching*, *tool use*);
**Vector store + Cohere via Bedrock** (RAG, embeddings multilíngues); **core bancário** (APIs de
produto); **memória durável** (estado fora da janela). Transversal: **observabilidade**
(`ChatModelListener` · OpenTelemetry GenAI → LangFuse).

## 2 · Micro — o fluxo seguro como decisões (com impacto OWASP)

Defesa em profundidade: cada *gate* é uma decisão; o caminho de falha tem um **impacto** mapeado ao
OWASP LLM Top 10 (2025, Lição 15). Regra-mestra: **o modelo propõe; a camada determinística autoriza.**

1. **Identidade pelo servidor** (🔒): *bind* do `clienteId` à sessão — o modelo nunca vê o ID.
2. **Entrada suspeita? (injeção / PII)** → se sim: **bloqueia/sanitiza** — impacto: **LLM01**
   (prompt injection) · **LLM02** (Sensitive Information Disclosure, para o PII).
3. **Loop agêntico — tool gating** (static / tool-search / skills).
4. **Ação autorizada? (regra + authZ determinística)** → se não: **nega / pede confirmação** —
   impacto: **LLM06** (excessive agency). *Este é o gate central.*
5. **Executa a tool · valida · erro como dado** (saída moldada e mínima, sem PII crua).
6. **Guardrail de saída → resposta** (reprompt/bloqueia se vazar PII) — impacto: **LLM05**.

**Insight:** todo *gate* vive na camada determinística, **fora do alcance do texto que o modelo lê**.
O loop é poderoso *porque* é cercado.

## 3 · A montagem (cada peça → lição)

| Preocupação | Onde mora | Lição |
| --- | --- | --- |
| Identidade pelo servidor | `@MemoryId` / `@ToolMemoryId` | 4, 7 |
| Design e *gating* de tools | `@Tool`, `ToolProvider`, tool-search, skills | 7, 20 |
| RAG e embeddings | `EmbeddingStore`, Cohere via Bedrock, filtro forçado | 5, 9 |
| Memória e contexto | `ChatMemory`, prompt caching, eviction *lossy* | 8, 16 |
| Saída estruturada | `record` como contrato | 10 |
| Guardrails e moderação | `Input/OutputGuardrail`; Bedrock Guardrails | 11 |
| Segurança | OWASP LLM Top 10 (2025); sanitização em camadas | 15 |
| Concorrência | *virtual threads*, *structured concurrency* | 13 |
| Observabilidade | `ChatModelListener`, OTel GenAI, LangFuse | 17 |
| Escala e resiliência | retries empilhados, throttling, fallback (DIY) | 18 |
| Avaliação | LLM-as-judge, *gate* de CI | 21 |

## 4 · Honestidade de plataforma (o que é DIY)

- **Loop agêntico**: montado com `AiServices` — **sem** *managed agents*; o Bedrock é o caminho de
  invocação do modelo, não o orquestrador (Lição 19).
- **Resiliência**: sem `FallbackChatModel` nem *rate limiter* prontos — retry/throttling/fallback são
  seus (Lição 18).
- **Guardrails**: os do LangChain4j são `@Experimental`; combine com **Bedrock Guardrails** (Lição 11).
- **Avaliação**: sem camada nativa em Java — o juiz é um *prompt* + modelo forte que você escreve
  (Lição 21).

## Fonte primária

**Anthropic — Building Effective Agents**: quando um agente se justifica, por que começar simples, e
como compor *workflows* e ferramentas com responsabilidade — a mesma referência canônica da Lição 1,
relida com a trilha inteira montada.
