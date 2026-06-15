# Módulo 6 — Tools (`@Tool`): Design, Granularidade, Nomes e Descrições

> **Parte 2.** Dividido em duas metades: **Parte A — princípios de design** (agnósticos de framework, construídos sobre o Módulo 3.3 — esta seção) e **Parte B — a API `@Tool` do LangChain4j** (aterrada por verificação, anexada adiante). Os princípios valem para qualquer framework ou linguagem; a API é o detalhe que os materializa.

---

# Parte A — Princípios de Design de Ferramentas

No Módulo 3.3 estabelecemos a tese central: **a qualidade da "decisão" do agente é, em grande parte, a qualidade dos nomes e descrições das suas tools.** Aqui transformamos essa tese em regras de design. Tudo gira em torno de um público inusitado: **o leitor das suas tools é o modelo**, não um humano.

## 6A.1 Granularidade: nem grossa demais, nem fina demais

A pergunta de design nº 1: **o que é "uma" ferramenta?**

- **Grossa demais (_coarse_):** `getCartaoCompleto()` que devolve fatura + limite + lançamentos + benefícios num único JSON gigante.
  - Problema: cada chamada despeja milhares de tokens na mesa (custo/latência, Módulo 2), a maior parte irrelevante para a pergunta, e ainda piora a resposta por "ruído" (perdido no meio).
- **Fina demais (_fine_):** `getLimiteDisponivel()`, `getLimiteTotal()`, `getLimiteUtilizado()`, `getDataFechamento()`… vinte micro-tools.
  - Problema: vinte descrições na mesa **toda chamada** (Módulo 3.2), mais decisões para o modelo errar, mais viagens sequenciais (latência).

**A medida certa (_Goldilocks_):** uma tool = **uma capacidade que faz sentido para o usuário**. `getFaturaCartao()`, `getLimiteCartao()`, `getLancamentosCartao(periodo)`.

`★ Insight ─────────────────────────────────────`
**Desenhe tools ao redor das INTENÇÕES do usuário, não da forma da sua API de backend.** É tentador espelhar 1:1 os _endpoints_ REST que já existem no banco — mas o modelo não pensa em _endpoints_, pensa em intenções ("quero ver minha fatura"). Uma tool que combina duas chamadas de backend numa capacidade limpa, ou que divide um _endpoint_ gordo em duas tools focadas, quase sempre melhora a decisão do agente. A camada de tools é uma **fachada (_facade_) projetada para o modelo**, não um espelho do seu backend.
`─────────────────────────────────────────────────`

## 6A.2 Nomes: verbo + substantivo, inequívocos e distintos

O nome é a primeira coisa que o modelo lê. Regras:
- **Verbo + substantivo:** `getFaturaCartao`, `agendarPagamentoBoleto`, `fazerPix`.
- **Inequívoco e distinto:** lembre do Módulo 3.3 — se duas tools têm nomes/descrições parecidos, o modelo confunde. `getSaldoContaNacional` vs. `getSaldoContaGlobal` precisam ser **claramente** distintos.

Surge aqui uma decisão de arquitetura recorrente no nosso banco (nacional vs. global):

| Abordagem | Exemplo | Prós | Contras |
|---|---|---|---|
| **Duas tools distintas** | `getSaldoNacional()`, `getSaldoGlobal()` | Decisão explícita; descrições podem divergir; roteamento de backend trivial | Dobra a contagem de tools (×2 para cada produto → "muitas tools", 6A.7) |
| **Uma tool parametrizada** | `getSaldo(tipoConta: NACIONAL\|GLOBAL)` | Menos tools na mesa; uma descrição | O modelo precisa preencher o parâmetro certo; risco de pôr o errado |

> 💡 Regra prática: quando os produtos têm **regras e backends realmente diferentes** (caso do nacional vs. global), tools distintas costumam dar **decisões mais confiáveis**; quando a diferença é só um filtro, a tool parametrizada com **enum** (que **restringe** os valores possíveis) é mais enxuta. Decida produto a produto.

## 6A.3 Descrições: você está escrevendo para o modelo

A descrição é o que o modelo usa para decidir **se** e **quando** chamar. Uma boa descrição diz:
1. **O que** a tool faz.
2. **Quando usá-la** (e, crucialmente, **quando NÃO**).
3. **Unidades e formatos** (moeda, datas em ISO, fuso).
4. **Efeitos colaterais** (se move dinheiro/estado).

```
RUIM:  "Retorna fatura."
BOM:   "Retorna a fatura ATUAL (em aberto) do cartão de crédito do cliente
        autenticado, com valor em BRL e data de vencimento (ISO-8601).
        Use para perguntas sobre o valor/vencimento da fatura corrente.
        NÃO use para faturas de meses anteriores — para isso, use
        getFaturaCartao(mesReferencia)."
```

`★ Insight ─────────────────────────────────────`
**No mundo real, ~80% do "tuning" de um agente é reescrever descrições de tools — não trocar o modelo nem mexer em hiperparâmetros.** Quando o agente chama a tool errada, traz a conta errada ou deixa de chamar quando deveria, a primeira (e quase sempre a única) correção necessária é tornar as descrições mais precisas e mutuamente exclusivas. Trate suas descrições de tools como **código de produção versionado e testado**, porque é exatamente o que elas são: a "lógica de decisão" do seu agente vive nelas.
`─────────────────────────────────────────────────`

## 6A.4 Parâmetros: mínimos, tipados, e sem identidade

Herdando o Módulo 3.6 (o insight mais importante daquele módulo):
- **Sem parâmetros de identidade/segurança.** `getFaturaCartao` **não** recebe `clienteId` — o servidor o injeta da sessão autenticada. O modelo só fornece **intenção** (qual mês), nunca **quem é o cliente**.
- **Mínimos.** Cada parâmetro é uma chance de o modelo alucinar um valor (Módulo 3.5). Menos é mais.
- **Tipados e restritos.** Use **enums** (`tipoConta: NACIONAL|GLOBAL`) para fechar o espaço de valores; datas em **ISO-8601**; descreva cada parâmetro (na Parte B veremos a anotação que faz isso).
- **Validados antes de executar.** Esquema + regras de negócio + autorização (Módulo 3.6), sempre na sua camada determinística.

## 6A.5 Valores de retorno: pequenos, moldados, e com erro como dado

O retorno da tool **vira tokens na mesa** (Módulo 3.2). Princípios:
- **Pequeno e moldado.** Não devolva o JSON cru do backend (gigante, vaza campos internos e **PII**, custa tokens). Devolva **só o necessário**, já moldado: `{ valor: 2310.55, moeda: "BRL", vencimento: "2026-06-20", status: "ABERTA" }`.
- **Estruturado e estável.** Um formato consistente ajuda o modelo a interpretar.
- **Erro como dado, não como exceção que mata o loop.** Se o backend global cai, a tool deve devolver algo como `{ erro: "BACKEND_GLOBAL_INDISPONIVEL", mensagem: "Conta global temporariamente indisponível." }` — para o modelo **reagir** (pedir desculpas, sugerir tentar depois, escalar), em vez de o loop estourar (Módulo 3.5, caminho infeliz). *(Como o LangChain4j faz isso por baixo é tema da Parte B.)*

> ⚠️ **Minimização de dados é segurança.** Quanto menos a tool devolve, menos PII entra no contexto do LLM (e em logs/traces). "Devolver só o necessário" não é só economia — é privacidade (Módulo 13).

## 6A.6 Tools de leitura vs. de ação (Módulo 3.7, agora no design)

Separe e sinalize:
- **Leitura** (`getSaldo`, `getFatura`): idempotentes, seguras, podem ser executadas quando o modelo pede.
- **Ação** (`fazerPix`, `agendarPagamentoBoleto`, `contratarFinanciamento`): movem dinheiro/estado → exigem **confirmação explícita**, **idempotência** e **autorização reforçada** (Módulo 12). 

Uma convenção de nomes que ajuda humanos **e** o modelo: verbos de consulta (`get…`, `consultar…`) vs. verbos de ação (`fazer…`, `agendar…`, `contratar…`).

## 6A.7 O problema das "muitas tools"

Nosso banco tem **todos** os produtos: boleto, DDA, Pix, Super Extrato, cartão/fatura, compras, shopping, financiamento, investimentos — × (nacional **e** global). Mapeado ingenuamente, isso são **dezenas de tools**, e **cada descrição vai na mesa em toda chamada** (Módulo 3.2). Consequências: custo fixo alto e **decisões piores** (o modelo se confunde entre muitas opções parecidas).

Mitigações (várias se aprofundam no Módulo 12):
- **Agrupar** por domínio e enxugar descrições.
- **Vários agentes especializados** sob um orquestrador (um agente de cartões, um de investimentos, um de Pix) — cada um vê **só as suas** tools (Módulo 12).
- **Seleção dinâmica de tools (_tool retrieval_ / RAG-sobre-tools):** recuperar, por similaridade com a pergunta, **apenas** as tools relevantes para expor naquele turno — RAG (Módulo 4) aplicado ao próprio catálogo de ferramentas.
- **Namespacing** claro (`cartao.getFatura`, `pix.enviar`).

## 6A.8 Mapeando os produtos do banco em tools (exemplo)

| Produto | Tools de leitura | Tools de ação |
|---|---|---|
| Cartão de crédito | `getFaturaCartao(mes?)`, `getLimiteCartao`, `getLancamentosCartao(periodo)` | `pagarFaturaCartao` (ação!) |
| Pix | `getLimitePix(tipoConta)`, `getChavesPix` | `fazerPix` (ação!) |
| Boleto / contas | `consultarBoleto(linhaDigitavel)` | `agendarPagamentoBoleto`, `pagarBoleto` (ação!) |
| Investimentos | `getRendimentoCDB`, `getPosicaoInvestimentos` | `aplicarInvestimento`, `resgatarInvestimento` (ação!) |
| Extrato / saldo | `getSaldo(tipoConta)`, `getSuperExtrato(periodo, tipoConta)` | — |
| Financiamento | `getFinanciamentos`, `simularFinanciamento` | `contratarFinanciamento` (ação!) |
| DDA | `getDebitosDDA` | `autorizarDebitoDDA` (ação!) |

Note como **nacional vs. global** vira um parâmetro `tipoConta` na maioria das leituras — e como as colunas separam claramente o que o agente **pode executar** do que ele só **pode propor**.

## ✅ Checagem de entendimento (Parte A)

1. Por que `getCartaoCompleto()` (uma tool grossa) é um problema de custo **e** de qualidade?
2. Quando preferir duas tools distintas (nacional/global) vs. uma parametrizada com enum?
3. Qual é o "público" das descrições de tools, e por que ~80% do tuning de um agente mora nelas?
4. Por que o retorno de uma tool deve ser moldado e pequeno (cite as razões de custo, qualidade e privacidade)?
5. Liste três formas de mitigar o problema de "muitas tools" num banco com todos os produtos.

---

# Parte B — A API `@Tool` do LangChain4j

> **Aterrada por verificação:** todos os símbolos abaixo foram conferidos **contra o código-fonte da tag `1.16.2`** no GitHub (não da memória). Fontes ao final. Onde um fato vem só da documentação (e não do código), está marcado.

## 6B.1 As três anotações

```java
import dev.langchain4j.agent.tool.Tool;          // @Tool   (no método)
import dev.langchain4j.agent.tool.P;             // @P      (no parâmetro)
import dev.langchain4j.agent.tool.ToolMemoryId;  // @ToolMemoryId (no parâmetro)
```

| Anotação | Atributos verificados (1.16.2) | Notas |
|---|---|---|
| **`@Tool`** | `String name()` (padrão = nome do método); `String[] value()` (a **DESCRIÇÃO**, várias entradas juntadas em multilinha); e três `@Experimental`: `returnBehavior()` (padrão `TO_LLM`), `searchBehavior()`, `metadata()` | `@Target(METHOD)` |
| **`@P`** | `description()` / `value()` (**aliases** — use um), `name()`, `boolean required()` **padrão `true`**, `defaultValue()` | `@Target(PARAMETER)` |
| **`@ToolMemoryId`** | (sem atributos) injeta o _memory id_ no parâmetro | par com `@MemoryId` do AI Service |

`★ Pegadinha verificada (não erre isto) ─────────`
**`@Tool.value()` é a DESCRIÇÃO, não o nome — e é um `String[]`, não `String`.** O nome é `@Tool.name()`, que por padrão é o nome do método. Muita gente (e muitos tutoriais) trocam os dois. E **todo parâmetro `@P` é obrigatório por padrão** (`required = true`); para torná-lo opcional, use `@P(required = false)`, um `defaultValue`, ou um `Optional<T>`.
`─────────────────────────────────────────────────`

## 6B.2 Tipos permitidos e como o retorno chega ao modelo

**Parâmetros:** primitivos, _boxed_ (`Integer`…), **enums**, POJOs e **records** (inclusive aninhados), tipos polimórficos (`sealed`), `List`/`Set`/`Map`, `Optional<T>` (torna opcional), ou **zero** parâmetros. Parâmetros injetados pelo framework (`@ToolMemoryId`) **não** são preenchidos pelo modelo.

**Retorno** (verificado no javadoc de `Tool.java`): o método pode retornar **qualquer** tipo, inclusive `void`.

| Retorno | O que é enviado ao modelo |
|---|---|
| `void` | a string literal `"Success"` |
| `String` | enviada **como está** (sem conversão) |
| qualquer outro (record, POJO, `Map`, coleção…) | **serializado em JSON** |
| multimodal (`Image`, `Content`…) | enviado como conteúdo multimodal (só em alguns provedores — _docs_) |

> 💡 Isso confirma a regra da Parte A (6A.5): retorne um **`record` enxuto** (vira JSON pequeno e estável) em vez do JSON cru do backend.

## 6B.3 O assistente do banco com tools reais

```java
class FerramentasBanco {

    private final ContaService contas;   // sua camada determinística (auth, roteamento de backend)

    @Tool("Returns the credit card invoice (amount in BRL, due date ISO-8601) for the "
        + "authenticated customer's CURRENT cycle. Use for the current invoice; "
        + "do NOT use for past months.")
    FaturaResumo getFaturaCartao(@ToolMemoryId String clienteId) {        // ← identidade INJETADA, não vinda do modelo
        return contas.faturaAtual(clienteId);                            //   retorna um record pequeno → vira JSON
    }

    @Tool("Returns the account balance for the authenticated customer.")
    SaldoResumo getSaldo(@ToolMemoryId String clienteId,
                         @P("Account scope to query") TipoConta tipoConta) {  // ← enum restringe os valores
        return contas.saldo(clienteId, tipoConta);
    }
}

record FaturaResumo(double valor, String moeda, String vencimento, String status) {}
record SaldoResumo(double saldo, String moeda) {}
enum TipoConta { NACIONAL, GLOBAL }
```

`★ Insight (o Módulo 3.6 vira mecanismo concreto) ─`
**`@ToolMemoryId` é exatamente a "identidade vem do servidor, nunca do modelo".** Lembre do Módulo 5: declaramos `conversar(@MemoryId String clienteId, ...)`. Esse `clienteId` — que **você** vincula à sessão autenticada — flui automaticamente para o `@ToolMemoryId String clienteId` da tool. **O modelo nunca toca nesse valor**; ele só escolhe `tipoConta`. Assim, o ataque "engana o modelo para passar o ID de outro cliente" (Módulo 3.5) **não tem superfície**: o ID não está nas mãos do modelo. Atenção honesta: a garantia vem de **você** fazer `memoryId = identidade autenticada` — o framework só transporta; a segurança é da sua decisão de _binding_.
`─────────────────────────────────────────────────`

## 6B.4 Tratamento de erros — o coração da robustez (e um risco de banco)

Aqui o LangChain4j tem comportamentos-padrão que **você precisa conhecer e, num banco, quase sempre sobrescrever**:

| Situação | Padrão na linha 1.x (verificado) | O que fazer no banco |
|---|---|---|
| **`@Tool` lança exceção** | AiServices **captura** e envia `e.getMessage()` ao modelo (para ele se corrigir). **Não** propaga ao chamador. | ⚠️ **Vaza dado interno/PII** para o modelo e a conversa. **Sobrescreva** com `toolExecutionErrorHandler` e devolva mensagem **sanitizada**; logue a causa real via `context.rawError()`. |
| **Argumentos inválidos** (JSON malformado, obrigatório faltando) | Caminho **separado**; padrão é **lançar/abortar** | Trate com `toolArgumentsErrorHandler` (retornar texto para o modelo tentar de novo, ou abortar). |
| **Tool alucinada** (nome inexistente) | `hallucinatedToolNameStrategy` → padrão `THROW_EXCEPTION` (aborta) | Forneça um `Function` que devolva `ToolExecutionResultMessage.from(req, "...")` para o modelo se recuperar. |
| **Loop sem fim** | `maxToolCallingRoundTrips(int)` → **padrão 100** | Reduza para um teto sensato (ex.: 6–8) para limitar custo (Módulo 2/3.6). |

Montando o assistente com essas travas (API verificada):

```java
AssistenteBanco assistente = AiServices.builder(AssistenteBanco.class)
    .chatModel(model)
    .tools(new FerramentasBanco(contaService))
    .chatMemoryProvider(id -> MessageWindowChatMemory.withMaxMessages(20))
    .maxToolCallingRoundTrips(8)                              // teto de loop (padrão 100)
    .toolExecutionErrorHandler((error, ctx) -> {             // NUNCA vaze e.getMessage() ao modelo
        log.error("Tool falhou", ctx.rawError());            // causa real só no log do servidor
        return ToolErrorHandlerResult.text("A operação não pôde ser concluída agora.");
    })
    .hallucinatedToolNameStrategy(req ->
        ToolExecutionResultMessage.from(req, "Error: no tool called " + req.name()))
    .build();
```

`★ Ponto de atenção verificado (armadilha do null) ─`
**Na linha 1.x, um parâmetro-objeto obrigatório que falta é passado como `null` SILENCIOSAMENTE** (só primitivos faltando lançam `ToolArgumentsException`). Num banco, isso significa que um `accountId` nulo pode entrar na sua tool sem erro. **Valide objetos críticos defensivamente dentro do corpo da tool** — não confie no `@P(required=true)` para garantir presença. (Isso, e os padrões de erro acima, estão **marcados para mudar no LangChain4j 2.0** — reconfirme na sua versão fixada.)
`─────────────────────────────────────────────────`

## 6B.5 `ReturnBehavior`, registro e tools dinâmicas

- **`ReturnBehavior`** (`@Experimental`): `TO_LLM` (padrão — resultado volta ao modelo, loop continua) vs. `IMMEDIATE`/`IMMEDIATE_IF_LAST` (curto-circuita e devolve o resultado direto ao chamador; exige tipo de retorno `Result` no método do AI Service). Qualquer erro de tool **desliga** o retorno imediato.
- **Registro** — `.tools(Object...)` / `.tools(Collection)` é o caminho recomendado (anotações). Existem também `.tools(List<AiServiceTool>)` e `.tools(Map<ToolSpecification, ToolExecutor>)` para o caminho programático.
- **Tools dinâmicas** — `.toolProvider(ToolProvider)` resolve a Seção 6A.7 ("muitas tools"): você expõe **só** as tools relevantes ao turno (o _tool retrieval_/RAG-sobre-tools), em vez de despejar dezenas de descrições na mesa. Conecta com **MCP** (Módulo 5/17).

## 6B.6 O que os fornecedores confirmam (valida a Parte A)

A pesquisa cruzou a doc oficial com guias da Anthropic e da OpenAI — e eles **convergem** com os princípios da Parte A:
- **Anthropic** ("Writing tools for agents"): *"More tools don't always lead to better outcomes"*; **consolide** tools em vez de envolver cada _endpoint_ (ex.: `transfer_funds` em vez de `list_accounts`+`validate`+`create_transfer`); retorne **só informação de alto sinal**; descreva a tool *"como você descreveria para um novo contratado"*. A precisão de seleção **degrada bastante acima de ~30–50 tools** → use _tool search_/RAG-sobre-tools.
- **OpenAI** (function calling): *"Aim for fewer than 20 functions available at the start of a turn"* (sugestão leve); **`strict: true`** (Structured Outputs) garante conformidade de esquema; *"don't make the model fill arguments you already know"* (= nosso `@ToolMemoryId`!); *"use enums... to make invalid states unrepresentable"*.

> Ou seja: os ~80% de tuning em descrições (6A.3), a consolidação (6A.1) e a identidade-pelo-servidor (6A.4/6B.3) não são opinião — são consenso dos dois maiores fornecedores **e** da doc do LangChain4j.

## 6B.7 Pendência honesta para o Módulo 10 (Micronaut)

O `@P` tem uma sutileza: sem a opção `-parameters` do `javac`, a reflexão vê `arg0`/`arg1` em vez do nome real do parâmetro — por isso Quarkus e Spring ativam `-parameters` por padrão. **Para o Micronaut (DI de compilação), preciso confirmar** se o _annotation processor_ já preserva os nomes ou se você deve usar `@P(name = "...")`. Não vou afirmar sem checar — fica para o Módulo 10, com código verificado.

## 📚 Fontes (Parte B)

- Código-fonte tag 1.16.2: [`Tool.java`](https://raw.githubusercontent.com/langchain4j/langchain4j/1.16.2/langchain4j-core/src/main/java/dev/langchain4j/agent/tool/Tool.java), [`P.java`](https://raw.githubusercontent.com/langchain4j/langchain4j/1.16.2/langchain4j-core/src/main/java/dev/langchain4j/agent/tool/P.java), [`ToolMemoryId.java`](https://raw.githubusercontent.com/langchain4j/langchain4j/1.16.2/langchain4j-core/src/main/java/dev/langchain4j/agent/tool/ToolMemoryId.java), [`ReturnBehavior.java`](https://raw.githubusercontent.com/langchain4j/langchain4j/1.16.2/langchain4j-core/src/main/java/dev/langchain4j/agent/tool/ReturnBehavior.java), [`AiServices.java`](https://raw.githubusercontent.com/langchain4j/langchain4j/1.16.2/langchain4j/src/main/java/dev/langchain4j/service/AiServices.java)
- [Doc oficial — Tools](https://docs.langchain4j.dev/tutorials/tools/)
- [Anthropic — Writing tools for agents](https://www.anthropic.com/engineering/writing-tools-for-agents) · [OpenAI — Function calling](https://developers.openai.com/api/docs/guides/function-calling)

## ✅ Checagem de entendimento (Parte B)

1. `@Tool.value()` é o nome ou a descrição da tool? E qual o tipo dele?
2. Por que `@ToolMemoryId` é a materialização do "identidade vem do servidor" (Módulo 3.6)?
3. Qual o **risco de banco** no comportamento-padrão de exceção de tool na linha 1.x, e como mitigá-lo?
4. Qual a "armadilha do null" em parâmetros-objeto, e por que ela exige validação defensiva?
5. Como `toolProvider`/_tool retrieval_ resolve o problema de "muitas tools" (6A.7)?

> ➡️ **Próximo:** Módulo 7 — `ChatMemory` e gestão da janela de contexto (o tema **crítico**): janelas de memória, sumarização, _token budgeting_ e o combate ao custo N² (Módulo 2) na prática do LangChain4j.
