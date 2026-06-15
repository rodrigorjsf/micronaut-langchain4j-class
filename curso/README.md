# 🏦 Trilha de Aprendizado — Sistemas Agênticos com LangChain4j + Micronaut 5 + Java 25

> **Foundation First (Fundação Primeiro):** "Conhecimento construído sobre uma fundação fraca, por maior que seja, é como um castelo de areia: vulnerável e capaz de desabar a qualquer momento."

Esta trilha ensina, do básico ao avançado, como projetar, implementar, proteger e escalar um **sistema agêntico** (um sistema de software onde um modelo de IA *decide* e *age* através de ferramentas) usando **LangChain4j** integrado ao **Micronaut 5** com **Java 25**.

## O exemplo que nos acompanha: o assistente do banco

Todo conceito é ancorado em um caso único e realista: o **chat de um banco** dentro do app. O cliente pergunta qualquer coisa sobre os produtos — "qual a fatura do meu cartão?", "agenda o pagamento desse boleto", "quanto rende meu CDB?", "qual o saldo da minha conta global?" — e o **backend agêntico**, por meio de **ferramentas (tools)**, busca a informação nos sistemas do banco e a entrega ao modelo para processar e responder.

O banco oferece praticamente todos os produtos financeiros possíveis: pagamento de contas/boletos (agendamento, erros, pagamentos), DDA (*Débito Direto Autorizado*), Pix, Super Extrato, cartão de crédito e suas faturas, compras, shopping, financiamentos, investimentos, **conta nacional (Brasil)** e **conta global** — sendo que os mesmos serviços existem para as duas contas, mas com dados vindos de **backends diferentes**. Essa multiplicidade de sistemas é, propositalmente, parte do desafio.

## Como a trilha é organizada

Cada módulo assume **apenas** o que os módulos anteriores ensinaram. Nunca pulamos a fundação.

### Parte 0 — Modelo Mental (sem framework)
- **Módulo 1 — Modelo mental e vocabulário fundamental** ✅ _disponível_

### Parte 1 — Fundamentos Técnicos (ainda sem framework)
- **Módulo 2 — Anatomia de uma chamada a um LLM**: tokens, tokenização, janela de contexto, temperatura, streaming, custo e latência.
- **Módulo 3 — O loop agêntico e o _tool calling_**: o padrão ReAct (*Reasoning + Acting* / Raciocínio + Ação), como o modelo "decide" chamar uma ferramenta.
- **Módulo 4 — RAG a fundo**: embeddings, bancos vetoriais, _chunking_, _retrieval_; quando usar RAG e quando usar tools.

### Parte 2 — LangChain4j 🔒
- **Módulo 5 — Arquitetura do LangChain4j**: a API de alto nível (`AiServices`) vs. a de baixo nível (`ChatModel`).
- **Módulo 6 — Tools (`@Tool`)**: design e granularidade de ferramentas.
- **Módulo 7 — `ChatMemory` e gestão da janela de contexto** (tema crítico).
- **Módulo 8 — RAG no LangChain4j**: `EmbeddingStore`, `ContentRetriever`, `RetrievalAugmentor`.
- **Módulo 9 — Saída estruturada, guardrails e moderação de conteúdo**.

### Parte 3 — Micronaut 5 + Java 25 🔒
- **Módulo 10 — Integração `micronaut-langchain4j`**: injeção de dependências, configuração, beans de modelo e de ferramentas.
- **Módulo 11 — Java 25 para escala**: virtual threads (_threads_ virtuais), structured concurrency (concorrência estruturada), scoped values, pattern matching, records e sealed types aplicados a roteamento e ferramentas.
- **Módulo 12 — Arquitetura do backend bancário multi-sistema**: conta nacional vs. global, agregação de múltiplos backends, idempotência, fluxos de confirmação para operações que movem dinheiro (Pix, pagamento de boleto) e _human-in-the-loop_ (humano no circuito).

### Parte 4 — Produção, Segurança e Escala 🔒
- **Módulo 13 — Segurança**: prompt injection (injeção de instruções) direta e indireta, OWASP Top 10 para Aplicações LLM, guardrails, sanitização, autorização de ferramentas, _least privilege_ e tratamento de PII (*Personally Identifiable Information* / Informação Pessoal Identificável).
- **Módulo 14 — Gestão da janela de contexto em profundidade**: sumarização, janelas de memória, _token budgeting_ (orçamento de tokens), recuperação seletiva.
- **Módulo 15 — Observabilidade**: OpenTelemetry GenAI, LangFuse, _tracing_, avaliação e _red-teaming_.
- **Módulo 16 — Escala e resiliência**: _rate limiting_, custo, cache, _fallback_, multi-tenant.
- **Módulo 17 — O ecossistema honesto**: LangGraph / langgraph4j, Deep Agents, LangServe, LangSmith, LangFuse — o que de fato existe em Java, o que é exclusivo de Python e quais as alternativas.

> 🔒 = módulo cujos detalhes de versão e API serão refinados com uma pesquisa de _grounding_ (aterramento factual) sobre as versões atuais (LangChain4j, Micronaut 5, Java 25) e o ecossistema, executada à parte para evitar ensinar fatos desatualizados.
