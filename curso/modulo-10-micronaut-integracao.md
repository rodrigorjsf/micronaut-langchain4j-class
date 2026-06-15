# Módulo 10 — Integração `micronaut-langchain4j` (DI de compilação) + a versão real

> **Rascunho-fonte da Lição 12** (`lessons/0012-micronaut-integracao.html`). Aterrado na
> fonte da tag `v2.0.1` do `micronaut-langchain4j` + LangChain4j `1.15.1`.

Até aqui ensinamos a **API standalone do LangChain4j 1.16.2**. Agora ela entra no
**Micronaut 5** — e a primeira lição é uma verdade desconfortável **verificada na fonte**.

## 1 · A verdade da versão (manchete verificada)

`micronaut-langchain4j 2.0.1` **NÃO embarca 1.16.2** — o catálogo fixa
`managed-langchain4j = "1.15.1"`, `managed-langchain4j-community = "1.15.0-beta25"`,
`micronaut = "5.0.1"`. O `langchain4j-bom` importado é o **1.15.1**.

**O que fazer:** ou (a) ensinar/usar a superfície como **1.15.1** (as APIs centrais —
`@Tool`, `@P`, `AiServices`, `BedrockChatModel` — são estáveis entre 1.15 e 1.16), ou
(b) **sobrescrever o `langchain4j-bom` para 1.16.2** no seu build e **re-verificar os
deltas** (ex.: capability de JSON schema, framework de guardrails `@Experimental`,
`BedrockGuardrailConfiguration`, `promptCaching` — recursos que ensinamos em 1.16.2 podem
diferir/não existir em 1.15.1). Foundation First: **saber a versão que você realmente
recebe** é parte da competência.

## 2 · O que o `micronaut-langchain4j` faz por você (DI de compilação)

| Recurso | Como | Verificado |
| --- | --- | --- |
| Beans de modelo Bedrock | `@Lang4jConfig` em `BedrockModule` → processador gera `@ConfigurationProperties`/`@Factory` | `BedrockModule.java` |
| Declarar AI service | `@AiService` (interface) — bean com DI de compilação | `AiService.java` |
| Tools | `@Tool` em bean `@Singleton`; registradas em compilação por `ToolRegistry` (`ExecutableMethodProcessor`) | `ToolRegistry.java` |
| RAG automático | se houver beans `EmbeddingModel` **e** `EmbeddingStore`, o `AiServiceFactory` compõe `EmbeddingStoreContentRetriever` | `AiServiceFactory.java` |
| Memória | `ChatMemoryProvider` por bean; store default `InMemoryChatMemoryStore` (Redis/Neo4j/Cassandra = módulos separados) | `chatMemory.adoc` |

O modelo de chat produzido é `dev.langchain4j.model.bedrock.BedrockChatModel` (Converse API)
— exatamente o requisito "Claude via Bedrock, não a SDK direta".

## 3 · Configurar o Bedrock (armadilhas verificadas)

- **Prefixo código-verdade: `langchain4j.bedrock`** (chaves `langchain4j.bedrock.model`,
  `langchain4j.bedrock.region`). ⚠️ A doc oficial `bedrock.adoc` mostra
  `langchain4j.bedrock-llama` — **obsoleto/incorreto** para 2.0.1 (que não declara modelo
  Llama). Copiar a doc literalmente dá um prefixo que não funciona.
- **Autenticação = credenciais AWS, nunca api-key.** `credentialsProvider` é
  `injected=true, required=true` → você **deve** registrar um bean
  `software.amazon.awssdk.auth.credentials.AwsCredentialsProvider` (ex.: via `micronaut-aws`
  SDK v2). O `api-key` que aparece no `BedrockTest` é só um gatilho de ativação de teste.
- **Model default = `claude-3-haiku-20240307`** (alias). Em produção, defina um **model id /
  inference profile** explícito e atual via `langchain4j.bedrock.model`.

## 4 · `@AiService`, `@Tool` e a dívida do `@P` (resolvida)

- **`@AiService`** (`io.micronaut.langchain4j.annotation`): `value()`/`named()` selecionam o
  bean de modelo; `tools()` lista as classes de tools; `customizer()` permite ajustar o builder.
- **Tools só são fiadas se listadas** em `@AiService(tools={...})` — `getAllTools()` **não**
  é aplicado automaticamente. E os métodos `@Tool` **precisam estar em beans `@Singleton`**.
- **Dívida de verificação resolvida (`@P` + nomes de parâmetros):** em 1.15.1, `@P` **tem**
  `name()`. O **plugin Gradle do Micronaut adiciona `-parameters` por padrão** (PR #153) →
  nomes simples já funcionam. Mas um build **Maven puro sem** `<parameters>true</parameters>`
  gera `arg0/arg1` (confunde o modelo) → aí `@P(name=...)` é **obrigatório**.

## 5 · O assistente do banco, fiado por DI

```yaml
# application.yml — prefixo CÓDIGO-VERDADE para 2.0.1
langchain4j:
  bedrock:
    model: anthropic.claude-3-5-sonnet-20240620-v1:0   # explícito em prod (não o alias haiku)
    region: us-east-1
# autenticação = credenciais AWS → registre um AwsCredentialsProvider (micronaut-aws SDK v2)
```

```java
import io.micronaut.langchain4j.annotation.AiService;
import dev.langchain4j.service.SystemMessage;
import dev.langchain4j.agent.tool.Tool;
import dev.langchain4j.agent.tool.P;
import io.micronaut.context.annotation.Factory;
import jakarta.inject.Singleton;
import software.amazon.awssdk.auth.credentials.*;

@Factory
class AwsConfig {                                  // bean OBRIGATÓRIO p/ o Bedrock autenticar
    @Singleton AwsCredentialsProvider creds() { return DefaultCredentialsProvider.create(); }
}

@Singleton                                         // métodos @Tool DEVEM estar em @Singleton
class BankingTools {
    @Tool("Consulta o saldo de uma conta (nacional ou global)")
    String saldo(@P("numero da conta") String accountId, @P("escopo: NACIONAL|GLOBAL") String scope) { ... }

    @Tool("Transfere valor; exige idempotencyKey para evitar dupla execução")
    String transferir(@P("conta origem") String from, @P("conta destino") String to,
                      @P("valor em centavos") long amountCents,   // primitivo: required É validado em 1.x
                      @P("chave de idempotência") String idempotencyKey) {
        // confirmação + idempotência vivem AQUI (o framework só roteia a chamada)
    }
}

@AiService(tools = { BankingTools.class })         // tools SÓ entram se listadas aqui
interface BankingAssistant {
    @SystemMessage("Você é um assistente bancário. Nunca efetive transferências sem confirmação.")
    String chat(String userMessage);
}
// injete BankingAssistant em qualquer @Controller/@Singleton
```

## Quiz

1. **Qual versão do LangChain4j o `micronaut-langchain4j 2.0.1` resolve por padrão?**
   (a) 1.16.2, a mesma das lições standalone · (b) ✅ **1.15.1** (community 1.15.0-beta25) ·
   (c) a mais recente, baixada no build
2. **Uma classe `@Tool` não aparece para o modelo. Causa mais provável?**
   (a) ✅ não listada em `@AiService(tools={...})`, ou não é `@Singleton` ·
   (b) o Bedrock não suporta tool calling via Converse · (c) faltou `@Executable` manual
3. **Como o `BedrockChatModel` autentica sob `micronaut-langchain4j`?**
   (a) por `langchain4j.bedrock.api-key` · (b) ✅ por um bean `AwsCredentialsProvider` ·
   (c) pelo `modelId`, que embute o ARN

## Vá mais fundo

- **Guia oficial:** https://micronaut-projects.github.io/micronaut-langchain4j/latest/guide/ (ciente da divergência doc-vs-código do prefixo Bedrock).
- Fonte conferida @ `v2.0.1`: `gradle/libs.versions.toml` (versões), `BedrockModule.java`,
  `AiService.java`, `AiServiceFactory.java`, `ToolRegistry.java`, `Langchain4jConfigVisitor.java`;
  `@P` em `langchain4j 1.15.1`.
- **Aberto:** compatibilidade real do stack (Micronaut 5.0.1 / LC 1.15.1) sob **Java 25** não foi
  verificada — confirmar toolchain antes de produção.
- **Próximo (Lição 13):** Java 25 (virtual threads, scoped values, structured concurrency) para chamadas de tool em paralelo.
