# Módulo 14 — Gestão da janela de contexto em profundidade

> **Rascunho-fonte da Lição 16** (`lessons/0016-contexto-a-fundo.html`). Aterrado na fonte
> 1.16.2 (memórias, `TokenCountEstimator`, busca recursiva na árvore do repo) + AWS.

A Lição 8 deu o problema (custo N², 200K) e as duas janelas. Esta lição vai **a fundo**: o
que o 1.16.2 **de fato** entrega — e o que você **tem de construir**.

## 1 · O que o 1.16.2 realmente traz (preciso)

- `ChatMemory` (interface, **core**): `id()`, `add()`, `messages()`, `set()`, `clear()`. O
  **core não tem nenhuma implementação** de janela ou de sumarização.
- `MessageWindowChatMemory` e `TokenWindowChatMemory` vivem no **agregador `dev.langchain4j:langchain4j`**
  (pacote `dev.langchain4j.memory.chat`), **não** no core. (Dependa do agregador para tê-las.)
- `dynamicMaxTokens`/`dynamicMaxMessages` e `alwaysKeepSystemMessageFirst` **existem** em
  1.16.2 — mas **não são novos** (idênticos já em 1.15.0). Ensine "disponíveis", não "novos".

## 2 · Embutido vs. "você constrói"

| Estratégia (Lição 8) | Em 1.16.2 |
| --- | --- |
| Janela por mensagem / por token | **embutido** (Message/Token WindowChatMemory) |
| **Sumarização / compactação** | **NÃO existe** (zero `Summariz*`/`Compact*` na árvore) → **você constrói** |
| **RAG sobre o histórico** (recuperação seletiva) | **NÃO é tipo de memória** → **você compõe** (store + EmbeddingStore) |
| Enxugar resultados de tools | app-level (molde retornos pequenos — Lição 7) |

`★ Insight ─────────────────────────────────────`
**As duas memórias embutidas são janelas por RECÊNCIA — nada mais.** Não há `SummarizingChatMemory`
nem uma memória apoiada em embeddings. "Recuperar o turno **relevante**, não só o **recente**"
exige compor à mão: **persistir o histórico completo num `ChatMemoryStore`** e **indexar/recuperar**
os turnos relevantes via `EmbeddingStore` + `ContentRetriever` (Lição 9). O framework te dá as peças;
a estratégia avançada é sua.
`─────────────────────────────────────────────────`

## 3 · Orçamento de tokens no Bedrock (a peça que falta)

`TokenWindowChatMemory` **exige** um `TokenCountEstimator` (`ensureNotNull` no construtor). A
interface (core) tem 3 métodos; há **7 implementações de provedor** (OpenAi, AzureOpenAi,
GoogleAiGemini, GoogleGenAi, Anthropic, Watsonx, HuggingFace) — **nenhuma para Bedrock**.

- `BedrockChatModel` **só** implementa `ChatModel` — **sem** tokenizador Claude local.
- `AnthropicTokenCountEstimator` é **armadilha**: vive em `langchain4j-anthropic` (API **direta**
  da Anthropic), é `@Experimental`, e conta **remotamente** via `api.anthropic.com` — **não**
  serve para Bedrock.
- A AWS tem a operação remota `CountTokens` (`POST /model/{modelId}/count-tokens`, input union
  `converse|invokeModel` → `inputTokens`), **mas o langchain4j-bedrock 1.16.2 não a adapta** a um
  `TokenCountEstimator` — chame o AWS SDK direto. Contar remoto **a cada eviction** é caro.

**Conclusão:** no Bedrock você **fornece** um `TokenCountEstimator` (local/aproximado para a
janela ao vivo; o `CountTokens` da AWS para conferência ocasional). Cf. Lição 8.

## 4 · Eviction é lossy — estado durável fica FORA da janela

`★ Insight ─────────────────────────────────────`
**A janela deslizante esquece por recência — e isso é perigoso num banco.** Um detalhe citado
há muitos turnos (qual é a conta nacional vs. global; um **token de confirmação/idempotência**
emitido para uma operação que move dinheiro) pode **cair fora da janela**. **Nunca conte que ele
permanece lá.** Persista esse estado **durável** na sua aplicação/store e recupere-o à parte. A
janela é para *fluência de conversa*, não para *estado de negócio*. (Detalhe verificado: ao
evictar um `AiMessage` com `ToolExecutionRequest`, os `ToolExecutionResultMessage` órfãos saem
junto — automático, evita erro de provedor.)
`─────────────────────────────────────────────────`

## 5 · Construindo o avançado (esboço)

```java
// No Bedrock, TokenWindowChatMemory exige um TokenCountEstimator da APLICAÇÃO.
final class AppApproxTokenCountEstimator implements TokenCountEstimator {
    public int estimateTokenCountInText(String t) { return t == null ? 0 : Math.max(1, t.length()/4); }
    public int estimateTokenCountInMessage(ChatMessage m) { return estimateTokenCountInText(m.toString()); }
    public int estimateTokenCountInMessages(Iterable<ChatMessage> ms) {
        int total = 0; for (ChatMessage m : ms) total += estimateTokenCountInMessage(m); return total;
    }
}

ChatMemoryProvider memoryProvider(ChatMemoryStore durableStore, TokenCountEstimator estimator) {
    return memoryId -> TokenWindowChatMemory.builder()
            .id(memoryId)
            .maxTokens(2000, estimator)            // exige estimator no Bedrock
            .chatMemoryStore(durableStore)          // durável (NÃO InMemoryChatMemoryStore em prod)
            .alwaysKeepSystemMessageFirst(true)     // disponível em 1.16.2 (não novo)
            .build();
}
// Sumarização e RAG-sobre-histórico: construídos pela app (sumarizar quebra o cache — Lição 8).
```

## Quiz

1. **O LangChain4j 1.16.2 traz uma ChatMemory de sumarização pronta?**
   (a) sim, `SummarizingChatMemory` no core · (b) ✅ **não**: só janelas por mensagem/token; sumarização é sua ·
   (c) sim, mas só no agregador
2. **Um token de confirmação emitido há 30 turnos ainda está na janela?**
   (a) sim, a janela retém o que for importante · (b) ✅ **talvez não**: a janela é por recência e lossy —
   persista fora · (c) sim, se usar Token em vez de Message
3. **Para `TokenWindowChatMemory` no Bedrock, de onde vem a contagem de tokens?**
   (a) de um tokenizador Claude local no `BedrockChatModel` · (b) do `AnthropicTokenCountEstimator`,
   que serve direto · (c) ✅ de um `TokenCountEstimator` que **você** fornece

## Vá mais fundo

- **Doc:** https://docs.langchain4j.dev/tutorials/chat-memory · AWS CountTokens (API Reference).
- Fonte 1.16.2: `MessageWindowChatMemory`/`TokenWindowChatMemory` (agregador), `TokenCountEstimator` (core),
  ausência verificada de `Summariz*`/RAG-de-memória na árvore.
- **Próximo (Lição 17):** observabilidade (ChatModelListener → OpenTelemetry → LangFuse).
