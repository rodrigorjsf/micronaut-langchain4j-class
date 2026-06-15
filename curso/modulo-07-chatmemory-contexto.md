# Módulo 7 — ChatMemory e Gestão da Janela de Contexto (o tema crítico)

> **Parte 2.** Duas metades: **Parte A — estratégia** (conceitual, ancorada nos fatos verificados do Claude Sonnet 200K — esta seção) e **Parte B — a API de `ChatMemory` do LangChain4j** (aterrada por Workflow). Este é, junto do Módulo 3, o módulo que mais decide se o seu assistente bancário é **viável em produção** ou queima dinheiro.

---

# Parte A — Estratégia de gestão de contexto

## 7A.1 O problema, consolidado

Junte três fatos que já provamos:
1. O modelo é **sem estado** (Módulo 1): para "lembrar", **reenviamos o histórico** a cada turno.
2. Isso faz o custo de uma conversa crescer **~N²** (Módulo 2): o turno N reenvia ~N mensagens.
3. A janela é **finita**: **200K tokens** no Sonnet do banco (compartilhados entre entrada e saída; saída até 64K).

A "mesa de trabalho" (Módulo 1.5) tem tamanho fixo, enche, e cada token reenviado **custa**. Gerir a janela **é** gerir custo, latência e qualidade ao mesmo tempo.

## 7A.2 O orçamento de 200K: quem disputa a janela

| Componente | Tamanho típico (ilustrativo) | Natureza |
|---|---|---|
| System prompt + **descrições de dezenas de tools** (todos os produtos) | ~6.000 | **Fixo** (reenviado todo turno) |
| RAG: regras de produto recuperadas | ~3.000 | Por pergunta |
| Histórico da conversa | ~10.000 **e crescendo** | Acumula (N²) |
| Resultado de tools recente (extrato, fatura) | ~1.500 cada — **podem ser enormes** | Por chamada |
| **Reservado para a saída** | até 64K (resposta típica ~500) | Disputa o mesmo orçamento |

`★ Insight ─────────────────────────────────────`
**Caber em 200K quase nunca é o problema — o custo é.** Um turno típico do banco usa ~20K de 200K: sobra espaço. A dor não é estourar a janela; é que **aquele bloco fixo de ~6K (system + tools) é reenviado a cada turno**, e o histórico cresce em N². Multiplicado por milhões de turnos/dia em pt-BR (que ainda infla os tokens — Módulo 2), isso é a maior conta recorrente do sistema. Gestão de contexto, num banco, é primariamente **engenharia de custo**, não de "fazer caber".
`─────────────────────────────────────────────────`

## 7A.3 O menu de estratégias

| Estratégia | O que faz | Custo/benefício |
|---|---|---|
| **Janela de mensagens** | Mantém as últimas **N mensagens**; descarta as mais antigas | Simples; pode cortar contexto relevante no meio de uma tarefa |
| **Janela de tokens** | Mantém os últimos **N tokens** | Controla o orçamento com precisão; precisa contar tokens (cuidado no Claude — 7A.4) |
| **Sumarização / compactação** | Substitui turnos antigos por um **resumo** | Preserva o "sentido" do passado gastando menos tokens; **mas reescreve o histórico** (ver 7A.5) |
| **RAG sobre o histórico** | Guarda a conversa inteira **fora** da janela e **recupera** só os trechos relevantes | Escala para conversas longuíssimas; adiciona a complexidade do RAG (Módulo 4) |
| **Enxugar resultados de tools** | Expira/encurta saídas de tools antigas (extrato de 3 turnos atrás) | Ataca os **maiores** consumidores da janela |
| **Memória por cliente** | Isola a "mesa" de cada cliente (`@MemoryId`, Módulos 5/6) | Correção e privacidade; cada cliente tem seu próprio custo N² para gerir |

## 7A.4 Prompt caching: a alavanca direta contra o N²

Aqui entra o fato mais valioso que verificamos do Claude (via `claude-api`):

> No **Bedrock**, o prompt caching torna a **leitura** do cache muito mais barata (a doc do `langchain4j-bedrock` cita até **~90% de economia** e 85% menos latência); a **escrita** pode custar **mais** que entrada normal — só compensa com reúso frequente dentro do TTL. O **mínimo cacheável varia por modelo**: **4.096 tokens** no Sonnet 4.5, **1.024** no Sonnet 4.6. Máximo de **4 checkpoints** por requisição; TTL **5 min** (1 h só em Sonnet 4.5 / Opus 4.5 / Haiku 4.5).

O bloco fixo de ~6K (system + tools) que reenviamos a **todo** turno é o candidato perfeito: cacheado, sua leitura despenca a cada turno. **É a resposta direta ao custo N²** que diagnosticamos no Módulo 2.

> ⚠️ **Regra de ouro do cache (prefix match):** o cache casa por **prefixo** — qualquer byte alterado no prefixo invalida tudo depois dele. Ordem de render: **`tools` → `system` → `messages`**. No Bedrock você marca um **cachePoint explícito** (ex.: `AFTER_SYSTEM`): tudo *antes* dele é cacheado. Logo: **conteúdo estável primeiro** (system prompt congelado, lista de tools determinística), **conteúdo volátil depois** (a conversa que cresce). Nunca injete `timestamp`, UUID ou "data de hoje" no system prompt — invalida o cache a cada requisição (o silencioso assassino de cache do Módulo 2).

## 7A.5 A tensão central: caching **vs.** sumarização

`★ Insight (decisão de arquitetura que pouca gente vê) ─`
**Sumarizar o histórico e cachear o prefixo puxam em direções opostas.** A janela de **mensagens/tokens** é *append-only*: você adiciona no fim e o prefixo (system + tools + turnos antigos já cacheados) permanece byte-a-byte igual → **o cache continua válido** e você paga ~0,1× por ele. Já a **sumarização** *reescreve* o meio da conversa (troca 10 turnos por 1 resumo) → muda o prefixo → **invalida o cache** de tudo depois daquele ponto, forçando reescrita a 1,25×. 

Conclusão prática para o banco: prefira **janela + caching** para o caso comum (barato e simples), e **sumarize com parcimônia** — só quando a conversa fica longa de verdade e o custo de carregar history crua supera o custo de quebrar o cache. Medir, não adivinhar.
`─────────────────────────────────────────────────`

## 7A.6 Os desafios bancários específicos

1. **Resultados de tools são os maiores consumidores.** Um Super Extrato ou uma fatura detalhada pode ocupar milhares de tokens. Some o princípio do Módulo 6A.5 (moldar retornos pequenos) **com** expiração agressiva de resultados antigos na memória.
2. **PII se acumula — na janela E no armazenamento.** Tudo que entra na "mesa" (saldos, nomes, chaves Pix) fica no histórico e, se você persistir a memória (7B), **em repouso**. Implicações: minimização de dados, política de **retenção**, criptografia, e o **direito ao esquecimento** — apagar a memória de um cliente sob demanda (LGPD). Prévia do Módulo 13.
3. **Persistência vs. realidade de produção.** Memória só em RAM **morre no restart** e não escala horizontalmente (Módulo 5: o Micronaut sobe rápido e escala — mas cada instância teria sua própria memória). Produção pede um **store durável** (Redis/banco) por `@MemoryId` — o que reintroduz o problema de PII em repouso.
4. **Operações que movem dinheiro são multi-turno.** Um fluxo "agende este boleto → confirme" precisa reter contexto suficiente entre os turnos; uma janela curta demais pode "esquecer" o que estava sendo confirmado (perigoso — Módulo 12).

## 7A.7 Modos de falha

| Falha | O que é | No banco |
|---|---|---|
| **Overflow / truncamento** | Estourou a janela; o framework corta o histórico | Perde o produto que o cliente mencionou há 3 turnos |
| **Perdido no meio** | Info relevante mal posicionada na janela cheia (Módulo 2) | Ignora a cláusula recuperada |
| **_Cache thrashing_** | Prefixo varia a cada turno → **0 hits** de cache | Paga 1× sempre; o custo N² volta com força |
| **Custo descontrolado** | Sem janela nem caching, history crua cresce sem limite | Conta de inferência explode silenciosamente |

## ✅ Checagem de entendimento (Parte A)

1. Por que "caber em 200K" raramente é o problema real num banco — e qual é o problema real?
2. Por que o bloco *system + tools* é o candidato ideal a **prompt caching**?
3. Explique a tensão entre **sumarizar** o histórico e **cachear** o prefixo.
4. Por que persistir a `ChatMemory` num store durável é necessário em produção **e** cria um problema de segurança?
5. O que é _cache thrashing_ e como ele faz o custo N² "voltar"?

---

# Parte B — A API de memória do LangChain4j

> **Aterrada por verificação:** símbolos conferidos contra o código-fonte da tag `1.16.2`. Fontes ao final.

## 7B.1 `ChatMemory` e as duas janelas

`ChatMemory` (pacote `dev.langchain4j.memory`, módulo `langchain4j-core`) é a interface: `id()`, `add(ChatMessage)`, `messages()` (retorna `List<ChatMessage>` — que pode ser um **subconjunto** ou **resumo**, não tudo) e `clear()`. Duas implementações de janela (pacote `dev.langchain4j.memory.chat`):

| Implementação | Fábrica | Despejo (eviction) |
|---|---|---|
| **`MessageWindowChatMemory`** | `withMaxMessages(int)` | mantém as últimas **N mensagens** |
| **`TokenWindowChatMemory`** | `withMaxTokens(int, TokenCountEstimator)` | mantém os últimos **N tokens** |

Em ambas, o despejo é **mais antigo primeiro** e **indivisível** (uma mensagem que não cabe é removida inteira). **Para o orçamento de 200K do Sonnet, prefira `TokenWindowChatMemory`** — o despejo acompanha o **custo real em tokens**, não a contagem de mensagens.

## 7B.2 O que a janela protege automaticamente (importa muito no banco)

Dois comportamentos verificados na fonte que evitam bugs sérios:

1. **A `SystemMessage` é fixada (_pinned_) e nunca despejada** — há no máximo uma por vez; uma nova substitui a antiga. (`alwaysKeepSystemMessageFirst(Boolean)` controla se ela vai no índice 0.) Ou seja: **políticas/guardrails do banco no system prompt sobrevivem ao despejo** — e, como veremos em 7B.6, é a mesma `SystemMessage` que você vai **cachear**. _Pinning_ e caching se reforçam.
2. **`ToolExecutionResultMessage` órfão é despejado junto** — quando uma `AiMessage` com pedido de tool é despejada, os resultados de tool que a seguem também saem. Isso evita um erro real: muitos LLMs **proíbem** um resultado de tool sem o pedido correspondente. O framework cuida disso por você.

## 7B.3 Memória por cliente — e o vazamento que ninguém vê

`ChatMemoryProvider` (`@FunctionalInterface`, `ChatMemory get(Object memoryId)`) + `@MemoryId` (no parâmetro do AI Service) dão **uma memória isolada por cliente**.

`★ Ponto de atenção verificado (vazamento de memória) ─`
**O `AiServices` retém TODA `ChatMemory` que já criou.** Num serviço bancário de vida longa, cada cliente que conversa uma vez deixa sua memória **presa para sempre** — vazamento de memória clássico, agravado em escala. A correção verificada: a interface do AI Service **estende `ChatMemoryAccess`** (`dev.langchain4j.service.memory`), que expõe `getChatMemory(memoryId)` e **`evictChatMemory(memoryId)`**. Chame `evictChatMemory` ao fim da conversa. **Bônus:** esse mesmo método é a sua ferramenta para o **direito ao esquecimento** (LGPD) — apagar a memória de um cliente sob demanda.
`─────────────────────────────────────────────────`

## 7B.4 Persistência: `ChatMemoryStore`

`ChatMemoryStore` (`dev.langchain4j.store.memory.chat`, em `langchain4j-core`) é a SPI de persistência, com três métodos por `memoryId`: `getMessages`, `updateMessages`, `deleteMessages`.

- **Padrão (em memória):** `SingleSlotChatMemoryStore` (`@Internal`, um slot por `id`). _(Nota: a doc menciona `InMemoryChatMemoryStore` como "única implementação", mas o default real das janelas é o `SingleSlot` — divergência doc/código no 1.16.2.)_ `InMemoryChatMemoryStore` (público, `ConcurrentHashMap`) serve para um store multi-conversa em RAM.
- **Produção (durável):** implemente `ChatMemoryStore` (Redis/SQL) e injete via `builder().chatMemoryStore(...)`, serializando com `ChatMessageSerializer`/`ChatMessageDeserializer`.
- **Ciclo de vida (verificado):** por interação, `getMessages` é chamado **~1× (leitura)** e `updateMessages` **~2× (escrita)** — uma ao adicionar a `UserMessage`, outra ao adicionar a `AiMessage`; `deleteMessages` só dispara no `clear()`. **O store é tocado a cada turno → eficiência de escrita importa.**

## 7B.5 Contagem de tokens no Bedrock: estime local, confira remoto

Para a `TokenWindowChatMemory` você passa um `TokenCountEstimator` (`dev.langchain4j.model`). **No caminho Bedrock, o `langchain4j-bedrock` 1.16.2 não traz nenhum contador de tokens** (verificado por listagem completa do módulo). A AWS tem a operação `CountTokens` (`POST /model/{modelId}/count-tokens`, IAM `bedrock:CountTokens`), **mas**:

> ⚠️ **`CountTokens` é REMOTO** — chamá-lo **a cada `add`** na memória custa latência (e uma chamada AWS). **Não o use na janela ao vivo.** Use um `TokenCountEstimator` **local/aproximado** para o dimensionamento por turno e reserve o `CountTokens` da AWS para **verificação ocasional**. Não há tokenizador offline do Claude; um estimador local (heurística/`jtokkit`) **subconta** o Claude ~15–20% — deixe folga no `maxTokens`. O **consumo real** (incl. cache) volta na resposta: faça *cast* de `chatResponse.metadata().tokenUsage()` para **`BedrockTokenUsage`** e leia `cacheReadInputTokens()`/`cacheWriteInputTokens()` (a interface `TokenUsage` simples não expõe os campos de cache).

## 7B.6 Prompt caching no `langchain4j-bedrock` — a resposta de produção

> ⚠️ **Armadilha de provedor (verificada):** `cacheSystemMessages(true)`/`cacheTools(true)` são métodos **reais**, mas do módulo `langchain4j-anthropic` (API direta da Anthropic). **No caminho Bedrock eles NÃO existem e têm efeito ZERO** — o código compila e não cacheia nada. É o erro "parece certo" que só a fonte primária pega.

O jeito Bedrock (verificado em `BedrockChatRequestParameters.java` @ 1.16.2) é um **cachePoint** via `defaultRequestParameters`:

```java
BedrockChatModel model = BedrockChatModel.builder()
    .modelId("us.anthropic.claude-sonnet-4-5-20250929-v1:0")   // inference profile cross-region
    .region(Region.US_EAST_1)
    .defaultRequestParameters(BedrockChatRequestParameters.builder()
        .promptCaching(BedrockCachePointPlacement.AFTER_SYSTEM, // cacheia tools+system (o prefixo fixo)
                       CacheTTL.VALUE_5_M)                       // VALUE_5_M / VALUE_1_H (enum do AWS SDK)
        .build())
    .build();
```

- **Placements** (`BedrockCachePointPlacement`): `AFTER_SYSTEM`, `AFTER_USER_MESSAGE`, `AFTER_LAST_USER_MESSAGE`, `AFTER_TOOLS`. `null` desliga; TTL `null` = 5 min.
- **Granular (alternativa):** `BedrockSystemMessage.builder().addTextWithCachePoint(...)` — mas `AFTER_SYSTEM` é **ignorado** se a última mensagem de system for `BedrockSystemMessage`, e a `MessageWindowChatMemory` **não** trata esse tipo; **com memória, prefira `promptCaching(AFTER_SYSTEM)` com uma `SystemMessage` do core**.
- **Limites:** máx. **4 checkpoints**/requisição (`MAX_CACHE_POINTS_PER_REQUEST = 4`); mínimo por checkpoint **varia** (4.096 tok no Sonnet 4.5; 1.024 no Sonnet 4.6) — prefixo abaixo do mínimo **cai para cobrança normal em silêncio**.
- **`CacheTTL`** é enum do **AWS SDK** (`software.amazon.awssdk.services.bedrockruntime.model.CacheTTL`): `VALUE_5_M`/`VALUE_1_H` — **não** `FIVE_MINUTES`/`ONE_HOUR`. 1 h só em Sonnet 4.5 / Opus 4.5 / Haiku 4.5.
- **Cota:** `cacheReadInputTokens` **não** contam para TPM/TPD; `cacheWriteInputTokens` **contam**. Claude 3.7+ queima **5×** em tokens de saída.
- **Observabilidade:** *cast* de `tokenUsage()` para `BedrockTokenUsage` → `cacheReadInputTokens()`/`cacheWriteInputTokens()` — **confirme o ganho** (se `cacheRead` fica em zero, prefixo abaixo do mínimo ou invalidador silencioso).

## 7B.7 O assistente do banco — memória + caching + privacidade

```java
// Claude Sonnet no Bedrock, com cachePoint do prefixo fixo (a alavanca contra o N²)
BedrockChatModel model = BedrockChatModel.builder()
    .modelId("us.anthropic.claude-sonnet-4-5-20250929-v1:0")   // inference profile
    .region(Region.US_EAST_1)
    .defaultRequestParameters(BedrockChatRequestParameters.builder()
        .promptCaching(BedrockCachePointPlacement.AFTER_SYSTEM, CacheTTL.VALUE_5_M)
        .build())
    .build();

// AI Service estende ChatMemoryAccess → poder de despejar/esquecer
interface AssistenteBanco extends ChatMemoryAccess {
    @SystemMessage("You are the assistant of Bank X. Use tools for account data; "
        + "never reveal another customer's data. Answer in Brazilian Portuguese.")
    String conversar(@MemoryId String clienteId, @UserMessage String pergunta);
}

AssistenteBanco assistente = AiServices.builder(AssistenteBanco.class)
    .chatModel(model)
    .tools(new FerramentasBanco(contaService))
    .chatMemoryProvider(clienteId -> TokenWindowChatMemory.builder()
        .id(clienteId)
        .maxTokens(20_000, estimadorLocalBarato)   // bem abaixo de 200K; estimador LOCAL (não o remoto)
        .chatMemoryStore(redisStore)               // produção: store durável por clienteId (PII em repouso!)
        .build())
    .build();

// ... ao encerrar a conversa (ou sob pedido de LGPD):
assistente.evictChatMemory(clienteId);             // libera a memória e/ou "esquece" o cliente
```

Note como **cada peça resolve um problema da Parte A**: `TokenWindowChatMemory(20_000)` controla o N² e cabe folgado em 200K; o `promptCaching(AFTER_SYSTEM)` do Bedrock derruba o custo do prefixo fixo; `redisStore` dá durabilidade (ao custo de PII em repouso — Módulo 13); `evictChatMemory` resolve vazamento **e** direito ao esquecimento.

## 📚 Fontes (Parte B)

- Código-fonte 1.16.2: [`ChatMemory.java`](https://raw.githubusercontent.com/langchain4j/langchain4j/1.16.2/langchain4j-core/src/main/java/dev/langchain4j/memory/ChatMemory.java), [`MessageWindowChatMemory.java`](https://raw.githubusercontent.com/langchain4j/langchain4j/1.16.2/langchain4j/src/main/java/dev/langchain4j/memory/chat/MessageWindowChatMemory.java), [`BedrockChatRequestParameters.java`](https://raw.githubusercontent.com/langchain4j/langchain4j/1.16.2/langchain4j-bedrock/src/main/java/dev/langchain4j/model/bedrock/BedrockChatRequestParameters.java), [`BedrockTokenUsage.java`](https://raw.githubusercontent.com/langchain4j/langchain4j/1.16.2/langchain4j-bedrock/src/main/java/dev/langchain4j/model/bedrock/BedrockTokenUsage.java)
- [Doc — Chat Memory](https://docs.langchain4j.dev/tutorials/chat-memory) · [AWS Bedrock — Prompt caching](https://docs.aws.amazon.com/bedrock/latest/userguide/prompt-caching.html) · [AWS — CountTokens](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_runtime_CountTokens.html) · [Burndown de cota](https://docs.aws.amazon.com/bedrock/latest/userguide/quotas-token-burndown.html)

## ✅ Checagem (Parte B)

1. Por que `TokenWindowChatMemory` é preferível a `MessageWindowChatMemory` num orçamento de 200K?
2. Dois comportamentos automáticos da janela que evitam bugs — quais?
3. Por que o `AiServices` "vaza" memória, e qual método verificado resolve (também servindo à LGPD)?
4. Por que medir tokens da janela ao vivo no Bedrock pede um estimador **local** (e para que serve o `CountTokens` da AWS)?
5. Qual API do Bedrock ataca o custo N² (e por que `cacheSystemMessages` **não** serve aqui), e como você **confirma** o ganho?

> ➡️ **Próximo:** Módulo 8 — RAG no LangChain4j (`EmbeddingStore`, `ContentRetriever`, `RetrievalAugmentor`), levando o Módulo 4 à prática com filtro por metadado (nacional vs. global).
