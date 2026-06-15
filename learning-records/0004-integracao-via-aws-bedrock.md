# Integração com o Claude é via AWS Bedrock, não pela SDK direta da Anthropic

Status: active

O usuário estabeleceu (2026-06-14) que o assistente bancário invoca o Claude **através da AWS Bedrock**, usando o módulo `langchain4j-bedrock` (`BedrockChatModel`), e **não** pela SDK/API direta da Anthropic. Toda referência a API, exemplo ou recurso de _chat model_, _embeddings_ e _prompt caching_ deve partir da documentação e dos exemplos da **integração com a AWS Bedrock**.

## Implications

- **Chat model:** usar `BedrockChatModel` (módulo `langchain4j-bedrock`), não `AnthropicChatModel`. O `AiServices` cabla igual — só muda o bean do modelo e a config (região, credenciais AWS, model ID / inference profile).
- **Embeddings (RAG):** o caminho natural é **Bedrock** — Amazon **Titan** ou **Cohere** embeddings via Bedrock — em vez de Voyage/ONNX. Para conteúdo **pt-BR**, preferir um modelo **multilíngue** (a confirmar no aterramento).
- **Prompt caching:** é o **cachePoint do Bedrock** (Converse API), não o `cacheSystemMessages` da `AnthropicChatModel`. Confirmar se `langchain4j-bedrock` 1.16.2 já expõe isso — se **não** expuser, esse é em si o fato a ensinar.
- **Token counting:** a contagem vem do _usage_ retornado pela Bedrock; não assumir o endpoint `count_tokens` da Anthropic direta.
- **Dívida de correção:** a Lição 8 (prompt caching) foi escrita com a API direta da Anthropic — precisa de retrofit para Bedrock. Ver [[NOTES.md]] (seção "Dívida de correção").
- A spec do **modelo** Claude em si (janela de 200K, comportamento, tokenização) continua válida — ver [[learning-records/0003-modelo-alvo-claude-sonnet-200k]]. O que muda é **como** se invoca o modelo.
