# Módulo 13 — Segurança: prompt injection e o OWASP LLM Top 10 (2025)

> **Rascunho-fonte da Lição 15** (`lessons/0015-seguranca-owasp.html`). Aterrado verbatim na
> fonte OWASP (`2_0_vulns/*.md`) + genai.owasp.org.

A lição-capstone de segurança: ela **costura** as defesas das lições anteriores (1, 7, 9, 10,
11) no padrão de mercado — o **OWASP Top 10 para Aplicações LLM, edição 2025 (v2.0)**.

## 1 · A edição certa (corrige o mito)

A edição **atual** é **2025 (v2.0)**. **Não existe** edição 2026 *de Aplicações LLM* — o
"2026" é o **OWASP Top 10 for Agentic Applications** (ASI Top 10, IDs `ASI##`), projeto
**separado** (lançado dez/2025). **Novos** em 2025 vs. 2023/24: **LLM07 System Prompt Leakage**
e **LLM08 Vector and Embedding Weaknesses**. Prompt Injection é o **#1 (LLM01)** nas duas edições.

## 2 · LLM01 Prompt Injection: direta vs. indireta

- **Direta** (verbatim): *"a user's prompt input directly alters the behavior of the model"* —
  o cliente digitando um jailbreak no chat.
- **Indireta** (verbatim): *"an LLM accepts input from external sources, such as websites or
  files"* — a **variante RAG**, a mais fácil de subestimar: instrução maliciosa escondida no
  **dado ingerido** (um PDF de extrato, um campo de memo/descrição de transação, o corpo de um
  ticket). E (verbatim) *"prompt injections do not need to be human-visible/readable, as long
  as the content is parsed by the model"*.

## 3 · O mapa: OWASP 2025 → cenário do banco → defesa

| # (2025) | Cenário no banco | Defesa (lição) |
| --- | --- | --- |
| **LLM01** Prompt Injection | jailbreak no chat; instrução escondida num extrato ingerido | guardrails de entrada (L11); segregar conteúdo externo; teste adversarial |
| **LLM02** Sensitive Information Disclosure | vazar dados da conta global / de outro cliente | **authz server-side + filtro por cliente (L9)**; sanitização |
| **LLM03** Supply Chain | dependência/modelo comprometido | fixar model id Bedrock + versões LangChain4j/Micronaut |
| **LLM04** Data & Model Poisoning | doc envenenado ingerido no vector store | curadoria de ingestão; validação (overlap LLM08) |
| **LLM05** Improper Output Handling | saída do modelo vira XSS/SSRF/RCE no backend | **saída tipada (L10)**; zero-trust na saída; *parameterized queries* |
| **LLM06** Excessive Agency | transferência sem confirmação/idempotência | **least-privilege tools (L7)** + *complete mediation* + HITL (L14) |
| **LLM07** System Prompt Leakage *(novo)* | segredo/regra de authz no system prompt vaza | **nunca** ponha segredo/authz no prompt — enforce server-side (L1) |
| **LLM08** Vector & Embedding Weaknesses *(novo)* | vazamento cross-tenant num vector store compartilhado | **partição por metadado (L9)** — *verbatim* no OWASP |
| **LLM09** Misinformation | saldo/conselho alucinado | **RAG grounding (L9) + guardrail de saída (L11)** |
| **LLM10** Unbounded Consumption | *denial-of-wallet* (custo de inferência) | rate-limit por cliente (L18) |

A relação **mecanismo → entrada é muitos-para-muitos**: um mecanismo cobre várias entradas
(authz server-side → LLM06 **e** LLM02), e uma entrada precisa de vários mecanismos. É
**defesa em profundidade**, não 1:1.

## 4 · A linha-mestra: o controle vive no código, nunca no prompt

`★ Insight ─────────────────────────────────────`
**O OWASP diz, com todas as letras, o que esta trilha repete desde a Lição 1.** LLM06
*Complete mediation* (verbatim): *"Implement authorization in downstream systems rather than
relying on an LLM to decide if an action is allowed or not."* LLM06 *Require user approval*
(verbatim): *"human-in-the-loop ... to approve high-impact actions."* LLM07: o system prompt
**não** guarda segredo. Conclusão: **autenticação, autorização, confirmação e idempotência são
determinísticas e suas**; guardrails e saída tipada **reduzem risco residual**, não substituem
o controle. Um system prompt instruindo "só aja na conta do próprio cliente" **não é um
controle** — o modelo pode ser persuadido a desobedecer.
`─────────────────────────────────────────────────`

## 5 · As duas prioridades do banco (código)

LLM06 (Excessive Agency) e LLM08/LLM02 (vazamento cross-tenant) são as mais críticas.
Os controles são **Java puro determinístico** (não há anotação que substitua):

```java
// LLM05/LLM01: saída tipada limita o que o modelo pode emitir (não texto livre de transferência)
record TransferRequest(String fromAccountId, String toAccountId, long amountCents, String idempotencyKey) {}

class TransferService {                          // LLM06 "complete mediation": authz no backend, não no modelo
    Receipt execute(TransferRequest req, AuthenticatedCustomer caller, boolean humanConfirmed) {
        if (!caller.ownsAccount(req.fromAccountId()))      // LLM06 + LLM02: saída do modelo é não-confiável
            throw new ForbiddenException("caller does not own source account");
        if (!humanConfirmed)                               // LLM06 "require user approval" (HITL)
            throw new ConfirmationRequiredException();
        rateLimiter.check(caller.id());                    // LLM10: anti denial-of-wallet
        return ledger.transferIdempotent(req);             // idempotencyKey deduplica retries
    }
}
```

## Quiz

1. **Qual a edição atual do OWASP Top 10 para Aplicações LLM?**
   (a) a de 2026, recém-lançada para apps LLM · (b) ✅ **a de 2025 (v2.0)**; não há edição 2026 de LLM ·
   (c) ainda a de 2023/24
2. **O que é injeção de prompt INDIRETA num banco?**
   (a) o cliente digitando um jailbreak direto no chat · (b) ✅ **instrução escondida em dado
   ingerido** (extrato/memo) · (c) um erro de digitação que confunde o tokenizador
3. **Onde vive o controle que impede o modelo de autorizar uma transferência?**
   (a) no system prompt, instruindo o modelo a checar permissão · (b) ✅ **no backend
   determinístico** (complete mediation) · (c) no Bedrock Guardrails

## Vá mais fundo

- **Fonte primária:** https://genai.owasp.org/llm-top-10/ (edição 2025) e os arquivos
  `2_0_vulns/LLM0X_*.md` no GitHub do projeto.
- **Aberto:** LLM03/04/10 verificados a nível de ID/nome (texto de mitigação verbatim não citado);
  o código é Java puro (sem assinaturas de framework não-verificadas nesta passagem).
- **Próximo (Lição 16):** gestão da janela de contexto em profundidade.
