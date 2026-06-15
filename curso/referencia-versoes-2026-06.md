# Referência de Versões — verificada em 2026-06-14

> Documento de **referência** (não é um módulo). Versões confirmadas em **fonte primária** por busca direta, para a Parte 2+ assentar sobre rocha. Cada fato traz a fonte. Reverifique antes de iniciar um projeto real — versões mudam.

## ✅ Confirmado

| Item | Versão / Status | Fonte |
|---|---|---|
| **LangChain4j** (standalone, estável) | **1.16.2** | [Maven Central](https://central.sonatype.com/artifact/dev.langchain4j/langchain4j) |
| **LangChain4j** — JDK mínimo | **Java 17** | docs/comunidade |
| **LangChain4j** — versionamento | Duplo: trilha **estável** (`1.16.x`) + trilha **beta** (`1.x-betaNN`) para módulos novos; **use o `langchain4j-bom`** e não fixe versões à mão | docs do BOM |
| **Micronaut Framework** | **5.0.0 GA em 2026-05-20** (baseline Java 25, GraalVM 25.0.3, Groovy 5, Kotlin 2.3) | [micronaut.io](https://micronaut.io/2026/05/20/micronaut-framework-5-0-0-released/), [Java 25 baseline](https://micronaut.io/2026/04/27/micronaut-framework-5-0-with-java-25-baseline/) |
| **micronaut-langchain4j** (módulo de integração) | **2.0.1** (compilação por _annotation processor_ `micronaut-langchain4j-processor`) | [Guia oficial](https://micronaut-projects.github.io/micronaut-langchain4j/latest/guide/) |
| **Java / JDK 25** | **GA em 2025-09-16, LTS** (sucede o 21) | [InfoQ](https://www.infoq.com/news/2025/09/java25-released) |
| **LangChain4j — "não é port do Python"** | Confirmado verbatim: *"Despite the name, LangChain4j is not a Java port of LangChain (Python) — it is built for Java, not ported to it."* | [docs.langchain4j.dev/intro](https://docs.langchain4j.dev/intro) |
| **langgraph4j** | Projeto **terceiro/comunidade** (org `langgraph4j`, separada da `langchain4j`); funciona com LangChain4j e Spring AI | [github.com/langgraph4j/langgraph4j](https://github.com/langgraph4j/langgraph4j) |

## ⚠️ Java 25 — Project Loom: o detalhe que muda decisões de produção

Esta é a **correção** mais importante sobre o relatório inicial, que tratava tudo como "pronto para uso":

| Recurso | Status no JDK 25 | Implicação |
|---|---|---|
| **Virtual Threads** (_threads_ virtuais) | **FINAL** (desde o JDK 21) | Pode usar em produção sem flags. |
| **Scoped Values** (valores com escopo) | **FINAL** — JEP 506 | Pode usar em produção sem flags. |
| **Structured Concurrency** (concorrência estruturada) | **AINDA EM _PREVIEW_** — JEP 505 (5º _preview_) | Requer `--enable-preview`; **API ainda muda entre versões**. Use com consciência do risco; não é GA. |

Fontes: [InfoWorld — JDK 25](https://www.infoworld.com/article/3846172/jdk-25-the-new-features-in-java-25.html), [Inside.java](https://inside.java/2025/10/20/jdk-25-performance-improvements/), [JRebel — Java 25](https://www.jrebel.com/blog/java-25).

> 💡 **Por que isso importa no banco:** no Módulo 3 vimos que chamadas de tool paralelas pedem concorrência. _Virtual Threads_ e _Scoped Values_ (ambos **finais**) já resolvem a maior parte com segurança. _Structured Concurrency_ é a API mais elegante para "dispare N tools, junte os resultados, cancele todas se uma falhar" — mas, sendo **preview**, exige decisão consciente (flag + risco de mudança de API). Detalhamos no Módulo 11.

## 🔎 A verificar no momento certo (Módulo 10)

| Item | O que falta | Por quê |
|---|---|---|
| LangChain4j **embutido** no `micronaut-langchain4j 2.0.1` | O guia não declara a versão exata; indícios apontam para a trilha `1.14.x` (atrás do standalone `1.16.2`) | A integração costuma seguir **atrás** do standalone; confirmar no `pom`/catálogo ao montar o projeto |
| Módulo **agêntico** do LangChain4j (`langchain4j-agentic` / `AgenticServices`) | O `intro` lista "Agents and Agentic AI", mas não confirmei o nome exato do módulo/classe | Confirmar ao chegar na orquestração de agentes (Módulos 12/17) |

## Princípio

> **Nada nesta trilha sobre LangChain4j/Micronaut/Java é ensinado como fato sem uma destas linhas confirmadas — ou um aviso explícito de que está pendente de verificação.** É o Foundation First aplicado a versões.
