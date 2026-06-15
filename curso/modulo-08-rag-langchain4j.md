# Módulo 8 — RAG no LangChain4j (1.16.2) sobre AWS Bedrock

> **Rascunho-fonte da Lição 9** (`lessons/0009-rag-langchain4j.html`). Tudo aqui foi
> aterrado em fonte primária: código-fonte do LangChain4j na **tag `1.16.2`** e docs
> oficiais da **AWS Bedrock**. As assinaturas são verbatim da fonte; correções
> marcadas vieram de uma passagem de verificação adversarial.

A **Lição 5** terminou com um *esboço* da arquitetura RAG do banco (§12). Este módulo
transforma aquele esboço em **código verificado** do LangChain4j 1.16.2, invocando o
Claude **via AWS Bedrock** (diretriz do banco — não a SDK direta da Anthropic).

**O ganho desta lição (um só):** cablar um `ContentRetriever` com **filtro forçado
pelo servidor** no seu `AiService`, de modo que a **conta nacional** e a **conta
global** — no mesmo `EmbeddingStore` — **nunca se cruzem**.

---

## 1 · Os dois níveis de API (o mesmo padrão da Lição 6)

Assim como `AiServices` (alto nível) embrulha o `ChatModel` (baixo nível), o RAG tem
dois níveis de entrada no `AiServices` — **e não existe um terceiro**:

| Caminho | Método no `AiServices` builder | Quando |
| --- | --- | --- |
| **RAG ingênuo** | `.contentRetriever(ContentRetriever)` | caso comum: "busque top-k e injete" |
| **RAG avançado** | `.retrievalAugmentor(RetrievalAugmentor)` | transformação/roteamento/re-rank/citação |

**Correção verificada:** **não existe** `AiServices.retriever(...)` em 1.16.2 — código
que chama `.retriever(...)` **não compila**. A palavra "retriever" só sobrevive na
*string* de erro de exclusividade. Os dois métodos são **mutuamente exclusivos**:
setar ambos lança `illegalConfiguration("Only one out of [retriever, contentRetriever,
retrievalAugmentor] can be set")`. O caminho simples internamente monta um
`DefaultRetrievalAugmentor.builder().contentRetriever(...).build()`.

- `ContentRetriever` (`dev.langchain4j.rag.content.retriever`, **core**):
  `List<Content> retrieve(Query query)` — único método **abstrato**; a lista volta
  ordenada por relevância. (Há `addListener`/`addListeners` `@Experimental` desde 1.11.0.)
- `RetrievalAugmentor` (`dev.langchain4j.rag`, **core**):
  `AugmentationResult augment(AugmentationRequest)` — o ponto de entrada do fluxo todo.

---

## 2 · Os dois pipelines da Lição 5, mapeados em classes

A Lição 5 §4 ensinou: RAG são **dois pipelines em momentos diferentes**.

```
INGESTÃO (offline)   Documento → Carregar → Quebrar → Embeddar → Guardar
                                              │           │          │
                                     DocumentSplitter  EmbeddingModel  EmbeddingStore
                                              └──────── EmbeddingStoreIngestor ────────┘

RECUPERAÇÃO (online) Pergunta → embeddar → buscar top-k → filtrar → injetar
                                              └─ EmbeddingStoreContentRetriever ─┘
```

### Pegadinha de módulos (verificada) — use o BOM

A API se divide em **dois artefatos**:

- **`langchain4j-core`**: `rag.*`, `Filter`/`MetadataFilterBuilder`,
  `EmbeddingStoreContentRetriever`, a interface `EmbeddingStore`,
  `EmbeddingStoreIngestor`, `Document`, **as duas** `Metadata`, `TextSegment`,
  `TokenCountEstimator`.
- **`langchain4j` (agregador)**: `AiServices`, `DocumentSplitters` + os
  `DocumentBy*Splitter`, e `InMemoryEmbeddingStore`.

Uma ingestão funcional precisa dos **dois** no classpath. E há **dois trilhos de
versão** na tag 1.16.2: **stable 1.16.2** (`core`, `langchain4j`, `anthropic`,
`open-ai`, `google-ai-gemini`) vs **beta `1.16.2-beta26`** (`pgvector`, `voyage-ai`,
`cohere`, `embeddings*`). Misturar a versão errada **não resolve** — gerencie tudo
pelo **`langchain4j-bom`**.

---

## 3 · O embedding na Bedrock (a escolha do banco, para pt-BR)

A Anthropic **não tem** API de embeddings — `langchain4j-anthropic` só traz
`AnthropicChatModel`/`AnthropicStreamingChatModel`, **não** há `AnthropicEmbeddingModel`
(a própria doc da Anthropic diz isso e recomenda a Voyage). Como a invocação do banco é
**via Bedrock**, o embedding também vem da Bedrock:

- **Escolha de produção (pt-BR): `BedrockCohereEmbeddingModel` + `cohere.embed-multilingual-v3`**
  (1024 dimensões, **GA**, feito para 100+ idiomas incl. português). A alternativa
  `amazon.titan-embed-text-v2:0` (também 1024-dim) tem o multilíngue rotulado pela AWS
  como *"English (100+ languages in preview)"* e o modelo *"optimized for English"* —
  inadequado como caminho primário de um banco em produção.
- **Pegadinha crítica do Cohere (verificada):** `inputType` é **obrigatório e fixo por
  instância** (`ensureNotBlank(inputType)` no construtor). A AWS manda embeddar o corpus
  com `SEARCH_DOCUMENT` e as perguntas com `SEARCH_QUERY`. Logo, um pipeline correto usa
  **DUAS instâncias**: uma `inputType(SEARCH_DOCUMENT)` para o `EmbeddingStoreIngestor` e
  outra `inputType(SEARCH_QUERY)` para o `EmbeddingStoreContentRetriever`. Cada texto é
  limitado a **512 tokens (~2048 chars)** → o `DocumentSplitter` precisa quebrar pequeno.
- Ambas estendem `DimensionAwareEmbeddingModel` (que implementa `EmbeddingModel`), então
  entram inalteradas no `EmbeddingStoreIngestor`/`EmbeddingStoreContentRetriever`.
- **Assimetria de auth (verificada):** os builders de **embedding** têm
  `credentialsProvider(AwsCredentialsProvider)`; o builder de **chat** (`BedrockChatModel`)
  **não tem** — ele fixa `DefaultCredentialsProvider.create()`. Para STS/assume-role no
  chat, construa seu `BedrockRuntimeClient` e injete via `.client(...)`.

---

## 4 · A joia da coroa: três metadados e o filtro forçado pelo servidor

O desafio central do banco (nacional vs. global, Lição 5) resolve-se com **filtro por
metadado**. Mas há **TRÊS** `Metadata` confundíveis — e o erro mora em confundi-las:

| Tipo | Pacote | Papel | A tag `account_scope`? |
| --- | --- | --- | --- |
| **`data.document.Metadata`** | `dev.langchain4j.data.document` | tags de negócio no **segmento** | **SIM — é o que `Filter.test()` inspeciona** |
| `rag.query.Metadata` | `dev.langchain4j.rag.query` | contexto da **query** (chatMemoryId, invocationParameters) | NÃO |
| `Content.metadata()` | enum `ContentMetadata` | bookkeeping (`SCORE`/`RERANKED_SCORE`/`EMBEDDING_ID`) | NÃO |

**Correção verificada (a linha mais sensível à segurança):**
`query.metadata().get("account_scope")` **NÃO EXISTE** — a `rag.query.Metadata` não tem
`get(String)`. Ela expõe: `chatMessage()`, `systemMessage()`, `chatMemoryId()`,
`chatMemory()`, `invocationContext()`, `invocationParameters()` (desde 1.6.0). O padrão
correto para um `dynamicFilter` ler o escopo:

```java
String scope = query.metadata().invocationParameters().get("account_scope"); // <T> T get(String)
// OU, quando o escopo deriva do usuário logado:
Object userId = query.metadata().chatMemoryId(); // "Can be used to distinguish between users."
```

E **`query.metadata()` pode ser `null`** (na `Query` de um argumento) → **sempre
null-check** antes de desreferenciar.

### Por que o escopo vem do SERVIDOR, não do modelo

Entitulamento é **autorização** (Lição 1: identidade/autorização na camada
determinística, nunca no modelo). O `dynamicFilter` (`Function<Query, Filter>`) lê o
escopo **confiável** (passado pelo servidor em `invocationParameters`, ou derivado do
`chatMemoryId`), **não** de algo que o modelo escreveu. Compõe-se com `AND` a qualquer
faceta de produto derivada do modelo (self-query, Lição 5 §8):

```java
Filter.and(metadataKey("account_scope").isEqualTo(scopeDoServidor),  // entitulamento (servidor)
           metadataKey("produto").isEqualTo(produtoDoModelo));        // refino (modelo, opcional)
```

### A garantia de separação (verificada na fonte)

`IsEqualTo.test()` retorna **`false`** quando o objeto não é `Metadata` **e** quando o
metadado **não contém a chave** (guarda `containsKey`). Logo, um segmento "global" (que
tem `account_scope=global`, ou não tem a chave) **nunca** casa
`metadataKey("account_scope").isEqualTo("national")`. É esse `false` que mantém os dois
mundos separados.

**Outras armadilhas verificadas do filtro:**
- `filter(Filter)` e `dynamicFilter(Function<Query,Filter>)` são métodos de **instância**
  do builder (não estáticos). Compartilham um campo `filterProvider`; `filter(filter)` é
  `if (filter != null) dynamicFilter = (q) -> filter;` → **`filter(null)` é no-op
  silencioso** e **não limpa** um filtro já setado.
- Tipos de valor da `data.document.Metadata` são um **conjunto fechado** (String, UUID,
  Integer/int, Long/long, Float/float, Double/double). **Não há** `put(String, Object)`,
  nem Boolean/List, nem `getOrDefault`. `account_scope` **tem de ser String**.
- Validação **preguiçosa** no builder do retriever: `maxResults`/`minScore` são checados
  **na hora da query** (capturados nas lambdas-provider) — `minScore(5.0)` só estoura na
  primeira busca, não no `build()`. Já `EmbeddingSearchRequest` valida **na hora** (no
  construtor).

---

## 5 · O portão de segurança: nem todo store APLICA o filtro

`EmbeddingStore.search(...)` traz no Javadoc, verbatim: *"not all EmbeddingStore
implementations support Filtering."* Se o store **ignora** o filtro, seu entitulamento
vira **no-op silencioso** = **vazamento entre contas, sem erro**. Eleve isto a portão de
segurança e escolha o store conscientemente:

- **`InMemoryEmbeddingStore`** (módulo `langchain4j`; **sem `builder()`** → use
  `new InMemoryEmbeddingStore<TextSegment>()`): **APLICA** o filtro em processo — o
  `search()` faz `if (filter != null && embedded instanceof TextSegment) { if
  (!filter.test(meta)) continue; }`. Ótimo para o **demo** do banco.
- **`PgVectorEmbeddingStore`** (`langchain4j-pgvector`, beta26; **cosine-only,
  ivfflat-only**): **APLICA** compilando o `Filter` para **SQL**. `MetadataStorageMode`
  default = **`COMBINED_JSON`** (não `COMBINED_JSONB`). Caminho de **produção**.

---

## 6 · O assistente do banco: ingestão + retrieval + wiring (verificado)

Combina os dois aterramentos: núcleo de RAG (agnóstico) + pontas Bedrock.

```java
// Maven (pelo BOM): langchain4j-core + langchain4j + langchain4j-bedrock(+pgvector em prod)
import dev.langchain4j.data.document.Document;
import dev.langchain4j.data.document.Metadata;                  // data.document.Metadata
import dev.langchain4j.data.document.splitter.DocumentSplitters; // módulo langchain4j
import dev.langchain4j.data.segment.TextSegment;
import dev.langchain4j.model.bedrock.BedrockChatModel;
import dev.langchain4j.model.bedrock.BedrockCohereEmbeddingModel;
import dev.langchain4j.model.bedrock.BedrockCohereEmbeddingModel.InputType;
import dev.langchain4j.model.bedrock.BedrockCohereEmbeddingModel.Model;
import dev.langchain4j.model.chat.ChatModel;
import dev.langchain4j.model.embedding.EmbeddingModel;
import dev.langchain4j.rag.content.retriever.EmbeddingStoreContentRetriever;
import dev.langchain4j.rag.query.Query;
import dev.langchain4j.service.AiServices;
import dev.langchain4j.store.embedding.EmbeddingStore;
import dev.langchain4j.store.embedding.EmbeddingStoreIngestor;
import dev.langchain4j.store.embedding.filter.Filter;
import dev.langchain4j.store.embedding.inmemory.InMemoryEmbeddingStore;
import software.amazon.awssdk.regions.Region;
import java.util.function.Function;
import static dev.langchain4j.store.embedding.filter.MetadataFilterBuilder.metadataKey;

static final String SCOPE_KEY = "account_scope"; // valor SEMPRE String ("national"/"global")

// (0) Pontas Bedrock — DUAS instâncias de embedding (inputType fixo por instância).
EmbeddingModel docEmbedder = BedrockCohereEmbeddingModel.builder()
        .model(Model.COHERE_EMBED_MULTILINGUAL_V3)   // "cohere.embed-multilingual-v3", 1024-dim, pt-BR
        .inputType(InputType.SEARCH_DOCUMENT)        // OBRIGATÓRIO — para indexar o corpus
        .region(Region.US_EAST_1)
        .build();
EmbeddingModel queryEmbedder = BedrockCohereEmbeddingModel.builder()
        .model(Model.COHERE_EMBED_MULTILINGUAL_V3)
        .inputType(InputType.SEARCH_QUERY)           // OBRIGATÓRIO — para embeddar a pergunta
        .region(Region.US_EAST_1)
        .build();

ChatModel chat = BedrockChatModel.builder()
        .modelId("us.anthropic.claude-sonnet-4-5-20250929-v1:0") // inference profile cross-region
        .region(Region.US_EAST_1)
        .build();

EmbeddingStore<TextSegment> store = new InMemoryEmbeddingStore<>(); // demo (aplica o filtro)

// (1) INGESTÃO — tag o discriminador UMA vez no Document; o splitter copia account_scope
//     verbatim para CADA TextSegment (+ chave "index"). Hierarquia: Parágrafo→Linha→Frase→Palavra→Caractere.
void ingest(String texto, String scope) {
    Document doc = Document.from(texto, Metadata.from(SCOPE_KEY, scope));
    EmbeddingStoreIngestor.builder()
            .documentSplitter(DocumentSplitters.recursive(300, 30)) // pequeno (limite 512 tok do Cohere)
            .embeddingModel(docEmbedder)   // obrigatório
            .embeddingStore(store)         // obrigatório
            .build()
            .ingest(doc);                  // IngestionResult só carrega tokenUsage()
}
// ingest(regrasCdbNacional, "national"); ingest(regrasCdbGlobal, "global");

// (2) RETRIEVAL — filtro POR USUÁRIO forçado pelo servidor.
Function<Query, Filter> escopoPorUsuario = query -> {
    String scope = null;
    if (query.metadata() != null && query.metadata().invocationParameters() != null) {
        scope = query.metadata().invocationParameters().get(SCOPE_KEY); // <T> T get(String)
    }
    if (scope == null) scope = "national"; // default seguro: nunca vaza global p/ query sem escopo
    return metadataKey(SCOPE_KEY).isEqualTo(scope); // segmento sem a chave nunca casa
};
EmbeddingStoreContentRetriever retriever = EmbeddingStoreContentRetriever.builder()
        .embeddingStore(store)
        .embeddingModel(queryEmbedder)     // o embedder de QUERY
        .maxResults(5)
        .minScore(0.6)
        .dynamicFilter(escopoPorUsuario)   // partição por query
        .build();

// (3) WIRING — caminho SIMPLES (não existe .retriever(...)).
interface BankAssistant { String chat(String pergunta); }
BankAssistant assistant = AiServices.builder(BankAssistant.class)
        .chatModel(chat)
        .contentRetriever(retriever)       // RAG ingênuo
        .build();
```

Cada peça resolve um ponto: **uma** `EmbeddingStore` com `account_scope` na
`data.document.Metadata`; **um** `dynamicFilter` que lê o escopo **confiável** do
servidor; o store **aplica** o `Filter.test`; o `BedrockChatModel` cabla no `AiServices`
como qualquer `ChatModel`. Um usuário **nacional** nunca recupera doc **global**.

---

## 7 · Prévia: o RAG avançado (`RetrievalAugmentor`) mapeado na Lição 5 §8

Quando o RAG ingênuo não basta (e em banco raramente basta), o
`DefaultRetrievalAugmentor` destrincha um **pipeline de 5 estágios**. Cada estágio é o
nome-de-framework de um padrão que a Lição 5 §8 já ensinou:

| Estágio (verificado) | Classe(s) 1.16.2 | Padrão da Lição 5 §8 |
| --- | --- | --- |
| 1 · Transformar query | `QueryTransformer` → `Compressing`/`Expanding` (`.chatModel(...)`) | transformação de consulta, multi-query, HyDE |
| 2 · Rotear | `QueryRouter` → `Default` (todos) / `LanguageModel` (escolhe) | self-query / roteamento por backend |
| 3 · Agregar | `ContentAggregator` → `Default` (RRF) / `ReRanking` (`ScoringModel`) | re-ranqueamento |
| 4 · Injetar | `ContentInjector` → `Default` (`metadataKeysToInclude`) | injeção + **citação** da fonte |

**Notas verificadas:** `queryRouter` é **obrigatório** no `DefaultRetrievalAugmentor`
(NPE no `build()` se nulo); o builder `.contentRetriever(...)` embrulha o retriever num
`DefaultQueryRouter` para satisfazê-lo. `DefaultQueryRouter` manda **toda** query para
**todos** os retrievers; para escolher nacional vs. global por *backend*, use
`LanguageModelQueryRouter` (mapa `ContentRetriever → descrição`,
`FallbackStrategy{DO_NOT_ROUTE(default), ROUTE_TO_ALL, FAIL}`) — mas, para **um store +
filtro**, o caminho deste módulo (§6) é mais simples e mais seguro. As classes LLM usam
`ChatModel` (não o legado `ChatLanguageModel`). O mergulho profundo fica para uma lição
futura.

---

## Quiz (recuperação ativa)

1. **Onde mora a tag `account_scope` que o filtro inspeciona?**
   - (a) Na `rag.query.Metadata`, lida via `query.metadata().get(...)`
   - (b) ✅ Na `data.document.Metadata` do segmento, que o `Filter.test()` lê
   - (c) Na `Content.metadata()`, sob uma chave do enum `ContentMetadata`
   > A `rag.query.Metadata` nem tem `get(String)`; a `Content.metadata()` é só
   > bookkeeping (SCORE/...). O filtro inspeciona o metadado **do segmento**.

2. **Por que o escopo (nacional/global) vem do servidor, e não do modelo?**
   - (a) Porque o modelo às vezes erra o idioma e troca os escopos
   - (b) Porque ler do modelo custaria mais latência que do servidor
   - (c) ✅ Porque entitulamento é autorização: nunca confie no texto
   > Identidade/autorização vivem na camada determinística (Lição 1). O `dynamicFilter`
   > lê o escopo confiável de `invocationParameters`/`chatMemoryId`.

3. **E se o `EmbeddingStore` não suportar filtro de metadado?**
   - (a) Ele lança erro no `build()`, avisando que o filtro caiu
   - (b) ✅ Ignora o filtro em silêncio — vira vazamento entre contas
   - (c) Aplica o filtro mesmo assim, por varredura linear na RAM
   > "not all EmbeddingStore implementations support Filtering." Sem suporte, o filtro é
   > no-op silencioso. `InMemoryEmbeddingStore` e pgvector **aplicam**; confirme o seu.

---

## Vá mais fundo (fonte primária)

- **LangChain4j — RAG (tutorial oficial):** https://docs.langchain4j.dev/tutorials/rag
  (Naive vs. Advanced RAG, `EmbeddingStoreContentRetriever`, `RetrievalAugmentor`).
- **AWS Bedrock:** model IDs/inference profiles, Titan/Cohere embeddings, prompt caching
  — https://docs.aws.amazon.com/bedrock/ .
- Fonte da API conferida na tag **1.16.2**:
  `langchain4j-core/.../rag/content/retriever/EmbeddingStoreContentRetriever.java`,
  `.../store/embedding/filter/MetadataFilterBuilder.java`,
  `langchain4j-bedrock/.../BedrockCohereEmbeddingModel.java`.
- Termos canônicos: ver `GLOSSARY.md`.
