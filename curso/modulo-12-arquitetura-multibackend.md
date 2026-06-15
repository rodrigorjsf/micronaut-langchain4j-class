# Módulo 12 — Arquitetura multi-backend do banco (agêntica, HITL, idempotência)

> **Rascunho-fonte da Lição 14** (`lessons/0014-arquitetura-multibackend.html`). Aterrado na
> fonte 1.16.2 do `langchain4j-agentic` + Maven Central.

O banco tem **vários backends** (conta nacional, conta global, cartão, investimentos) e
operações que **movem dinheiro**. Esta lição mostra como **compor** isso — e onde o framework
**não** te ajuda (e por que isso é correto).

## 1 · O módulo agêntico (e a armadilha de versão)

`★ Armadilha de versão verificada ───────────────`
O módulo é publicado **só** como **`dev.langchain4j:langchain4j-agentic:1.16.2-beta26`** —
**não existe** `langchain4j-agentic:1.16.2` puro no Maven Central (a tag git 1.16.2 serve o
código, mas não há artefato). Já o `langchain4j-bedrock` é **release puro 1.16.2**. No mesmo
build você usa **versões diferentes**: `bedrock=1.16.2`, `agentic=1.16.2-beta26`. O sufixo
`-beta` sinaliza **API instável** — fixe a versão exata e espere quebras entre betas.
`─────────────────────────────────────────────────`

`AgenticServices` (`public class`, não `final`) é o ponto de entrada, com fábricas estáticas:
`sequenceBuilder()`, `parallelBuilder()`, `loopBuilder()`, `conditionalBuilder()`,
`supervisorBuilder()`, `plannerBuilder()`, `humanInTheLoopBuilder()`, `agentBuilder()`,
`a2aBuilder()`, e `createAgenticSystem(Class[, ChatModel][, AgentConfigurator])`.

## 2 · O seam para o Bedrock + `@Agent` vs `@V`/`@P`

As sobrecargas que recebem `ChatModel` são o **encaixe** do `BedrockChatModel` (que
`implements ChatModel`) — Claude via Bedrock, sem SDK Anthropic direto.

**Distinção de ensino (pegadinha):**
- A **interface do agente** usa **`@V`** (lê variáveis do `AgenticScope` — saídas de agentes
  anteriores): `@Agent("...") String withdraw(@V("user") String u, @V("amount") Double a);`
- A **classe de tool** usa **`@P`** (descreve parâmetros da `@Tool` para o modelo):
  `@Tool("...") Double withdraw(@P("user name") String u, @P("amount") Double a);`

Trocar um pelo outro não funciona como esperado.

## 3 · Human-in-the-loop: genérico, sem semântica de dinheiro

Existem duas formas: a anotação **`@HumanInTheLoop`** (declarativa) e o **record
`HumanInTheLoop`** (programática, com `HumanInTheLoopBuilder`). Ambas são um mecanismo
**genérico** de "perguntar ao usuário" — **não há semântica de 'confirmação de dinheiro'
embutida**. O portão approve/deny é o **seu** `responseProvider`, que em produção precisa
carregar o **contexto da operação** (valor, contas origem/destino, idempotency key) para uma
decisão informada. O exemplo de 1 argumento do tutorial é didaticamente ingênuo.

## 4 · Idempotência + confirmação = ARQUITETURA, não API (a joia)

`★ Insight ─────────────────────────────────────`
**O framework não tem primitivo de idempotência nem de confirmação de dinheiro** (grep
exaustivo nos 141 arquivos do `langchain4j-agentic` 1.16.2: zero ocorrências de "idempoten";
só literais de exemplo `"user-approval"`/`"approved"` em javadoc). E isso é **correto**: mover
dinheiro com segurança é responsabilidade **determinística** da sua camada de tool/backend —
**dedupe por `transferId`/idempotency key** no `@Tool` ou no backend, e o gate de confirmação
na sua lógica (a `LoopAgentService.exitCondition` serve de porta determinística de
"retry-até-aprovar"). É o tema recorrente: **o modelo decide e sugere; o seu código valida,
autoriza e efetiva** (Lições 1, 9, 11).
`─────────────────────────────────────────────────`

## 5 · Nacional vs. global: suas tools, seu roteamento

Nada no módulo agêntico endereça o split nacional/global — modele como **tools distintas**
(uma fala com cada backend) ou roteie com `conditionalBuilder`/`supervisorBuilder`. O
paralelismo de leitura entra via `parallelBuilder` (ou o `executeToolsConcurrently` da Lição 13).

## 6 · Esboço (com a assimetria de versão)

```java
// bedrock = 1.16.2 (release)  |  agentic = 1.16.2-beta26 (experimental) — versões DIFERENTES no build
ChatModel claudeViaBedrock = BedrockChatModel.builder()
        .modelId("us.anthropic.claude-sonnet-4-5-20250929-v1:0").region(Region.US_EAST_1).build();

class BankTool {                                  // @Tool usa @P; idempotência é SUA
    @Tool("Withdraw amount for a user; returns new balance")
    Double withdraw(@P("user name") String user, @P("amount") Double amount) {
        // escolhe backend nacional vs global; aplica dedupe por idempotency key
        return /* novo saldo */ 0.0;
    }
}

interface BankAgent {                             // interface de agente usa @V
    @Agent("A banker that withdraws from an account")
    String withdraw(@V("user") String user, @V("amount") Double amount);

    @HumanInTheLoop(description = "Confirm money-moving operation", outputKey = "approval")
    String confirm(@V("user") String user, @V("amount") Double amount);
}

BankAgent bank = AgenticServices.createAgenticSystem(BankAgent.class, claudeViaBedrock);
```

## Quiz

1. **Como adicionar o módulo agêntico ao build?**
   (a) `langchain4j-agentic:1.16.2` (igual ao bedrock) · (b) ✅ `langchain4j-agentic:1.16.2-beta26`
   (só beta existe) · (c) já vem no agregado `langchain4j` 1.16.2
2. **Quem garante idempotência e confirmação numa transferência?**
   (a) o módulo agentic, via HumanInTheLoop e LoopAgentService · (b) o Bedrock Guardrails ·
   (c) ✅ **você**: dedupe por transferId no tool/backend; o gate é seu
3. **Na interface de um `@Agent`, como referenciar variáveis do escopo?**
   (a) com `@P`, a mesma anotação da tool · (b) ✅ com **`@V`** (lê do `AgenticScope`) ·
   (c) com `@MemoryId`

## Vá mais fundo

- **Tutorial oficial (agents):** https://docs.langchain4j.dev/tutorials/agents (usa caso bancário).
- Fonte 1.16.2: `AgenticServices.java`, `LoopAgentService.java`, `HumanInTheLoop.java` (record + anotação),
  `Agent.java`; Maven Central `maven-metadata.xml` (agentic só beta26; bedrock 1.16.2).
- **Aberto:** autoconfig do agentic via micronaut-langchain4j e compat. Java 25 — confirmar antes de produção.
- **Próximo (Lição 15):** segurança — prompt injection e o OWASP Top 10 para LLM.
