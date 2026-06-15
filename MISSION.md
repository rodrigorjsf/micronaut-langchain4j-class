# Mission: Construir um assistente bancário agêntico em produção (LangChain4j + Micronaut 5 + Java 25)

## Why
O usuário é engenheiro de software e está construindo, **no trabalho e agora**, o backend agêntico de um assistente de chat bancário em produção: clientes perguntam sobre qualquer produto (boleto, DDA, Pix, Super Extrato, cartão/fatura, compras, financiamento, investimentos, conta **nacional** e **global** — vindas de backends distintos) e o sistema, via _tools_, busca os dados e responde. Precisa acertar arquitetura, segurança e escala **desde o início**, porque erro em sistema que move dinheiro é caro e difícil de reverter.

## Success looks like
- Implementar um **AI Service** do LangChain4j no **Micronaut 5** que orquestra _tools_ de leitura e de ação para os produtos do banco, com **identidade/autorização na camada determinística** (nunca no modelo).
- Gerir **janela de contexto e memória por cliente** de modo que **custo (N²) e latência** fiquem sob controle em escala.
- Defender o sistema contra **prompt injection** (direto e indireto/RAG) com **guardrails** de entrada/saída e sanitização, seguindo o **OWASP Top 10 para LLM**.
- Decidir conscientemente sobre **concorrência** (virtual threads/scoped values finais; structured concurrency ainda _preview_), **observabilidade** (OpenTelemetry/LangFuse) e o **ecossistema** (o que existe em Java vs. Python).
- Saber quando usar **tool vs. RAG vs. fine-tuning** e desenhar _tools_ cuja granularidade/descrições o modelo use de forma confiável.

## Constraints
- Interação em **pt-BR**; código/artefatos em inglês. Estilo **Explanatory**, regra **Foundation First**.
- Produto em **pt-BR** (impacto de custo de tokenização já medido — ver lição 2).
- Stack fixada: **LangChain4j 1.16.x**, **Micronaut 5.0.x**, **Java 25 LTS**.
- **Modelo-alvo: Claude Sonnet 4.5+** (atualmente Sonnet 4.6), **janela de contexto de 200K tokens**, tokenizador da Anthropic. **A integração é feita via AWS Bedrock** (`langchain4j-bedrock`, classe `BedrockChatModel`), **não** pela SDK/API direta da Anthropic — todos os exemplos de _chat model_, _embeddings_ e _prompt caching_ devem partir da documentação e dos recursos da **AWS Bedrock** + `langchain4j-bedrock`. Ver [[learning-records/0004-integracao-via-aws-bedrock]].
- Preferência declarada por lições **detalhadas** (ver `NOTES.md`) — diverge do "lição curta" padrão da skill, por escolha do usuário.

## Out of scope (por ora)
- Treinar/_fine-tunar_ modelos próprios (decidido: fato que muda → RAG/tool, não _fine-tuning_).
- Front-end/UI do chat (foco no backend agêntico).
- Minúcia de _billing_/cotas no nível de fatura de _vendor_. (A **plataforma de invocação é fixada: Claude via AWS Bedrock** — isso é constraint, não está fora de escopo; o que sai de escopo é o detalhe de preços/limites de conta.)
