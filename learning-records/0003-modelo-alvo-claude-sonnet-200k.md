# Constraint estabelecido: modelo-alvo é Claude Sonnet 4.5+ (200K, tokenizador Anthropic)

Estabelecido pelo usuário como constraint de arquitetura: o fluxo agêntico do banco roda em **Claude Sonnet 4.5+** (atualmente `claude-sonnet-4-6`) na configuração de **janela de 200K tokens** — **confirmado pelo usuário** (o tier de 1M é separado e não é usado). Saída máx. 64K. Não há **tokenizador offline**: contagem via API `count_tokens`; o `tiktoken` da OpenAI subconta o Claude em ~15–20% (mais em pt-BR/código).

**Implicações para o ensino (steer):**
- A lição de tokenização (0003) media com `tiktoken` (OpenAI) como _proxy_: o **padrão** vale, mas os **números exatos** não são do Claude — exige ressalva e, idealmente, contagem via API `count_tokens` da Anthropic.
- O Módulo 7 (gestão de janela de contexto) deve usar **200K** como orçamento concreto e introduzir **prompt caching** do Claude como alavanca direta contra o custo N² do Módulo 2.
- Verificar specs do Claude via a referência `claude-api` antes de afirmar (não de memória).

Ver [[NOTES.md]], [[MISSION.md]].
