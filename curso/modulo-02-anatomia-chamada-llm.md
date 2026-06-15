# Módulo 2 — Anatomia de uma Chamada a um LLM

> Parte 1 da trilha, ainda **sem framework**. No Módulo 1 entendemos *o que* um LLM é. Aqui abrimos o capô: o que realmente acontece — e o que realmente custa — em **uma única chamada**. Sem isso, conceitos como "gestão de janela de contexto" (o tema crítico do Módulo 14) seriam decorados, não compreendidos.

---

## 2.1 Token e tokenização: a moeda do sistema

No Módulo 1 dissemos que o LLM "prevê o próximo token". Agora: **o que é um token?**

Um **token** não é uma palavra nem uma letra — é um **pedaço de texto** (uma _subword_, "subpalavra"). Os modelos usam um algoritmo de **tokenização** (geralmente **BPE**, *Byte Pair Encoding* / Codificação por Pares de Bytes) que quebra o texto em pedaços frequentes.

Heurística prática (para inglês): **1 token ≈ 4 caracteres ≈ ¾ de uma palavra**. Exemplos aproximados:

| Texto | Tokens (aprox.) | Por quê |
|---|---|---|
| `Pix` | 1 | palavra curta e frequente |
| `agendamento` | 3–4 | palavra longa, quebrada em pedaços |
| `R$ 2.310,55` | 5–7 | dígitos e pontuação tokenizam mal |
| `clienteId=987654321` | 8–11 | IDs numéricos viram muitos tokens |

`★ Insight ─────────────────────────────────────`
**Dois fatos com consequências diretas no banco:**
1. **Português custa mais que inglês.** Os tokenizadores são treinados majoritariamente em inglês, então o mesmo significado em português costuma gastar **mais tokens** (frequentemente 15–30% a mais). Seu assistente brasileiro é, por construção, mais caro por mensagem — isso muda cálculos de custo e de janela de contexto.
2. **Números e IDs são "caros" e frágeis.** `clienteId=987654321` explode em muitos tokens, e o modelo *raciocina mal sobre dígitos* (ele vê pedaços, não o número). Por isso **nunca** confie no LLM para fazer aritmética financeira ou comparar valores monetários "de cabeça" — isso é trabalho do seu código (tool), não do modelo. O modelo *orquestra*; a calculadora é determinística.
`─────────────────────────────────────────────────`

## 2.2 A janela de contexto, agora em números

A "mesa de trabalho" do Módulo 1 tem um tamanho medido em tokens, e ela é **compartilhada entre entrada e saída**:

```
janela de contexto = tokens de ENTRADA (prompt)  +  tokens de SAÍDA (resposta)
```

- **Tokens de entrada (_prompt tokens_):** system prompt + descrições das tools + histórico + resultados de tools + a pergunta.
- **Tokens de saída (_completion tokens_):** o que o modelo gera.

Se a janela é, digamos, de 128 mil tokens e sua entrada já ocupa 125 mil, sobram só 3 mil para a resposta — mesmo que o modelo "saiba" responder mais. **Entrada e saída disputam o mesmo orçamento.** Esse é o coração do Módulo 14.

## 2.3 Os parâmetros que você controla

Cada chamada tem "botões". Os que mais importam:

| Parâmetro | O que faz | Recomendação no banco |
|---|---|---|
| **temperature** (temperatura) | Aleatoriedade da escolha do próximo token. `0` ≈ mais determinístico/previsível; valores altos ≈ mais criativo/variado. | **Baixa** (ex.: 0–0,3) para respostas factuais e transacionais. Você não quer criatividade ao informar um saldo. |
| **top_p** (amostragem por núcleo) | Alternativa à temperatura: limita a escolha aos tokens que somam `p` de probabilidade. | Ajuste **um** dos dois (temperature *ou* top_p), não ambos. |
| **max_tokens** | Teto de tokens da **saída**. | Defina sempre — controla custo, latência e evita respostas que estouram a janela. |
| **stop sequences** (sequências de parada) | Texto que faz o modelo parar de gerar. | Útil para cortar respostas em formatos específicos. |
| **seed** (semente) | Tenta tornar a saída reproduzível. | Ajuda em testes, mas **não garante** determinismo total (ver 2.7). |

> 💡 **Por que temperatura baixa no banco?** "Sua fatura fechou em R$ 2.310,55, vence em 20/06" não admite variação. Já um assistente de _brainstorm_ de marketing se beneficiaria de temperatura alta. O parâmetro deve seguir a **tarefa**.

## 2.4 Custo: por que gestão de contexto É gestão de custo

A cobrança é **por token**, e quase sempre com preços **diferentes** para entrada e saída — **saída costuma custar várias vezes mais** que entrada.

> ⚠️ Os números abaixo são **ilustrativos** (preços reais variam por provedor e mudam com frequência; não os trate como fato). Servem para mostrar a *mecânica*.

Suponha (ilustrativo): entrada a US$ 3,00 por milhão de tokens, saída a US$ 15,00 por milhão. Um turno típico do assistente:

| Componente | Tokens |
|---|---|
| System prompt + descrições de todas as tools | ~500 |
| Histórico da conversa | ~800 |
| Resultado de tools (extrato + fatura) | ~1.200 |
| Pergunta do cliente | ~30 |
| **Total de entrada** | **~2.530** |
| Resposta gerada | ~250 (saída) |

Custo ≈ (2.530 × US$3 + 250 × US$15) / 1.000.000 ≈ **US$ 0,0114** por turno. Parece nada — mas **multiplique por milhões de turnos/dia** e por uma conversa que reenvia o histórico crescente a cada mensagem (limitação "sem estado" do Módulo 1!), e o custo explode de forma **quadrática** ao longo de uma conversa longa.

`★ Insight ─────────────────────────────────────`
**A armadilha do "sem estado" vira uma conta de luz.** Como o modelo não tem memória, reenviamos o histórico inteiro a cada turno. Numa conversa de N mensagens, o turno N reenvia ~N mensagens. Somando todos os turnos, o custo cresce com **N²**, não com N. É por isso que "gestão da janela de contexto" (Módulo 14) não é refinamento acadêmico — é a diferença entre um produto viável e um que queima dinheiro. As técnicas (resumir o passado, recuperar só o relevante, janelas de memória) são, na prática, **estratégias de custo**.
`─────────────────────────────────────────────────`

## 2.5 Latência: por que demora, e onde demora

Uma chamada tem duas fases com características distintas:

1. **Prefill (pré-preenchimento):** o modelo "lê" toda a entrada. Custa proporcional ao **tamanho da entrada**. É o que determina o **TTFT** (*Time To First Token* / Tempo Até o Primeiro Token).
2. **Decode (geração):** o modelo produz a saída **um token por vez**, em sequência. Custa proporcional ao **tamanho da saída**, medido em **tokens por segundo**.

Implicações no banco:
- Um system prompt gigante e um histórico enorme **atrasam o primeiro token** (prefill longo) — o cliente encara a tela "pensando...".
- Uma resposta longa **atrasa o fim** (decode é sequencial e não paraleliza por token).
- Encadear várias tools (Módulo 1.4) significa **várias chamadas em série** → latências que se somam. O assistente que compara CDB e financiamento pode fazer 3–4 viagens ao modelo.

## 2.6 Streaming: a resposta token a token

Como o decode é sequencial, podemos **transmitir cada token assim que sai** (_streaming_), em vez de esperar a resposta inteira. É por isso que chats de IA "digitam" na sua frente.

Benefício: **TTFT percebido** despenca — o cliente vê texto surgindo rápido, mesmo que a resposta completa demore. É quase puramente uma vitória de **experiência do usuário (UX)**.

> ⚠️ **Tensão que reaparece no Módulo 9 (guardrails):** se você já está *mostrando* os tokens ao cliente, você **ainda não validou a resposta completa**. Como aplicar um _guardrail_ de saída (ex.: "nunca revele o número completo do cartão") sobre algo que já está aparecendo na tela? Streaming e validação de saída brigam entre si — um trade-off de arquitetura real, não um detalhe.

## 2.7 Determinismo: o mesmo prompt, respostas diferentes

Por padrão, LLMs são **não determinísticos**: a mesma entrada pode gerar saídas diferentes (por causa da amostragem probabilística e de detalhes de hardware/ponto flutuante). Mesmo com `temperature=0` e `seed`, a reprodutibilidade **total não é garantida**.

Consequência prática (que detalhamos no Módulo 15, Avaliação): você **não pode** testar um agente como testa uma função pura com `assertEquals`. Testar IA exige outra mentalidade — avaliação por critérios, _LLM-as-judge_ (LLM como juiz), conjuntos de avaliação — porque a "resposta certa" é uma faixa, não um valor único.

## 2.8 Juntando tudo: a anatomia de um turno do banco

Cliente digita: _"Quanto foi minha última fatura e quanto rende meu CDB?"_

1. **Montagem do prompt (entrada):** system prompt (~500) + descrições das tools (já dentro dos 500) + histórico (~800) + pergunta (~30).
2. **1ª chamada → prefill + decode:** o modelo decide chamar **duas** tools (`getFaturaCartao`, `getRendimentoCDB`). TTFT depende dos ~1.330 tokens de entrada.
3. **Seu código executa as tools** (backends diferentes — cartão e investimentos), devolve ~1.200 tokens de resultado.
4. **2ª chamada → prefill maior** (agora com os resultados na mesa, ~2.530 tokens) **+ decode** da resposta final (~250 tokens, possivelmente em streaming).
5. **Custo e latência** = soma das duas viagens. **Note:** a mesa cresceu, a próxima pergunta partirá de uma base ainda maior.

Tudo o que faremos em LangChain4j (Parte 2) é, no fundo, **automatizar e gerenciar bem esse fluxo** — sem perder o controle sobre tokens, custo, latência e o que entra na mesa.

## 2.9 Glossário-resumo

| Termo | Em uma frase |
|---|---|
| **Token** | Pedaço de texto (subpalavra); unidade de processamento e de cobrança. |
| **Tokenização / BPE** | Algoritmo que quebra texto em tokens. |
| **Prompt tokens / completion tokens** | Tokens de entrada / de saída; disputam a mesma janela. |
| **temperature** | Botão de aleatoriedade; baixa = previsível, alta = criativa. |
| **max_tokens** | Teto da saída; controla custo e latência. |
| **TTFT** (Tempo Até o Primeiro Token) | Atraso até o primeiro token; dominado pela fase de prefill. |
| **Prefill / Decode** | Ler a entrada / gerar a saída token a token. |
| **Streaming** | Transmitir tokens conforme saem; melhora a UX percebida. |
| **Não determinismo** | Mesmo prompt pode gerar saídas diferentes. |

## ✅ Checagem de entendimento

1. Por que o seu assistente em **português** tende a custar mais por mensagem que um em inglês?
2. Por que o custo de uma **conversa longa** cresce de forma ~quadrática, e qual limitação do Módulo 1 causa isso?
3. Por que `temperature` baixa faz sentido para informar um saldo, mas não para um _brainstorm_?
4. Qual a diferença entre **prefill** e **decode**, e como cada um afeta a latência?
5. Por que **streaming** entra em conflito com **guardrails de saída**?

> ➡️ **Próximo:** Módulo 3 — O loop agêntico e o _tool calling_ (como o modelo "decide" chamar uma ferramenta, o protocolo de function calling, e por que o agente pode entrar em loop ou alucinar chamadas). Ainda sem framework.
