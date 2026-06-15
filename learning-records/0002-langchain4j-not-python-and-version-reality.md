# Fato canônico: LangChain4j ≠ port do Python; e a realidade de versões (2026-06)

Estabelecido como **fato canônico do workspace** (verificado em fonte primária, não cognição do usuário): **LangChain4j não é um _port_ do LangChain Python** — *"it is built for Java, not ported to it"* (doc oficial). Portanto o ecossistema Python (LangGraph, LangServe, LangSmith, Deep Agents) **não mapeia 1:1** para Java; equivalentes são distintos (ex.: `langgraph4j` é projeto de comunidade) ou agnósticos de linguagem (observabilidade via OTel/LangFuse).

Realidade de versões confirmada: **LangChain4j 1.16.2**, **Micronaut 5.0.0 GA (2026-05-20, baseline Java 25)**, **micronaut-langchain4j 2.0.1**, **Java 25 LTS** — com a correção crítica de que, no JDK 25, **Virtual Threads e Scoped Values são finais, mas Structured Concurrency ainda é _preview_ (JEP 505)**.

**Implicações:** ao chegar no ecossistema (Módulos 11, 15, 17), tratar nomes do mundo Python com ceticismo e confirmar o equivalente Java. Não recomendar Structured Concurrency como GA. Detalhes em [[referencia-versoes-2026-06.md]] (em `curso/`). Ver [[GLOSSARY.md]].
