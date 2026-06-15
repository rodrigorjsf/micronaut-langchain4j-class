# Glossário — Sistemas Agênticos com LangChain4j

A linguagem canônica deste workspace. Toda lição e registro de aprendizado deve aderir a estes termos. Cresce e é revisado conforme o entendimento se aprofunda.

## Fundamentos (agnósticos de framework)

**LLM (Large Language Model / Modelo de Linguagem de Grande Porte)**:
Função que prevê o próximo _token_ de texto; estática (conhecimento congelado no treino), sem estado e que só produz texto.
_Avoid_: "a IA", "o modelo que pensa"

**Token**:
Menor unidade de texto que o modelo processa (uma _subpalavra_); é também a unidade de cobrança e de medição da janela de contexto.

**Tool (Ferramenta)**:
Função do seu código que você descreve ao modelo e que ele pode **pedir** para executar; o modelo nunca a executa, só a solicita.
_Avoid_: "função do modelo", "plugin"

**Agente (Agent)**:
Um LLM operando dentro de um **loop** que usa _tools_ para cumprir um objetivo (Pensar → Agir → Observar → repetir).

**Janela de contexto (Context window)**:
A "mesa de trabalho" finita, medida em _tokens_, onde tudo que o modelo enxerga (instruções, histórico, descrições de tools, resultados) precisa caber de uma vez. Entrada e saída disputam o mesmo orçamento.

**System prompt**:
A "constituição" do agente: papel, regras e limites. É uma **instrução, não um cofre** — não é barreira de segurança.

**RAG (Retrieval-Augmented Generation / Geração Aumentada por Recuperação)**:
Recuperar trechos de conhecimento relevantes e injetá-los na janela de contexto para fundamentar a resposta. Para conhecimento; _tools_ para dados vivos/ação.

**Embedding**:
Vetor numérico que representa o **significado** de um texto; textos de sentido parecido ficam próximos no espaço vetorial.

**Prompt injection (Injeção de instruções)**:
Texto malicioso na janela de contexto que finge ser instrução. **Direto** (na mensagem do usuário) ou **indireto** (escondido em documento de RAG ou resultado de tool).

**Tool de leitura vs. de ação**:
Leitura consulta e é idempotente (pode executar quando o modelo pede); ação muda estado/dinheiro (exige confirmação, idempotência e autorização reforçada).

**Identidade-pelo-servidor**:
Princípio de que parâmetros de identidade/autorização (ex.: `clienteId`) vêm da sessão autenticada, **nunca** dos argumentos fornecidos pelo modelo.

## LangChain4j

**LangChain4j**:
Biblioteca Java idiomática (não um _port_ do LangChain Python) com API unificada sobre provedores de LLM e _vector stores_, _tool calling_ (incl. MCP), RAG e agentes.

**AiServices**:
API de **alto nível**: você declara uma interface Java anotada e o framework gera a implementação, rodando o loop agêntico por você.

**ChatModel / StreamingChatModel**:
API de **baixo nível**: você monta as mensagens e controla o loop manualmente.

**`@Tool`**:
Anotação de método que o expõe como ferramenta. `name()` = nome (padrão: nome do método); `value()` = **descrição** (um `String[]`).

**`@P`**:
Anotação de parâmetro de tool (descrição/nome); todo parâmetro é **obrigatório por padrão**.

**`@ToolMemoryId` / `@MemoryId`**:
Par que injeta o _memory id_ (identidade da sessão) num parâmetro de tool — a materialização da identidade-pelo-servidor.

**ChatMemory**:
Mecanismo que reenvia o histórico (o modelo é sem estado); ex.: `MessageWindowChatMemory` (janela de N mensagens).

**`langchain4j-bom`**:
_Bill of Materials_ que alinha as versões dos módulos; deve ser sempre importado (versionamento duplo: estável + beta).

**`ToolProvider`**:
SPI que fornece _tools_ dinamicamente por invocação (`provideTools(request)`); `isDynamic()` (padrão `false`) re-avalia a cada chamada do loop. É o **substrato comum** do _tool-search_ e das _skills_.

**Tool retrieval (RAG-sobre-tools)**:
Expor só as _tools_ relevantes ao turno em vez do catálogo inteiro. Dois caminhos: **embutido** (`ToolSearchStrategy`, o **modelo** dispara a busca) ou **escrito à mão** (um `ToolProvider` que embute a **mensagem do usuário**).

**`ToolSearchStrategy` / `VectorToolSearchStrategy`**:
Mecanismo **embutido** (1.16.2, `@Experimental`) de _tool-search_: injeta o meta-tool `tool_search_tool`; o modelo formula a _query_; a busca vetorial revela as _tools_. Liga via `.toolSearchStrategy(...)` no `AiServices`.

**`SearchBehavior`**:
Enum com `SEARCHABLE` (padrão) e `ALWAYS_VISIBLE`. **Com** uma estratégia anexada, `SEARCHABLE` fica oculto até ser encontrado; **sem** estratégia, tudo permanece visível.

## Agent Skills (langchain4j-skills)

**`langchain4j-skills`**:
Módulo Java (`@Experimental`/beta) que implementa o padrão aberto **Agent Skills** (formato `SKILL.md`) **sobre o `ToolProvider`**. Coordenada em _lockstep_ com o core: `X.Y.Z-betaN` depende de core `X.Y.Z` (resolva via `langchain4j-bom`). Modelo-agnóstico → roda no Bedrock.

**Skill / `SKILL.md`**:
Um diretório com um `SKILL.md`: _front matter_ YAML (`name`+`description`, sempre visíveis) + corpo Markdown de instruções + recursos opcionais (`references/`, `scripts/`). `Skill` é **interface** — **não existe anotação `@Skill`**.

**Progressive disclosure (revelação progressiva)**:
Mostrar só `name`+`description` no catálogo e carregar o corpo **sob demanda** — a disciplina de orçamento de contexto aplicada a **instruções**, não só a _tools_.

**`activate_skill` / `read_skill_resource`**:
_Tools_ geradas pelo módulo: a primeira carrega o corpo do `SKILL.md` no contexto; a segunda lê um recurso. A ativação é rastreada em memória (atributo `activated_skill`); o modelo nunca toca o _filesystem_.

## Micronaut / Java

**DI de compilação (Micronaut)**:
Injeção de dependências resolvida em **tempo de compilação** (via _annotation processor_), sem reflexão em _runtime_ — _startup_ rápido, baixa memória, compatível com GraalVM nativo.

**Virtual Threads / Scoped Values / Structured Concurrency**:
Recursos de concorrência do Project Loom. No Java 25: Virtual Threads e Scoped Values são **finais**; Structured Concurrency ainda é **_preview_** (JEP 505).
