# Módulo 5 — Arquitetura do LangChain4j: `AiServices` (alto nível) vs. `ChatModel` (baixo nível)

> **Parte 2 — início.** A partir daqui, tudo se apoia em [`referencia-versoes-2026-06.md`](./referencia-versoes-2026-06.md) (versões verificadas em fonte primária). Os Módulos 1–4 (fundação) são a base: você vai reconhecer **cada** conceito do framework como algo que já entendeu de forma agnóstica.

---

## 5.1 O que é o LangChain4j (e o que NÃO é)

**Confirmado na fonte oficial** ([docs.langchain4j.dev/intro](https://docs.langchain4j.dev/intro)):

> *"Despite the name, LangChain4j is not a Java port of LangChain (Python) — it is built for Java, not ported to it."*

Traduzindo a importância: **não tente mapear seu conhecimento de LangChain Python 1:1.** Não há código compartilhado, nem numeração de versão comum, nem os mesmos nomes de classe. O LangChain4j pegou **ideias** (chains, RAG, agents, tools) e as reimplementou de forma **idiomática em Java**. Quem chega do Python procurando `LCEL` (o operador `|`) ou `Runnable` não os encontra — encontra **interfaces Java anotadas**.

O que ele é, em uma frase: uma **biblioteca Java de código aberto** que oferece uma **API unificada** sobre dezenas de provedores de LLM e de _vector stores_, e que torna fáceis **tool calling** (inclusive **MCP** — *Model Context Protocol*), **RAG** e **agentes**.

Fatos de versão (ver referência): standalone estável **1.16.2**, **JDK mínimo 17**, **versionamento duplo** (estável + beta) — **sempre importe o `langchain4j-bom`** e não fixe versões de módulo à mão.

## 5.2 Os dois níveis de API (a decisão de arquitetura central)

O LangChain4j oferece **duas camadas**. Entender a diferença é entender o framework inteiro:

| | **Baixo nível: `ChatModel`** | **Alto nível: `AiServices`** |
|---|---|---|
| O que você faz | Monta as mensagens, chama o modelo, trata a resposta, **roda o loop de tools você mesmo** | Declara uma **interface Java anotada**; o framework **gera a implementação** |
| Mapeia ao... | Loop manual do **Módulo 3** (você é o dono do loop) | O framework roda o loop do Módulo 3 **por você** |
| Controle | Máximo | Conveniência máxima |
| Quando usar | Casos especiais, controle fino do fluxo, _streaming_ customizado | A **maioria** dos casos |

`★ Insight ─────────────────────────────────────`
**O `AiServices` não é "mágica" — é o loop do Módulo 3 embrulhado.** Quando você vê `String resposta = assistente.conversar(...)` retornar já com dados de conta dentro, lembre: por baixo, o framework montou o prompt, enviou as descrições das tools, recebeu os `tool_calls`, executou seus métodos `@Tool`, devolveu os resultados ao modelo e repetiu até o texto final — exatamente o fluxo `[1]…[8]` que rastreamos no Módulo 3. A fundação não foi perdida; ela está **escondida atrás da anotação**. Por isso aprendemos o loop manual *antes*: para nunca tratar o `AiServices` como caixa-preta.
`─────────────────────────────────────────────────`

## 5.3 `AiServices` na prática (API verificada na doc oficial)

A doc oficial ([tutorials/ai-services](https://docs.langchain4j.dev/tutorials/ai-services)) mostra o padrão. Você **declara uma interface**:

```java
interface Assistant {
    String chat(String userMessage);
}
```

E o framework gera a implementação (um _proxy_):

```java
Assistant assistant = AiServices.create(Assistant.class, model);
// ou, com mais controle:
Assistant assistant = AiServices.builder(Assistant.class)
    .chatModel(model)
    .build();
```

Aplicando ao **assistente do banco**, com as quatro peças da fundação encaixadas:

```java
interface AssistenteBanco {

    @SystemMessage("You are the virtual assistant of Bank X. "       // ← system prompt (Módulo 1.6)
        + "Use tools for any account data; never invent balances. "  //   (em inglês: economia de tokens, Módulo 2)
        + "Never reveal another customer's data. "
        + "Answer in Brazilian Portuguese.")                         //   responde em pt-BR
    String conversar(@MemoryId String clienteId,                    // ← memória por cliente (Módulo 1.3 / 7)
                     @UserMessage String pergunta);                  // ← mensagem do usuário
}

AssistenteBanco assistente = AiServices.builder(AssistenteBanco.class)
    .chatModel(model)
    .tools(new FerramentasBanco())                                  // ← @Tool: tool calling (Módulo 3)
    .chatMemoryProvider(id -> MessageWindowChatMemory.withMaxMessages(20)) // ← janela de memória (Módulo 2/7)
    .contentRetriever(retriever)                                    // ← RAG (Módulo 4)
    .build();
```

Cada linha é um conceito que você **já domina**:

| Peça do `AiServices` | Anotação / método | Módulo da fundação |
|---|---|---|
| Instrução de sistema | `@SystemMessage` (aceita `fromResource`, `systemMessageProvider`) | 1.6 (camadas da conversa) |
| Mensagem do usuário / templates | `@UserMessage`, `@V("nome")` | 1.6 |
| Ferramentas | `@Tool` + `.tools(...)` | 3 (loop agêntico) |
| Memória (e por usuário) | `.chatMemoryProvider(...)`, `@MemoryId`, `MessageWindowChatMemory` | 1.3 / 2 (custo N²) / 7 |
| RAG | `.contentRetriever(...)` ou `.retrievalAugmentor(...)` | 4 |
| Saída estruturada | tipo de retorno do método (ex.: um `record`) | 9 (próximos módulos) |

> 💡 Note o `@MemoryId String clienteId`: a **memória é isolada por cliente**. Isso conecta com o Módulo 3 (identidade vem do servidor) e com o Módulo 2 (cada cliente tem sua própria "mesa" que cresce — e que você precisa gerenciar, Módulo 7).

## 5.4 Quando descer ao baixo nível (`ChatModel`)

Use `AiServices` por padrão. Desça ao `ChatModel`/`StreamingChatModel` quando precisar de: controle fino do loop (ex.: lógica de confirmação humana **entre** o `tool_call` e a execução — crítico para `fazerPix`, Módulo 3.7/12), _streaming_ com pós-processamento token a token (a tensão com guardrails do Módulo 2.6/9), ou orquestração que o alto nível não expressa bem. Na prática, muitos sistemas bancários **misturam**: alto nível para leitura, baixo nível para ações sensíveis.

## 5.5 O encaixe no Micronaut (prévia do Módulo 10)

Aqui entra a diferença que torna a combinação Micronaut + LangChain4j especial. No Micronaut, você **não instancia o `AiServices` na mão** como acima — você declara a interface e o **_annotation processor_ de compilação** (`micronaut-langchain4j-processor`, confirmado) **gera o _bean_ em tempo de compilação**, sem reflexão em tempo de execução.

`★ Insight ─────────────────────────────────────`
**Micronaut faz injeção de dependências em tempo de COMPILAÇÃO, não de execução.** Spring monta os _beans_ via reflexão quando a aplicação sobe; Micronaut **gera o código** dos _beans_ durante o `javac`. Para um backend agêntico bancário isso significa: **_startup_ quase instantâneo, menor consumo de memória e compatibilidade nativa com GraalVM** (imagem nativa) — qualidades valiosas para escalar horizontalmente sob carga e cortar custo de infraestrutura. É um casamento de filosofias: LangChain4j também favorece configuração declarativa, e o Micronaut materializa isso sem o custo de _runtime_ do Spring.
`─────────────────────────────────────────────────`

> ⚠️ **Honestidade de fundação:** a anotação Micronaut exata para declarar o serviço de IA e a fiação completa (configuração de modelos, _beans_ de tools) eu mostro **com código verificado no Módulo 10**, junto da confirmação de qual LangChain4j o módulo `2.0.1` embute (ver pendências na referência de versões). Não vou afirmar a sintaxe exata antes de checá-la.

## 5.6 Glossário-resumo

| Termo | Em uma frase |
|---|---|
| **`AiServices`** | API de alto nível: interface anotada → implementação gerada (roda o loop por você). |
| **`ChatModel` / `StreamingChatModel`** | API de baixo nível: você controla mensagens e o loop. |
| **`@SystemMessage` / `@UserMessage` / `@V`** | System prompt / mensagem do usuário / variável de template. |
| **`@Tool` / `.tools(...)`** | Declara e registra ferramentas (Módulo 3). |
| **`@MemoryId` / `ChatMemoryProvider`** | Memória isolada por usuário. |
| **`.contentRetriever` / `.retrievalAugmentor`** | Plugue de RAG (Módulo 4). |
| **`langchain4j-bom`** | _Bill of Materials_: alinha as versões dos módulos. Use sempre. |
| **DI de compilação (Micronaut)** | _Beans_ gerados no `javac`, sem reflexão em _runtime_. |

## ✅ Checagem de entendimento

1. Por que é um erro mapear o conhecimento de LangChain Python 1:1 para o LangChain4j?
2. O `AiServices` "esconde" qual fluxo que você já aprendeu? Cite os passos.
3. Na construção do `AssistenteBanco`, aponte qual linha corresponde a cada um dos Módulos 1, 2, 3 e 4.
4. Quando você desceria do `AiServices` para o `ChatModel` num banco?
5. Qual a vantagem da DI de compilação do Micronaut para um backend agêntico que precisa escalar?

> ➡️ **Próximo:** Módulo 6 — Tools (`@Tool`): design, granularidade, nomes e descrições de ferramentas (onde o Módulo 3.3 vira prática), e o tratamento de erros de tool. Começamos a transformar os produtos do banco em ferramentas bem desenhadas.
