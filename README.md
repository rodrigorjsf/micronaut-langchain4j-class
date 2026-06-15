# 🏦 Sistemas Agênticos com LangChain4j + Micronaut 5 + Java 25

> Um **livro de estudos** (workspace `/teach`) que ensina, do zero, a construir **em produção** o
> backend agêntico de um **assistente bancário** — com Claude Sonnet **via AWS Bedrock**. Cada
> afirmação técnica é aterrada em **fonte primária** (não em conhecimento paramétrico).

## Missão

Construir o backend agêntico de um assistente de chat bancário (boleto, DDA, Pix, Super Extrato,
cartão/fatura, investimentos, financiamento — conta **nacional e global**), acertando **arquitetura,
segurança e escala**, sobre **LangChain4j + Micronaut 5 + Java 25**, invocando **Claude Sonnet (200K)
via AWS Bedrock**. Detalhe em [`MISSION.md`](MISSION.md).

## Como usar

1. Abra [`lessons/index.html`](lessons/index.html) no navegador — é o índice navegável da trilha.
2. Siga as lições em ordem (`0001` → `0022`). Cada uma é **autossuficiente**, tem **diagramas
   animados**, um **quiz de recuperação** e uma **fonte primária** recomendada.
3. **Pergunte ao professor** (o agente) sobre qualquer ponto — ele aprofunda ou cria um exercício.
4. Consulte a [referência rápida](reference/) e o [glossário](GLOSSARY.md) a qualquer momento.

> As lições usam um *design system* Tufte byte-idêntico e diagramas SVG animados por CSS (sem
> JavaScript). Prévias de diagramas ficam em [`docs/previews/`](docs/previews/).

## A trilha (22 lições, 6 partes)

- **Parte 0 — Modelo mental (sem framework).** Lição 1: por que um LLM puro não sabe seu saldo; tools,
  agente, janela de contexto, *prompt injection*.
- **Parte 1 — Fundamentos técnicos.** Lições 2–5: anatomia da chamada e custo N²; tokenização pt-BR;
  o loop agêntico e *tool calling*; RAG a fundo.
- **Parte 2 — LangChain4j (versões verificadas).** Lições 6–11: `AiServices` vs. `ChatModel`; design de
  **tools** (`@Tool`/`@P`/`@ToolMemoryId`) e **tool retrieval**; `ChatMemory` e *prompt caching*; RAG
  sobre Bedrock; saída estruturada; guardrails e moderação.
- **Parte 3 — Micronaut 5 + Java 25.** Lições 12–14: DI de compilação (e a versão real embarcada);
  concorrência do Java 25 (*virtual threads*, *structured concurrency*); arquitetura multi-backend
  agêntica (HITL, idempotência).
- **Parte 4 — Produção, Segurança e Escala.** Lições 15–19: OWASP LLM Top 10 (2025); gestão de contexto
  a fundo; observabilidade (OTel/LangFuse); escala e resiliência; o ecossistema honesto (Java vs. Python).
- **Parte 5 — Avançado: skills, avaliação e síntese.** Lições 20–22: **Agent Skills** com
  `langchain4j-skills` (progressive disclosure sobre o `ToolProvider`); **avaliação** (LLM-as-judge no
  Bedrock); e o **capstone** — a **arquitetura de referência** macro (componentes/integrações) e micro
  (o fluxo seguro como decisões: tools, agents, skills, guardrails).

## Princípios (Foundation First)

- **Conhecimento numa fundação fraca é um castelo de areia.** Cada lição assume zero conhecimento
  prévio e constrói sobre a anterior.
- **Bedrock, não a SDK direta da Anthropic.** O banco invoca o Claude via `BedrockChatModel`; exemplos
  de *chat*, *embeddings* e *prompt caching* vêm da integração com a AWS Bedrock. Ver
  [`learning-records/0004`](learning-records/0004-integracao-via-aws-bedrock.md).
- **Aterrar antes de ensinar.** APIs/versões são verificadas em fonte primária (raw GitHub na tag
  fixada, Maven Central, AWS, OWASP) — *verificado* ≠ *não-confirmado*.
- **Ensino visual.** Estrutura não-trivial é ensinada com **diagramas coloridos e animados**
  (fluxogramas de decisão com o impacto de cada escolha), não só texto + código.

## Documentos do workspace

| Arquivo | Papel |
| --- | --- |
| [`MISSION.md`](MISSION.md) | A razão de estudar — ancora todo o ensino |
| [`GLOSSARY.md`](GLOSSARY.md) | A linguagem canônica; toda lição adere a ela |
| [`RESOURCES.md`](RESOURCES.md) | Fontes de alta confiança (conhecimento) e comunidades (sabedoria) |
| [`NOTES.md`](NOTES.md) | Preferências de ensino e decisões |
| [`lessons/`](lessons/) | As lições HTML (a unidade de ensino) · [`reference/`](reference/) cheat-sheets |
| [`curso/`](curso/) | Rascunhos-fonte das lições · [`learning-records/`](learning-records/) decisões de aprendizado |

---

*Workspace `/teach` · pt-BR · Foundation First · trilha em construção contínua.*
