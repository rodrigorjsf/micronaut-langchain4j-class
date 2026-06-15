# Módulo 3 — O Loop Agêntico e o Tool Calling (detalhado)

> Parte 1 da trilha, ainda **sem framework**. Este é o módulo mais importante da fundação técnica: é aqui que um LLM "que só fala" (Módulo 1) vira um **agente que age**. Também é onde nascem **a maior parte dos bugs, custos e riscos** de um sistema agêntico real. Vamos devagar e fundo.

---

## 3.1 Relembrando o loop, agora a sério

No Módulo 1 desenhamos o ciclo ReAct (*Reasoning + Acting*): Pensar → Agir → Observar → repetir. Agora detalhamos o que **realmente** acontece, passo a passo, numa única pergunta do cliente:

```
            ┌───────────────────────────────────────────────┐
            │  Cliente: "Qual minha fatura e meu saldo?"     │
            └───────────────────────┬───────────────────────┘
                                    ▼
   (1) Você monta o prompt: system + DESCRIÇÕES DAS TOOLS + histórico + pergunta
                                    ▼
   (2) Chama o modelo  ───────────────────────────────►  MODELO
                                    ◄───────────────────────────────
   (3) Resposta do modelo é UMA de duas coisas:
        (a) texto final  → ACABOU, responde ao cliente
        (b) PEDIDO(S) de tool: getFatura(), getSaldo()  → continua
                                    ▼
   (4) SEU CÓDIGO valida → autoriza → executa as tools (backends do banco)
                                    ▼
   (5) Você anexa os RESULTADOS como novas mensagens na lista
                                    ▼
   (6) Volta ao passo (2) com a lista atualizada  ↺  (até o modelo dar texto final)
```

O ponto que quase todo iniciante erra: **o "loop" não é do modelo — é seu.** O modelo é uma função sem estado (Módulo 1) que você chama repetidamente. **Você** decide quando parar, valida cada passo e controla o que entra na mesa.

## 3.2 O protocolo de _function calling_, por baixo do capô

"Tool calling" (ou "function calling") é um protocolo. Os nomes exatos no fio (_wire format_) mudam por provedor (OpenAI usa `tool_calls`, Anthropic usa blocos `tool_use`), mas a estrutura é universal — e o LangChain4j vai abstrair tudo isso pra você (Módulo 6). A mecânica:

**Passo A — você declara as ferramentas.** Cada tool é descrita por: um **nome**, uma **descrição** em linguagem natural e um **esquema de parâmetros** (JSON Schema). Exemplo (formato neutro):

```json
{
  "name": "getFaturaCartao",
  "description": "Retorna a fatura atual do cartão de crédito do cliente autenticado.",
  "parameters": {
    "type": "object",
    "properties": {
      "mesReferencia": { "type": "string", "description": "Mês no formato YYYY-MM. Opcional; padrão = mês atual." }
    },
    "required": []
  }
}
```

**Passo B — o modelo responde com um pedido estruturado** (não com texto):

```json
{ "tool_calls": [ { "name": "getFaturaCartao", "arguments": { "mesReferencia": "2026-06" } } ] }
```

**Passo C — seu código executa e devolve o resultado como mensagem `tool`:**

```json
{ "role": "tool", "name": "getFaturaCartao",
  "content": { "valor": 2310.55, "vencimento": "2026-06-20", "status": "ABERTA" } }
```

**Passo D — você chama o modelo de novo**, agora com a fatura na mesa, e ele redige a resposta final em pt-BR.

> 💰 **Conexão com o Módulo 2:** as **descrições das tools são enviadas em TODA chamada** — elas vivem na janela de contexto. Um banco com dezenas de produtos pode ter dezenas de tools; isso é um custo fixo recorrente enorme. (Lembra do aprofundamento de tokenização? É por isso que descrições de tools em **inglês** economizam tanto.)

## 3.3 Como o modelo "decide" chamar uma tool

Aqui está a verdade desconfortável: **ele não "decide" no sentido humano.** Continua sendo predição do próximo token (Módulo 1). Os modelos são **treinados/ajustados** para emitir tokens de "pedido de ferramenta" quando o contexto sugere que uma ferramenta é útil. A "decisão" é **probabilística**, condicionada principalmente por:

1. **O nome e a descrição da tool** (é o que o modelo "lê" para saber que ela existe e para que serve).
2. **A mensagem do usuário** e o histórico.
3. **O system prompt** (que pode reforçar "sempre use ferramentas para dados de conta").

`★ Insight ─────────────────────────────────────`
**A qualidade da "decisão" do agente é, em grande parte, a qualidade das suas descrições de ferramentas.** Se `getSaldoContaGlobal` e `getSaldoContaNacional` têm descrições vagas ou parecidas, o modelo vai confundir qual chamar — e mostrar o saldo da conta errada. No mundo real, **a maior parte do "tuning" de um agente não é mexer no modelo: é reescrever nomes e descrições de tools** até a decisão ficar confiável. Isso é o Módulo 6 inteiro, e começa aqui.
`─────────────────────────────────────────────────`

## 3.4 Chamadas paralelas vs. sequenciais

Modelos modernos podem pedir **várias tools de uma vez** (paralelo) ou **encadear** (sequencial):

- **Paralelo** — as tools são independentes. _"Qual minha fatura e meu saldo?"_ → `getFatura()` **e** `getSaldo()` no mesmo passo. Seu código pode executá-las concorrentemente (guarde isso para o Módulo 11: _virtual threads_ e _structured concurrency_ do Java 25 brilham exatamente aqui).
- **Sequencial** — o resultado de uma alimenta a próxima. _"Mostre o extrato da conta onde caiu meu salário"_ → `descobrirContaSalario()` → e **só então** `getExtrato(contaId)`. O modelo precisa do primeiro resultado antes de formular o segundo pedido. Isso significa **mais viagens ao modelo** → mais latência (Módulo 2).

## 3.5 Os modos de falha (a parte do "mundo real")

É aqui que sistemas agênticos quebram em produção. Cada falha tem um nome e uma defesa:

| Falha | O que é | No banco | Defesa |
|---|---|---|---|
| **Sub-chamada (_under-calling_)** | O modelo **não** chama a tool e responde da "memória" (que é nula/desatualizada) | Inventa um saldo em vez de consultar → **catastrófico** | System prompt forte + nunca confiar em dado factual sem tool; validação de saída (Módulo 9) |
| **Alucinação de ferramenta** | Pede uma tool que **não existe** | Chama `getLimitePix` quando só existe `getPix` | Seu código rejeita tools desconhecidas e devolve erro ao modelo |
| **Alucinação de argumento** | Inventa valores/parâmetros | Passa um `clienteId` inventado, ou `mesReferencia: "2026-13"` | Validação de esquema + regras de negócio **antes** de executar |
| **Sobre-chamada (_over-calling_)** | Chama tools desnecessárias | Consulta 5 backends para um "oi" | Boas descrições; o modelo aprende quando *não* agir |
| **Loop infinito** | Continua chamando tools sem convergir | Reconsulta a fatura 20 vezes | **Teto de iterações** (você impõe), detecção de repetição |
| **Entidade errada** | Usa o ID/contexto de outra pessoa | Mostra a conta do cliente 999 | **Vínculo de identidade no servidor** (ver 3.6) — nunca deixar o modelo fornecer a identidade |
| **Caminho infeliz não tratado** | A tool falha (timeout, erro, vazio) e o loop não sabe lidar | Backend da conta global fora do ar | Devolver o **erro como resultado de tool** para o modelo reagir; _fallback_/escalonamento |

> ⚠️ **A sub-chamada é a mais perigosa num banco.** Um modelo que "acha" que sabe o saldo e responde sem consultar produz uma resposta **confiante e errada** sobre dinheiro. A defesa é cultural e técnica: o agente é instruído a tratar **todo** dado factual de conta como algo que *só* pode vir de tool, e a saída é validada.

## 3.6 O loop de controle é SEU (e onde ficam as travas)

O modelo propõe; **o seu código dispõe**. Entre o passo (3) e o (4) do fluxo, há uma camada determinística que você controla:

1. **Validação de esquema** — os argumentos batem com o JSON Schema? Tipos certos, campos obrigatórios presentes?
2. **Regras de negócio** — `mesReferencia` não pode ser futuro; valor de Pix dentro do limite; etc.
3. **Autorização** — este cliente pode acessar esta conta/produto? (Determinístico, nunca delegado ao modelo.)
4. **Teto de iterações e _timeouts_** — máximo de N passos; tempo máximo por tool e por turno.
5. **Idempotência** — para ações que mudam estado (Módulo 12).
6. **Observabilidade** — registrar cada passo (Módulo 15).

`★ Insight (o mais importante do módulo) ─────────`
**Parâmetros de identidade/segurança NÃO vêm do modelo — vêm do seu contexto de sessão autenticado.** Note que, na Seção 3.2, a tool `getFaturaCartao` **não tem** um parâmetro `clienteId`. Isso é proposital. O `clienteId` é injetado pelo **seu código**, a partir do _token_ de sessão autenticado, *depois* que o modelo pede a tool. O modelo só fornece a **intenção** (qual produto, qual mês) — nunca **quem é o cliente**. Por quê? Porque o modelo pode ser **enganado** (prompt injection, Módulo 13) a passar o ID de outra pessoa. Se a identidade nunca está nas mãos do modelo, esse ataque morre na fundação. Regra de ouro: **o modelo carrega intenção; o servidor carrega identidade e autorização.**
`─────────────────────────────────────────────────`

## 3.7 Tools de leitura vs. tools de ação (a distinção que salva bancos)

Nem toda ferramenta é igual:

- **Tools de leitura** (`getSaldo`, `getFatura`, `getExtrato`): consultam, são (idealmente) idempotentes e seguras. Podem ser executadas automaticamente quando o modelo pede.
- **Tools de ação / escrita** (`fazerPix`, `agendarPagamento`, `contratarFinanciamento`): **movem dinheiro ou mudam estado**. Estas **não podem** ser executadas só porque o modelo pediu.

Para tools de ação, o fluxo ganha travas extras (detalhadas no Módulo 12): **confirmação explícita do usuário**, **idempotência** (para não pagar o boleto duas vezes se o loop repetir), **autorização reforçada** e, às vezes, **humano no circuito** (_human-in-the-loop_). 

> 💡 Princípio: **leitura o agente pode propor e executar; ação o agente só pode *propor* — a execução exige uma porta determinística com confirmação.**

## 3.8 Um trace detalhado (a lista de mensagens crescendo)

Cliente: _"Mostre o extrato da conta onde caiu meu salário e veja se já posso pagar a fatura."_ Acompanhe a **lista de mensagens** (a "mesa") evoluindo:

```
[1] system:    "Você é o assistente do Banco X... use tools para dados de conta..."
[2] user:      "Mostre o extrato da conta do salário e se posso pagar a fatura."
       │  → chamada 1 ao modelo
[3] assistant: tool_calls: [ descobrirContaSalario() ]            (sequencial: precisa do ID antes)
[4] tool:      descobrirContaSalario() -> { contaId: "NAC-771" }
       │  → chamada 2 ao modelo
[5] assistant: tool_calls: [ getExtrato("NAC-771"), getFaturaCartao() ]   (agora paralelo)
[6] tool:      getExtrato -> { ...lançamentos... }
[7] tool:      getFaturaCartao -> { valor: 2310.55, vencimento: "2026-06-20" }
       │  → chamada 3 ao modelo
[8] assistant: "Seu salário caiu na conta NAC-771. O extrato mostra saldo de R$ 4.800.
                Sua fatura é R$ 2.310,55 (vence 20/06) — você tem saldo para pagá-la."  ← TEXTO FINAL
```

Três viagens ao modelo, quatro execuções de tool, a mesa crescendo a cada passo. Note como **custo e latência (Módulo 2) se acumulam** a cada ida — e por que, na Parte 3, vamos querer executar `[5]` em paralelo com _virtual threads_.

## 3.9 ReAct "clássico" vs. _function calling_ nativo (evolução)

Vale saber a história, porque você verá os dois nomes:

- **ReAct clássico (2022):** convencia-se o modelo, **via prompt**, a escrever texto no formato `Thought: ... / Action: ... / Observation: ...`, e o código **fazia _parsing_ desse texto**. Frágil: o modelo errava o formato, e o _parsing_ quebrava.
- **_Function calling_ nativo (hoje):** o modelo foi **treinado** para emitir os pedidos de tool de forma **estruturada** (JSON), sem depender de _parsing_ de texto livre. Muito mais confiável.

O LangChain4j usa o mecanismo nativo quando o provedor suporta. A ideia conceitual (Pensar→Agir→Observar) é a mesma; a **implementação** evoluiu de "parsear texto" para "receber estrutura".

## 3.10 Prévia: um agente ou vários?

Tudo acima descreve **um** agente com várias tools. Para sistemas grandes (como um banco com produtos muito distintos), surge a pergunta: um agente gigante com 40 tools, ou **vários agentes especializados** (um para cartões, um para investimentos, um para Pix) coordenados por um **orquestrador/supervisor**? Cada abordagem tem custos e riscos próprios. Isso é a arquitetura do Módulo 12 — por ora, guarde que **"mais tools na mesma mesa" piora a decisão e o custo**, e que dividir para conquistar é uma ferramenta de design.

## 3.11 Glossário-resumo

| Termo | Em uma frase |
|---|---|
| **Function calling / Tool calling** | Protocolo onde o modelo emite pedidos estruturados de ferramenta. |
| **Tool definition** | Nome + descrição + JSON Schema dos parâmetros. |
| **tool_call / tool_result** | O pedido do modelo / o resultado que seu código devolve. |
| **Chamada paralela / sequencial** | Várias tools de uma vez / encadeadas (uma depende da outra). |
| **Under-calling / Over-calling** | Não chamar quando deveria / chamar à toa. |
| **Alucinação de tool/argumento** | Inventar ferramenta inexistente / valores inválidos. |
| **Teto de iterações** | Limite de passos que **você** impõe ao loop. |
| **Tool de leitura vs. de ação** | Consulta segura vs. operação que muda estado/dinheiro. |
| **Vínculo de identidade no servidor** | Identidade/autz vêm da sessão, nunca do modelo. |

## ✅ Checagem de entendimento

1. Por que dizemos que "o loop é seu, não do modelo"?
2. Por que a tool `getFaturaCartao` **não** recebe `clienteId` como parâmetro? Que ataque isso previne?
3. Qual modo de falha é o mais perigoso num banco, e por quê?
4. Diferença entre chamada **paralela** e **sequencial** — dê um exemplo bancário de cada.
5. Por que tools de **ação** (fazerPix) não podem ser executadas só porque o modelo pediu?
6. Como um erro de backend (timeout) deve "entrar" no loop para o modelo poder reagir?

> ➡️ **Próximo:** Módulo 4 — RAG a fundo (embeddings, bancos vetoriais, _chunking_, _retrieval_; quando RAG e quando tool). Último módulo da fundação antes de entrarmos no LangChain4j (Parte 2) — onde acionaremos o **B**: verificação das versões reais.
