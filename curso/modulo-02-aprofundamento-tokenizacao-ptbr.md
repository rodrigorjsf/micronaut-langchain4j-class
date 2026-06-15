# Módulo 2 — Aprofundamento: Tokenização pt-BR vs. Inglês e o Impacto no Custo

> Complemento da Seção 2.1. Aqui os números **não são estimados** — foram **medidos** com o `tiktoken` (biblioteca real de tokenização da OpenAI), comparando dois tokenizadores: `cl100k_base` (GPT-4 / GPT-3.5) e `o200k_base` (GPT-4o e posteriores, vocabulário maior e mais multilíngue).

## 1. O que foi medido (metodologia)

Tokenizei 5 frases bancárias **equivalentes** em inglês e português, mais um trecho de _system prompt_, com os dois tokenizadores. Para isolar variáveis, as frases pt-BR foram escritas **sem acentos** (o efeito dos acentos é medido à parte, na Seção 4) — ou seja, os números de inflação abaixo são um **piso**: com acentuação real, a inflação é um pouco maior.

> ⚠️ São tokenizadores da OpenAI. Modelos da Anthropic (Claude) e outros usam tokenizadores próprios, com contagens diferentes. Mas o **padrão** (português gasta mais tokens que inglês, e tokenizadores mais novos reduzem a diferença) **se mantém** em todos os tokenizadores BPE modernos. Use estes números como *ilustração da mecânica*, não como verdade exata para o seu modelo. **Importante:** o modelo-alvo deste curso é o **Claude Sonnet (200K)**, e a documentação oficial da Anthropic adverte que o `tiktoken` **subconta** o Claude em ~15–20% (mais em código e idiomas não-ingleses como o pt-BR) — logo a inflação real do português no Claude é **ainda maior** que a medida aqui (esta análise é *conservadora*). Para números exatos, use a API `count_tokens` (o Claude não tem tokenizador offline).

## 2. Resultado medido: a inflação do português

| Tokenizador | Tokens EN (5 frases) | Tokens PT | **Inflação** | System prompt (EN→PT) |
|---|---|---|---|---|
| `cl100k_base` (GPT-4/3.5) | 60 | 88 | **1,467×** | 26 → 32 (1,231×) |
| `o200k_base` (GPT-4o+) | 59 | 75 | **1,271×** | 26 → 31 (1,192×) |

Leitura: o mesmo conteúdo em português custa de **~27% a ~47% mais tokens** que em inglês, **dependendo do tokenizador**.

`★ Lição medida ─────────────────────────────────`
**Trocar de tokenizador cortou ~15% dos tokens do português** (88 → 75), enquanto o inglês quase não mudou (60 → 59). Ou seja: escolher um modelo com tokenizador moderno (vocabulário ~200k, mais multilíngue) é uma **alavanca de custo concreta e gratuita** para um produto em pt-BR — sem mudar uma linha do seu texto. O português é "penalizado" justamente por ser sub-representado no vocabulário; vocabulários maiores e mais multilíngues reduzem essa penalidade.
`─────────────────────────────────────────────────`

## 3. Por que isso acontece (a mecânica)

A tokenização BPE (*Byte Pair Encoding*) **aprende** seus "pedaços" a partir de um corpus de treino majoritariamente em inglês. Consequência:
- Palavras e subpalavras **inglesas frequentes** ganham um token próprio (ex.: `invoice`, `statement`, `account`).
- A **morfologia rica do português** — sufixos como `-ção`, `-mento`, `-ância`, e a infinidade de conjugações verbais — é sub-representada, então fragmenta em pedaços menores.

Veja como termos bancários em pt-BR se quebram (`o200k_base`, pedaços separados por `·`):

```
  Pix            1 tok  ->  Pix
  saldo          1 tok  ->  saldo
  boleto         2 tok  ->  bole·to
  fatura         2 tok  ->  f·atura
  cartão         2 tok  ->  cart·ão
  extrato        2 tok  ->  extr·ato
  investimento   2 tok  ->  invest·imento
  agendamento    2 tok  ->  ag·endamento
  comprovante    3 tok  ->  com·prov·ante
  financiamento  3 tok  ->  fin·anci·amento
  vencimento     3 tok  ->  v·enc·imento
```

`Pix` e `saldo` têm sorte (1 token). Já `comprovante`, `financiamento` e `vencimento` — termos que aparecem o tempo todo num assistente bancário — custam **3 tokens cada**.

## 4. O efeito dos acentos (diacríticos)

Em UTF-8, uma letra acentuada ocupa **mais de um byte**, e o BPE pode ou não ter aprendido a forma acentuada como token limpo. Medido (`o200k_base`):

| Sem acento | Tokens | Com acento | Tokens | Δ |
|---|---|---|---|---|
| `credito` | 1 | `crédito` | 2 | **+1** |
| `confirmacao` | 2 | `confirmação` | 3 | **+1** |
| `cartao` | 2 | `cartão` | 2 | 0 |
| `vencimento` | 3 | `vencimento` | 3 | 0 |
| `transferencia` | 2 | `transferência` | 2 | 0 |

O acento **às vezes** adiciona um token (`crédito`, `confirmação`), às vezes não. Como o português real é acentuado, a inflação de produção fica **acima** do piso medido na Seção 2.

## 5. O impacto no custo: três multiplicadores que se empilham

A inflação do português não age sozinha. Ela **multiplica** com outros dois fatores já vistos no Módulo 2:

1. **Inflação de idioma** (×1,27 a ×1,47): português gasta mais tokens.
2. **Prêmio da saída**: tokens de **saída custam mais** que os de entrada (ex.: 5×). E a resposta ao cliente é **obrigatoriamente** em pt-BR — você não consegue fugir da inflação no lado mais caro.
3. **Crescimento N²** (Seção 2.4): o histórico reenviado a cada turno faz o custo da conversa crescer quadraticamente — e cada token desse histórico já vem inflado pelo idioma.

> O resultado é que o "imposto do português" incide com mais força exatamente onde dói: na saída (mais cara) e no histórico que se acumula (N²).

## 6. Estratégias de mitigação (acionáveis)

| Estratégia | Por que funciona | Quanto economiza | Ressalva |
|---|---|---|---|
| **Escolher modelo com tokenizador moderno** | Vocabulário maior e mais multilíngue fragmenta menos o português. | **~15% medido** (cl100k→o200k) no mesmo texto pt-BR. | Depende do provedor; meça com o tokenizador real do seu modelo. |
| **Escrever o _overhead_ fixo em inglês** (system prompt, descrições de tools, nomes de campos) e instruir o modelo a **responder em pt-BR** | Esse bloco é enviado em **toda** chamada; em inglês ele encolhe ~20%. | ~19–23% medido no system prompt. | Modelos capazes seguem bem "instruções em inglês, resposta em pt-BR" — mas **teste**. Exemplos _few-shot_ que precisam ser em pt-BR continuam em pt-BR. |
| **Conter a verbosidade da saída** (`max_tokens`, estilo conciso) | Saída é inflada **e** mais cara por token. | Proporcional ao corte. | Não sacrifique clareza com o cliente. |
| **Gestão agressiva de contexto** (Módulo 14) | Corta o N² antes que ele multiplique a inflação. | Pode ser a maior economia de todas. | É um módulo inteiro; vem depois. |
| **Medir, não chutar** | Orçamento de tokens baseado em medição real (como esta). | Evita surpresas de custo em produção. | Embuta a contagem no _design_, não no pós-incidente. |

## 7. Resumo de uma frase

> Em pt-BR, **todo token conta mais** — e como o português infla justamente a saída (mais cara) e o histórico (N²), as decisões de tokenizador, idioma do _prompt_ fixo e gestão de contexto deixam de ser detalhe e viram **arquitetura de custo**.

---

> ➡️ Voltamos à trilha no **Módulo 3 — O loop agêntico e o _tool calling_**.
