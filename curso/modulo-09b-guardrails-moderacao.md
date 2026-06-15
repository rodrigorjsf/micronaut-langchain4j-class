# Módulo 9b — Guardrails e moderação no LangChain4j (1.16.2) sobre AWS Bedrock

> **Rascunho-fonte da Lição 11** (`lessons/0011-guardrails-moderacao.html`). Aterrado na
> fonte 1.16.2 (`dev.langchain4j.guardrail`, `BedrockGuardrailConfiguration`) + docs AWS.
> A Lição 10 entregou o objeto **tipado**; esta o **defende**.

A Lição 10 fechou com um ponto: o POJO parseado é **tipado mas não-confiável**. Esta lição
adiciona a **rede de defesa** — e separa, com cuidado, **dois sistemas que só compartilham a
palavra "guardrail"**.

**Ganho:** defender a saída do banco com um `OutputGuardrail` que **reprompta**, mais o
**Bedrock Guardrails** como rede da plataforma — sabendo que guardrail é **defesa
probabilística, nunca autorização**.

---

## 1 · Dois sistemas de guardrail (não confunda)

| Camada | O que é | Onde mora | Você escreve… |
| --- | --- | --- | --- |
| **LangChain4j guardrails** | checagens **no seu código**, in-process | `dev.langchain4j.guardrail` (core) + `dev.langchain4j.service.guardrail` (anotações) | **código** (Java) |
| **AWS Bedrock Guardrails** | filtro de conteúdo **do provedor** | config na AWS, anexada à chamada | **configuração** (na AWS) |

Elas **compõem** (defesa em profundidade) e o próprio Bedrock as cabla em linhas separadas
da saída estruturada. **⚠️ Todo o framework de guardrails do LangChain4j é `@Experimental`
em 1.16.2** — assinaturas podem mudar entre _minors_; não é controle de segurança GA.

## 2 · LangChain4j: Input e Output guardrails (verificado)

- **`InputGuardrail`** (`extends Guardrail<InputGuardrailRequest, InputGuardrailResult>`):
  `validate(UserMessage)`; helpers **default** `success()`, `failure(String)`, `fatal(String)`.
  **Sem retry/reprompt** — a primeira falha encerra a cadeia e vira `GuardrailException` para
  o chamador. Use para: detectar prompt injection/abuso **antes** do modelo.
- **`OutputGuardrail`** (`...<OutputGuardrailRequest, OutputGuardrailResult>`): `validate(AiMessage)`;
  além de `success()`, tem **`reprompt(msg, reprompt)`** (re-invoca o modelo com novo prompt
  anexado) e **`retry(msg)`** (re-invoca com o **mesmo** prompt).

`★ Armadilha verificada ─────────────────────────`
**`reprompt(...)`/`retry(...)`/`fatal(String)` são métodos `default` da INTERFACE
`OutputGuardrail`, NÃO estáticos de `OutputGuardrailResult`.** `OutputGuardrailResult.reprompt(...)`
**não compila**; e o estático `OutputGuardrailResult.failure(...)` recebe `List<Failure>`, não
`String`. Chame `reprompt(...)` **direto** dentro do `validate(...)`.
`─────────────────────────────────────────────────`

**Registro** (anotações em `dev.langchain4j.service.guardrail`): `@InputGuardrails({...})`,
`@OutputGuardrails(value={...}, maxRetries=2)`. Precedência: **método > classe > builder**
programático (exceção: se guardrails **e** config forem setados no builder, o builder vence).
`maxRetries` é **total de tentativas** (default 2; `0`→1; negativo→2); esgotou →
`OutputGuardrailException`. `@InputGuardrails` **não** tem `maxRetries` (entrada não tem retry).

```java
class PromptInjectionGuard implements InputGuardrail {
    @Override public InputGuardrailResult validate(UserMessage um) {
        String t = um.singleText().toLowerCase();
        if (t.contains("ignore as instrucoes") || t.contains("ignore previous"))
            return failure("Possivel prompt injection");   // default helper
        return success();
    }   // input NAO tem retry/reprompt: a falha vira GuardrailException
}

class PiiPtBrGuard implements OutputGuardrail {
    @Override public OutputGuardrailResult validate(AiMessage resp) {
        String txt = resp.text();
        if (txt == null || txt.isBlank())
            return reprompt("Resposta vazia", "Responda em pt-BR, em JSON valido."); // re-invoca c/ novo prompt
        if (vazaContaDeOutroCliente(txt))
            return reprompt("Possivel vazamento de PII", "NAO inclua dados de outro cliente.");
        return success();
    }   // reprompt/retry sao metodos DEFAULT da interface — nunca OutputGuardrailResult.reprompt(...)
}

interface BankAssistant {
    @InputGuardrails(PromptInjectionGuard.class)
    @OutputGuardrails(value = PiiPtBrGuard.class, maxRetries = 2) // 2 = total de tentativas
    Triagem triar(@V("msg") String msg);
}
```

## 3 · AWS Bedrock Guardrails (a rede da plataforma)

Sistema **separado**, do provedor. Políticas (docs AWS): **filtros de conteúdo** (Hate,
Insults, Sexual, Violence, Misconduct, **Prompt Attack** = jailbreak/injection), **tópicos
negados**, **filtros de palavra**, **filtros de informação sensível** (PII: bloquear **ou**
mascarar/anonimizar), **contextual grounding check** (nota de aterramento + relevância, p/ RAG).

Anexar em `langchain4j-bedrock` 1.16.2 — `BedrockGuardrailConfiguration` tem **exatamente
três** campos: `guardrailIdentifier`, `guardrailVersion`, `streamProcessingMode`
(`ProcessingMode{SYNC, ASYNC}`). **Não há campo `trace`** — o LangChain4j fixa
`GuardrailTrace.ENABLED` internamente (por isso os _assessments_ por política voltam no trace).

```java
BedrockGuardrailConfiguration gc = BedrockGuardrailConfiguration.builder()
    .guardrailIdentifier("gr-xxxxxxxx")
    .guardrailVersion("DRAFT")
    .streamProcessingMode(BedrockGuardrailConfiguration.ProcessingMode.SYNC) // SYNC = veredito antes do token
    .build();
BedrockChatRequestParameters params = BedrockChatRequestParameters.builder()
    .guardrailConfiguration(gc)   // ⚠️ builder = guardrailConfiguration(...); getter = bedrockGuardrailConfiguration()
    .build();
ChatModel model = BedrockChatModel.builder()
    .modelId("us.anthropic.claude-sonnet-4-5-20250929-v1:0")
    .region(Region.US_EAST_1)
    .defaultRequestParameters(params)
    .build();
```

- **In-band** (Converse, junto da geração) exige IAM `bedrock:InvokeModel`; **out-of-band**
  (pré-triagem) usa a operação `ApplyGuardrail` (IAM `bedrock:ApplyGuardrail`).
- `GuardrailAssessment`: `action` (`ANONYMIZED|BLOCKED|NONE|UNKNOWN`), `policy`
  (`TOPIC|CONTENT|WORD|SENSITIVE|CONTEXT`) — **flags de avaliação, não um veredito de permissão**.

## 4 · Moderação: para Claude-on-Bedrock, Guardrails É a moderação

O `langchain4j-core` define a SPI `ModerationModel`, **mas as implementações em 1.16.2 são só
OpenAI, Mistral, Watsonx** — **não há `ModerationModel` para Bedrock/Anthropic**. Logo, para
este banco **não existe** `ModerationModel.moderate()`; a moderação é o **Bedrock Guardrails**
(in-band via `BedrockGuardrailConfiguration`, ou out-of-band via `ApplyGuardrail`).

## 5 · A fronteira que ancora tudo: guardrail ≠ autorização

`★ Insight ─────────────────────────────────────`
**Guardrails (as DUAS camadas) são defesa probabilística, NUNCA a camada de autorização.**
Onde a API deixa isso claro: o Javadoc do `@InputGuardrails` diz, verbatim, *"It does not
replace a moderation model"*; o `GuardrailAssessment` expõe **flags** (`BLOCKED`/`ANONYMIZED`),
não allow/deny; o `ProcessingMode.ASYNC` **libera tokens antes** de terminar a avaliação
(prova de que é _best-effort_, não portão rígido). A autorização real é **IAM**
(`bedrock:InvokeModel`, a condição `bedrock:GuardrailIdentifier`) **+ a sua autorização de
negócio no código** (Lição 1, e o filtro forçado pelo servidor da Lição 9). Guardrail reduz o
risco residual; ele **não substitui** o controle de acesso. **Nota de compliance:** conteúdo
bloqueado aparece em **texto puro** nos Bedrock Model Invocation Logs, se ligados — cuidado com
PII em pt-BR.
`─────────────────────────────────────────────────`

Defesa em profundidade:

```
entrada → [InputGuardrail (app)] → modelo  ⟵ [Bedrock Guardrails (provedor)]
        → [OutputGuardrail (app, pode repromptar)] → resposta
        — e a autorização (IAM + código determinístico) por fora de tudo
```

## Quiz

1. **O que distingue as duas famílias de "guardrail"?**
   - (a) São a mesma coisa, com nomes diferentes por versão
   - (b) ✅ LangChain4j roda no seu código; Bedrock é do provedor
   - (c) Uma valida a entrada e a outra valida só a saída
   > Compartilham só a palavra. Uma é código in-process; a outra, config gerenciada na AWS.

2. **Um OutputGuardrail bloqueou um vazamento de PII. Isso é a sua autorização?**
   - (a) Sim: o guardrail é a camada que decide quem acessa o quê
   - (b) Sim, desde que o Bedrock Guardrails também esteja ligado
   - (c) ✅ Não: guardrail é defesa probabilística; autz é IAM/código
   > Guardrail é _best-effort_ (ASYNC libera tokens antes de avaliar). Autorização = IAM + código.

3. **Como sinalizar "resposta ruim, tente de novo" num OutputGuardrail?**
   - (a) Retornando `OutputGuardrailResult.reprompt(...)`, o estático
   - (b) ✅ Chamando `reprompt(...)`, método default da interface
   - (c) Lançando `OutputGuardrailException` de dentro do validate
   > `reprompt/retry` são `default` da interface `OutputGuardrail`. O estático em
   > `OutputGuardrailResult` não existe (e `failure` recebe `List<Failure>`, não String).

## Vá mais fundo (fonte primária)

- **LangChain4j — Guardrails:** https://docs.langchain4j.dev/tutorials/guardrails (lembre: `@Experimental`).
- **AWS — Bedrock Guardrails:** https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails.html ·
  componentes: `.../guardrails-components.html` · `ApplyGuardrail` (API Reference).
- Fonte conferida @ 1.16.2: `OutputGuardrail.java` (reprompt/retry default), `OutputGuardrailExecutor.java`
  (maxRetries), `BedrockGuardrailConfiguration.java`, `GuardrailAssessment.java`, `ModerationModel.java`.
- **Próximo (Lição 12):** integração `micronaut-langchain4j` (DI de compilação, beans, config).
