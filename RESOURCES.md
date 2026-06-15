# Sistemas Agênticos com LangChain4j — Resources

Fontes de alta confiança para fundamentar as lições. Conhecimento vem daqui, não de palpites paramétricos. Sabedoria vem das comunidades.

## Knowledge

- [Doc oficial — LangChain4j](https://docs.langchain4j.dev/)
  Documentação canônica. Use para: AiServices, tools, RAG, ChatMemory, guardrails, structured output.
- [Código-fonte — github.com/langchain4j/langchain4j](https://github.com/langchain4j/langchain4j)
  A fonte de verdade quando a doc é ambígua. Use para: **verificar a API/comportamento exato por versão** (fixamos a tag `1.16.2` para o Módulo 6).
- [Micronaut LangChain4j — guia oficial](https://micronaut-projects.github.io/micronaut-langchain4j/latest/guide/)
  Use para: integração `micronaut-langchain4j` (2.0.1), DI de compilação, configuração de modelos/beans.
- [LangChain4j — Amazon Bedrock (chat models)](https://docs.langchain4j.dev/integrations/language-models/amazon-bedrock) · [Bedrock embeddings](https://docs.langchain4j.dev/integrations/embedding-models/)
  **Caminho de invocação fixado do banco.** Use para: `BedrockChatModel`, embeddings via Bedrock (Titan/Cohere), config de região/credenciais. Conferir na fonte `langchain4j-bedrock` @ tag fixada.
- [AWS — Amazon Bedrock docs](https://docs.aws.amazon.com/bedrock/) · [Bedrock prompt caching](https://docs.aws.amazon.com/bedrock/latest/userguide/prompt-caching.html) · [Cross-region inference profiles](https://docs.aws.amazon.com/bedrock/latest/userguide/cross-region-inference.html)
  Fonte primária do provedor. Use para: model IDs / inference profiles do Claude, _prompt caching_ (cachePoint), Titan/Cohere embeddings, IAM (`bedrock:InvokeModel`), _usage_/contagem de tokens.
- [Micronaut Framework — release 5.0.0](https://micronaut.io/2026/05/20/micronaut-framework-5-0-0-released/) · [Java 25 baseline](https://micronaut.io/2026/04/27/micronaut-framework-5-0-with-java-25-baseline/)
  Use para: novidades do Micronaut 5, baseline Java 25, GraalVM.
- [JDK 25 — features (InfoWorld)](https://www.infoworld.com/article/3846172/jdk-25-the-new-features-in-java-25.html) · [Performance (Inside.java)](https://inside.java/2025/10/20/jdk-25-performance-improvements/)
  Use para: status de Virtual Threads (final), Scoped Values (final, JEP 506), Structured Concurrency (**preview**, JEP 505).
- [Anthropic — Writing tools for agents](https://www.anthropic.com/engineering/writing-tools-for-agents)
  Use para: design de tools (consolidar, descrições, "muitas tools", _tool search_).
- [OpenAI — Function calling guide](https://developers.openai.com/api/docs/guides/function-calling)
  Use para: design de funções, `strict`/Structured Outputs, contagem de tools por turno.
- [OWASP Top 10 for LLM Applications](https://genai.owasp.org/llm-top-10/)
  Use para: segurança — prompt injection, _insecure output handling_, _excessive agency_ (Módulo 13). _(Confirmar versão vigente ao chegar lá.)_
- [langgraph4j (comunidade)](https://github.com/langgraph4j/langgraph4j)
  Use para: orquestração de grafos/estado em Java (projeto de terceiros; funciona com LangChain4j e Spring AI).

## Wisdom (Communities)

- [LangChain4j — GitHub Discussions/Issues](https://github.com/langchain4j/langchain4j/discussions)
  Onde os mantenedores respondem. Use para: dúvidas de API, _gotchas_ de versão, comportamentos não documentados.
- [Micronaut — Discord/GitHub Discussions](https://github.com/micronaut-projects/micronaut-core/discussions)
  Use para: integração, DI de compilação, GraalVM nativo.
- [r/LocalLLaMA](https://reddit.com/r/LocalLLaMA) e [r/java](https://reddit.com/r/java)
  Direcional. Use para: tendências, comparação de abordagens (filtre _bro-science_).

> Preferência de comunidade do usuário: **ainda não declarada** — confirmar se deseja recomendações de fórum/Discord antes de insistir.

## Gaps (a preencher em fontes primárias quando chegarmos lá)
- Versão **exata** do LangChain4j embutida no `micronaut-langchain4j 2.0.1` (indício: trilha `1.14.x`) — confirmar no `pom`/catálogo (Módulo 10).
- Módulo agêntico do LangChain4j (`langchain4j-agentic` / `AgenticServices`) — confirmar nome de módulo/classe e API (Módulos 12/17).
- Suporte Java a **LangFuse** e às **OpenTelemetry GenAI semantic conventions** — aterrar no Módulo 15.
- Estudos de caso reais de LangChain4j em bancos — escassos; buscar fontes de engenharia confiáveis.
