# Módulo 9 — Saída estruturada no LangChain4j (1.16.2) sobre AWS Bedrock

> **Rascunho-fonte da Lição 10** (`lessons/0010-saida-estruturada.html`). Aterrado em
> fonte primária: código-fonte do LangChain4j na tag `1.16.2` (`DefaultAiServices`,
> `PojoOutputParser`, `ResponseFormat`, `BedrockChatModel`) + docs AWS Bedrock.
> Guardrails e moderação ficam para a **Lição 11** (Módulo 9b) — esta lição entrega o
> objeto *tipado*; a próxima ensina a *defendê-lo*.

Até aqui o agente **busca** (tools, RAG — Lições 4/9) e **lembra** (memory — Lição 8).
Agora: **confiar na forma da saída**. O ganho desta lição: fazer o `AiService` do banco
devolver um **objeto tipado** que o backend pode *rotear* e *decidir* — e entender por que
ele é **tipado mas ainda não-confiável**.

---

## 1 · Por que um banco precisa de saída estruturada

Texto livre serve para **mostrar** ao cliente. Mas o backend agêntico precisa **decidir**:
"isto é um Pix, um pagamento de boleto ou uma dúvida de tarifa?", "o valor é R$ 100,00?".
Para isso a saída tem de ser **tipada e validável** — um `record`, não uma frase.

| Você quer... | Forma da saída |
| --- | --- |
| Exibir uma resposta ao cliente | `String` (texto livre) |
| **Rotear / decidir / persistir** no backend | **POJO/record tipado** (saída estruturada) |

## 2 · O tipo de retorno **é** o contrato (verificado)

No `AiServices` 1.16.2, **o tipo de retorno do método dirige tudo** — não há anotação
`@Json` nem `responseFormat` por chamada. `DefaultAiServices` calcula o `returnType` e
escolhe a estratégia (linhas 246-247).

- Tipos suportados (via `DefaultOutputParserFactory`): `boolean/int/long/double`,
  `BigInteger`/`BigDecimal`, `Date`/`LocalDate`/`LocalTime`/`LocalDateTime`, **enum**,
  `List<T>`/`Set<T>` (de String/enum/POJO) e, por padrão, **POJO/record** (`PojoOutputParser`).
- **`@Description`** (FQN **`dev.langchain4j.model.output.structured.Description`**,
  `@Target({FIELD, TYPE})`) descreve campos/classe para o schema. **Não** mira parâmetros
  de método (`dev.langchain4j.service.output.Description` **não existe** — 404).
- **`Result<T>`** (`dev.langchain4j.service`) embrulha o tipo com `content()`,
  `tokenUsage()`, `sources()` (os *chunks* do RAG — Lição 9!), `finishReason()`,
  `toolExecutions()`. Dirige o **mesmo** schema do `T` interno.
- **Armadilha:** `Map` é degenerado — não há `MapOutputParser`, e `schemaNotRequired(Map.class)`
  pula schema **e** prompt. **Prefira um POJO/record concreto.**

## 3 · Os dois caminhos do AiServices (e só dois)

`DefaultAiServices` decide entre **exatamente duas** estratégias (não há um terceiro
caminho via tool-use para saída por tipo de retorno — *tool-use* é function calling,
outro mecanismo):

| Caminho | Quando (todos verdadeiros) | O que faz |
| --- | --- | --- |
| **(A) JSON schema nativo** | `supportsJsonSchema()` **e** `!streaming` **e** `!returnsImage` **e** há schema | monta `ResponseFormat.builder().type(JSON).jsonSchema(...)` |
| **(B) JSON por prompt (fallback)** | capability ausente **ou** sem schema | **em silêncio** anexa instrução em linguagem natural à mensagem, **sem nenhuma garantia** |

`supportsJsonSchema()` = `chatModel.supportedCapabilities().contains(RESPONSE_FORMAT_JSON_SCHEMA)`.
`ResponseFormatType` tem **só** `TEXT` e `JSON` (não há constante `JSON_SCHEMA`); "schema
nativo" = `type(JSON)` **+** um `JsonSchema` não-nulo.

## 4 · Bedrock: o opt-in obrigatório (e o fallback silencioso)

`★ Insight ─────────────────────────────────────`
**O gêmeo do `cacheSystemMessages` da Lição 8.** Por padrão, `BedrockChatModel` **não
anuncia** a capability `RESPONSE_FORMAT_JSON_SCHEMA` (`Utils.copy(null) = Set.of()` — conjunto
vazio). Resultado: o `AiServices` **cai no fallback por prompt em silêncio** — sem warning,
sem exceção. Você acha que tem schema forçado; tem só uma "sugestão" de formato. É o mesmo
modo de falha "compila e não faz o que você acha": só a fonte primária pega.
`─────────────────────────────────────────────────`

A correção — **opt-in explícito**:

```java
ChatModel model = BedrockChatModel.builder()
    .modelId("us.anthropic.claude-sonnet-4-5-20250929-v1:0")
    .region(Region.US_EAST_1)
    .supportedCapabilities(Capability.RESPONSE_FORMAT_JSON_SCHEMA)  // sem isto: fallback silencioso
    .build();
```

Com o opt-in, o caminho nativo do Converse monta
`OutputConfig.textFormat(OutputFormat.type(JSON_SCHEMA).structure(...))` (`BedrockChatModel.java:95`)
— **separado** do `.guardrailConfig(...)` (linha 94): saída estruturada e guardrails são
ortogonais. `outputConfigFrom` lança `UnsupportedFeatureException("JSON response format is
not supported without a schema")` se você pedir JSON sem schema. Provado pelo teste de
integração `BedrockAiServiceWithJsonSchemaIT` (com `us.anthropic.claude-haiku-4-5-20251001-v1:0`,
`isStrictJsonSchemaEnabled=true`).

## 5 · O assistente do banco: triagem tipada

```java
import dev.langchain4j.model.bedrock.BedrockChatModel;
import dev.langchain4j.model.chat.Capability;
import dev.langchain4j.model.chat.ChatModel;
import dev.langchain4j.model.output.structured.Description;
import dev.langchain4j.service.AiServices;
import dev.langchain4j.service.Result;
import dev.langchain4j.service.UserMessage;
import dev.langchain4j.service.V;
import software.amazon.awssdk.regions.Region;
import java.math.BigDecimal;

enum Intencao { CONSULTA, PIX, PAGAMENTO_BOLETO, FORA_DE_ESCOPO }

record Triagem(
        Intencao intencao,
        @Description("produto citado, ex.: CDB, cartao, Pix; senao null") String produto,
        @Description("valor em reais se houver; senao null") BigDecimal valor,
        @Description("resumo em pt-BR da intencao do cliente") String resumo
) {}

interface Triador {
    @UserMessage("Classifique a mensagem do cliente do banco: {{msg}}")
    Triagem triar(@V("msg") String msg);

    // Variante com metadados (tokenUsage, sources do RAG, finishReason):
    @UserMessage("Classifique: {{msg}}")
    Result<Triagem> triarComMetadados(@V("msg") String msg);
}

ChatModel model = BedrockChatModel.builder()
        .modelId("us.anthropic.claude-sonnet-4-5-20250929-v1:0")
        .region(Region.US_EAST_1)
        .supportedCapabilities(Capability.RESPONSE_FORMAT_JSON_SCHEMA) // opt-in!
        .build();

Triador triador = AiServices.create(Triador.class, model);
Triagem t = triador.triar(mensagemDoCliente);

// t é TIPADO, mas NÃO-CONFIÁVEL. NUNCA aja só porque o modelo classificou "PIX":
if (t.intencao() == Intencao.PIX) {
    // valide o valor, confirme com o cliente, e AUTORIZE na camada determinística
    // (Lição 1 + Lição 11). O tipo garante a FORMA, não a VERDADE nem a permissão.
}
```

## 6 · Tipado ≠ confiável (a ponte para a Lição 11)

`★ Insight ─────────────────────────────────────`
**Saída estruturada garante a FORMA, nunca a VERDADE — nem a autorização.** O schema faz o
JSON *casar com o record*; ele **não** garante que `valor` é o certo, que `intencao` é
honesta, ou que o cliente **pode** fazer aquilo. O caminho nativo restringe a geração, mas
ainda é **probabilístico**; o fallback por prompt **não restringe nada**. Trate o POJO
parseado como **entrada não-confiável**: valide regras de negócio e **autorize no seu
código** (determinístico) antes de agir. É o mesmo princípio da Lição 1 (a sugestão do
modelo não é autorização) — e o gancho da **Lição 11** (guardrails + moderação), que adiciona
a *rede de defesa* sobre esta saída.
`─────────────────────────────────────────────────`

## Quiz (recuperação ativa)

1. **O que define o formato da saída estruturada no AiServices?**
   - (a) Uma anotação `@Json` aplicada ao método do AI Service
   - (b) ✅ O **tipo de retorno** do método (record/POJO/enum)
   - (c) Um parâmetro `responseFormat` passado em cada chamada
   > O `DefaultAiServices` lê o `returnType` e gera o schema/parser a partir dele.

2. **No Bedrock, sem o opt-in de capability de JSON schema, o que ocorre?**
   - (a) O `AiServices` lança `UnsupportedFeatureException` no build
   - (b) Ele usa o schema nativo do Converse assim mesmo, por padrão
   - (c) ✅ Cai em **JSON por prompt, em silêncio**, sem garantia
   > `supportedCapabilities` default = `Set.of()` → fallback silencioso. Opte por
   > `.supportedCapabilities(RESPONSE_FORMAT_JSON_SCHEMA)`.

3. **Recebeu um record tipado e válido do modelo. Pode confiar nele?**
   - (a) ✅ Não: é entrada não-confiável; valide e **autorize** no seu código
   - (b) Sim: o schema garante que os valores são corretos e seguros
   - (c) Sim, desde que o Bedrock Guardrails esteja ativo na chamada
   > Tipo garante FORMA, não VERDADE nem permissão. Nem guardrail é autorização (Lição 11).

## Vá mais fundo (fonte primária)

- **LangChain4j — Structured outputs / AI Services:** https://docs.langchain4j.dev/tutorials/structured-outputs
- Fonte conferida @ 1.16.2: `DefaultAiServices.java` (decisão dos dois caminhos),
  `PojoOutputParser.java` (schema + fallback), `BedrockChatModel.java` (`outputConfig`),
  `Description.java` (`@Target({FIELD,TYPE})`).
- **Próximo (Lição 11):** guardrails (`InputGuardrail`/`OutputGuardrail`, `@Experimental`)
  + AWS Bedrock Guardrails + moderação — defendendo esta saída tipada.
