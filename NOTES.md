# NOTES — Preferências e decisões de ensino

## Preferências do aprendiz
- **Idioma:** interação em pt-BR; código/artefatos duráveis em inglês.
- **Estilo:** Explanatory (blocos de insight ★), **Foundation First**.
- **Profundidade:** lições **detalhadas** — pedido explícito e repetido ("Detalhado").
- **Exemplo-âncora:** assistente bancário agêntico (todos os produtos; conta **nacional vs. global** em backends distintos).
- **Processo:** usar **Workflows em background para aterrar APIs específicas de versão em fontes primárias**, mantendo o contexto principal especializado em ensinar (pedido explícito).
- **Rigor:** **verificar versões/APIs em fonte primária antes de ensinar** — nada de conhecimento paramétrico não-verificado. Mostrar a verificação faz parte da aula.
- **Modelo-alvo:** o fluxo agêntico do banco usa **Claude Sonnet 4.5+** (atualmente Sonnet 4.6) e **o tokenizador da Anthropic** — não OpenAI. **Janela de contexto padrão: 200K tokens.** Toda medição/decisão de tokens, janela de contexto, _prompt caching_ e _tool use_ assume esse modelo. Consultar a skill/refer. `claude-api` antes de afirmar specs do **modelo** Claude (janela, comportamento).
- **⚠️ Caminho de invocação = AWS Bedrock (não a SDK direta da Anthropic).** O banco invoca o Claude **via AWS Bedrock**, usando `langchain4j-bedrock` (`BedrockChatModel`). Logo, exemplos/APIs de _chat model_, _embeddings_ (**Titan/Cohere via Bedrock**, não Voyage/ONNX) e _prompt caching_ (**cachePoint do Bedrock**, não `cacheSystemMessages`) devem vir da doc da **AWS Bedrock** + `langchain4j-bedrock`. A spec do modelo Claude em si continua válida; muda **como** se invoca. Ver [[learning-records/0004-integracao-via-aws-bedrock]].

## Desvios deliberados da SKILL.md (documentados)
- **Tamanho da lição:** a skill recomenda lições curtas (um ganho, dentro da memória de trabalho). O usuário pediu lições **detalhadas**. Resolução: manter o conteúdo detalhado aprovado, mas impor em **cada** lição o _scaffold_ exigido pela skill — fonte primária recomendada, _cross-links_, **quiz de recuperação**, vínculo com a missão, lembrete "pergunte ao professor". Reavaliar se o usuário sinalizar sobrecarga.
- **`curso/*.md`:** mantidos como **rascunhos-fonte**; as lições canônicas da skill são `lessons/*.html`.

## Fatos do Claude Sonnet 4.6 (verificados via `claude-api`, 2026-06-14)
- **Modelo:** `claude-sonnet-4-6` (Sonnet 4.5 = `claude-sonnet-4-5`, legado mas ativo). Sonnet é a escolha recomendada para produção de **alto volume** (mais barato que Opus: ~US$3 / US$15 por milhão de tokens in/out).
- **✅ Janela confirmada pelo usuário: 200K tokens.** O banco usa o Sonnet na configuração de **200K de contexto** (a janela padrão do Sonnet; o tier de 1M é separado/beta e **não** é usado aqui). Saída máx. 64K. Todo orçamento de contexto do Módulo 7 parte de **200K**.
- **Tokenizador:** **NÃO existe tokenizador offline** para Claude. Conte via API `count_tokens` (`POST /v1/messages/count_tokens`), específica por modelo. **`tiktoken` (OpenAI) SUBCONTA tokens do Claude em ~15–20%** em texto típico — e **mais ainda em código e idiomas não-ingleses** (logo pt-BR infla ainda mais no Claude do que a medição-proxy da lição 0003 mostrou).
- **Prompt caching (a alavanca contra o N²):** leitura ~**0,1×** do preço de entrada (≈90% de economia); escrita **1,25×** (TTL 5min) ou **2×** (TTL 1h). Mínimo cacheável no Sonnet 4.6 = **2048 tokens**. _Break-even_: 2 requisições (5min) / 3 (1h). É **prefix match** — qualquer byte alterado no prefixo invalida o resto; ordem de render `tools → system → messages`.
- **Tool use / structured output:** tool calling nativo (JSON Schema; `tool_choice` auto/any/tool/none; chamadas paralelas por padrão), `strict: true` e `output_config.format` para saída estruturada — abstraídos pelo módulo `langchain4j-anthropic`.

## Dívida de correção — RESOLVIDA (2026-06-14)
- **Lição 8 (`0008-chatmemory-contexto.html`) + `curso/modulo-07`:** o exemplo usava `AnthropicChatModel.builder().cacheSystemMessages(true)` e o `AnthropicTokenCountEstimator` — provider-errado para o banco Bedrock. **Retrofit feito:** agora usa `BedrockChatModel` + `BedrockChatRequestParameters.promptCaching(BedrockCachePointPlacement.AFTER_SYSTEM, CacheTTL.VALUE_5_M)`; contagem via `BedrockTokenUsage`/`CountTokens` (estimador **local** na janela ao vivo). `cacheSystemMessages` permanece citado **apenas como armadilha** (método real do `langchain4j-anthropic`, no-op no Bedrock). Suite 0001–0009 revalidada: toda verde.

## Estado da trilha (2026-06-14)
- **Trilha base COMPLETA: 19 lições** (`lessons/0001`–`0019`) + rascunhos-fonte (`curso/modulo-01`–`17`, com `09b`). Suite revalidada: **toda verde** (style/script byte-idênticos ao 0001, quiz 3×3, balanceada). Índice reestruturado em Partes 0–4, sem placeholder "futuro".
- **Correções de versão descobertas no aterramento (durável):** `micronaut-langchain4j 2.0.1` → **LangChain4j 1.15.1** (não 1.16.2), Micronaut 5.0.1; `langchain4j-agentic` existe **só** como `1.16.2-beta26` (assimetria com `langchain4j-bedrock` 1.16.2); OWASP LLM Top 10 edição **2025 (v2.0)**; LangFuse **sem SDK Java** (OTel); `langsmith-java` beta.
- **Revisão final (pedido do usuário):** Workflow `review-trilha-19-licoes` (task `w10fu6c4s`) **lançado** — audita as 19 lições em 3 eixos (aderência ao prompt inicial / embasamento na fonte / profundidade) + pedagogia + consistência Bedrock, com spot-check adversarial. **Aguardando resultado** para triagem de correções. **Só depois** aplicar fixes.

## Histórico de processo
- Sessão agendada (disparo 2026-06-13 19:41 -0300) começou o ensino direto em `curso/*.md` **antes** de invocar a skill `/teach`; corrigido para conformidade com a skill a pedido do usuário (este _retrofit_).
