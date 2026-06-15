# Módulo 19 — Avaliação: medir o assistente sem framework (LLM-as-judge no Bedrock)

> **Rascunho-fonte da Lição 21** (`lessons/0021-avaliacao.html`). Aterrado em fonte primária:
> RAGAS (taxonomia de métricas, agnóstica de framework), repo langchain4j (tutorial de avaliação
> "more information coming soon"; `ScoringModel` é reranker), Maven Central (RAGAS/DeepEval/TruLens
> sem artefato JVM; `langsmith-java` 0.1.0-beta.7), promptfoo (HTTP provider). Mesma espinha de
> honestidade-de-ecossistema do Módulo 17/Lição 19.

## 1 · Por que "vibes" não passa auditoria

Num banco regulado, "parece bom" não é evidência. Avaliação = **conjunto de testes offline**
versionado e commitado (como _fixtures_): triplas **pergunta → resposta-ouro → docs-ouro
esperados**, por escopo de conta. Roda em CI; falha o build se a qualidade regredir. Sem isso, um
ajuste de _prompt_ ou troca de modelo regride silenciosamente uma resposta de KYC ou de movimentação.

## 2 · Os dois eixos (separados)

RAG tem **duas** qualidades a medir, independentemente (recap da Lição 5):

| Eixo | Mede | Métricas | Como |
| --- | --- | --- | --- |
| **Recuperação** | vieram os _chunks_ certos? | recall@k, precision@k, **MRR** | **determinístico** — matemática de conjuntos sobre os doc-ids ouro; **sem LLM** |
| **Geração** | a resposta é fiel e relevante? | **faithfulness** (aterrada no contexto, sem inventar), **answer relevancy** | **LLM-as-judge** — um modelo forte pontua contra uma rubrica |

Definições das métricas de geração: RAGAS (agnóstico de linguagem). Você as **implementa**, não as importa.

## 3 · A realidade Java (honesta)

`★ Insight ─────────────────────────────────────`
**Java não tem camada de avaliação nativa.** O ecossistema Python entrega graders "de fábrica"
(RAGAS, DeepEval, TruLens, promptfoo, evaluators do LangSmith); na JVM **nenhum** roda
in-process. **Você constrói o juiz** — e isso é só um _prompt_ + um modelo forte + uma rubrica, que
você já tem via Bedrock.
`─────────────────────────────────────────────────`

| Peça | Realidade em Java | Use para o banco |
| --- | --- | --- |
| **langchain4j eval** | **não existe** — o tutorial de avaliação é um _placeholder_ ("more information coming soon"); sem LLM-as-judge, sem faithfulness | construa LLM-as-judge à mão |
| **`ScoringModel`** (Cohere/Jina/Voyage) | é **reranker** (relevância doc↔query p/ recuperação), **NÃO** avaliador de resposta | use p/ re-rank (Lição 5), não como _grader_ |
| **RAGAS / DeepEval / TruLens** | **só Python** (zero artefato Maven) | sidecar Python sobre _traces_ logados (se aceitar poliglota) |
| **`langsmith-java`** | existe, mas **beta** (0.1.0-beta.7) e é cliente de _tracing_, **não** _eval runner_ | observabilidade (Lição 17), não avaliação |
| **promptfoo** | Node, mas o **HTTP provider** bate em **qualquer endpoint** | conjunto de eval em CI contra o endpoint Micronaut |

## 4 · O padrão honesto: LLM-as-judge via Bedrock + AiServices

O juiz retorna um **record tipado** (não `Map` — a saída por `Map` é degenerada, Lição 10):

```java
record Verdict(int faithfulness, int relevancy, String rationale) {}   // 0..5 + justificativa

interface RagJudge {
    @SystemMessage("You are a strict evaluator of a banking assistant. "
        + "Score faithfulness (answer fully supported by the context, no invented facts) "
        + "and relevancy (answer addresses the question) from 0 to 5. Be conservative.")
    @UserMessage("Question: {{q}}\nContext: {{ctx}}\nAnswer: {{a}}")
    Verdict judge(@V("q") String question, @V("ctx") String context, @V("a") String answer);
}

RagJudge judge = AiServices.create(RagJudge.class, judgeModel);   // judgeModel = BedrockChatModel
```

Para auditabilidade: **fixe** o juiz (um _inference profile_ Claude), **temperatura 0**, **versione a
rubrica** e **guarde o `rationale`** de cada nota. Um juiz LLM é não-determinístico — por isso, para
gates de conformidade duros, **pareie** com as métricas determinísticas de recuperação.

## 5 · O gate de CI

Rode o conjunto de eval offline a cada mudança (de _prompt_, modelo, _chunking_): **falhe o build**
se faithfulness ou recall@k caírem abaixo do limiar. `promptfoo` pode hospedar o conjunto contra o
endpoint Micronaut; o juiz fica **dentro do stack** (Bedrock). Assim, um bump de modelo não regride
às escondidas uma resposta que move dinheiro.

## Fonte primária

**RAGAS — Available Metrics** (`docs.ragas.io`): definições agnósticas de faithfulness, answer
relevancy, context precision/recall — o vocabulário que você implementa em Java. Realidade Java: o
**tutorial de testing-and-evaluation do langchain4j** (GitHub). Cross-stack: **promptfoo** (HTTP
provider).
