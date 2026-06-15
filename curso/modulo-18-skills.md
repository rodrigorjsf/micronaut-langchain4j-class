# Módulo 18 — Agent Skills no Java: o módulo `langchain4j-skills` (sobre o `ToolProvider`)

> **Rascunho-fonte da Lição 20** (`lessons/0020-agent-skills.html`). Aterrado em fonte primária:
> o módulo `dev.langchain4j:langchain4j-skills` na tag **1.16.2** (raw GitHub), a metadata e os
> POMs no Maven Central, e a especificação aberta em `agentskills.io`. **Correção de escopo
> (2026-06-15):** isto NÃO é a feature gerenciada da Anthropic — é a **dependência Java real**
> `langchain4j-skills` (a versão que o usuário citou, `1.15.1-beta25`, casa com o core 1.15.1).

## 1 · O problema: o *system prompt* não escala

A Lição 7 mostrou o *tool retrieval* para não despejar dezenas de **tools** na mesa. O mesmo vale
para **instruções**: o manual de "Pix na conta global", "simular financiamento", "ler o Super
Extrato" — se tudo vive no *system prompt*, ele incha, encarece cada chamada (o N² da Lição 8) e
afoga o sinal em ruído. A resposta é **progressive disclosure**: mostrar pouco, carregar o resto
sob demanda.

## 2 · O formato `SKILL.md`

Uma **skill** é um diretório com um `SKILL.md`: *front matter* YAML (`name` + `description`,
sempre visíveis ao modelo) + corpo Markdown de instruções (carregado na ativação) + recursos
opcionais (`references/`, `scripts/`). Segundo `agentskills.io` (a spec que o langchain4j
referencia), o formato foi **originalmente criado pela Anthropic e liberado como padrão aberto**.

```
# skills/pix-global/SKILL.md
---
name: pix-global
description: Limites e envio de Pix na conta GLOBAL (regras e backend distintos da nacional).
---

# Pix na conta global
Use quando o cliente perguntar sobre Pix na conta global.
1. Confirme o tipo de conta antes de qualquer ação de envio.
2. Cheque o limite com a tool de leitura; só então proponha o envio.
```

## 3 · O módulo real (API verificada @ 1.16.2)

`@Experimental`/beta. API pública essencial:

| Símbolo | Papel |
| --- | --- |
| `Skills` (classe) | `Skills.from(...)`, `.toolProvider()` (o `ToolProvider` dinâmico), `.formatAvailableSkills()` (catálogo XML p/ o *system message*) |
| `Skill` (**interface**) | `name()`, `description()`, `content()`, `resources()`; `Skill.builder()`. **Sem anotação `@Skill`** |
| `FileSystemSkillLoader` | `loadSkills(Path)` / `loadSkill(Path)` |
| `ClassPathSkillLoader` | o mesmo, do *classpath* (inclusive dentro de JARs) |
| `SkillResource`, `ActivateSkillToolConfig`, `ReadResourceToolConfig` | recurso sob demanda; config dos tools `activate_skill` / `read_skill_resource` |

**Pegadinhas:** não existe `@Skill` nem `AiServices.skills(...)`. Não confundir com o módulo irmão
`langchain4j-experimental-skills-shell` (`ShellSkills`), que **executa shell** — o `langchain4j-skills`
carrega tudo em memória, **sem acesso ao filesystem na inferência** e sem execução de código arbitrário.

## 4 · Como liga ao `AiService` (sobre o `ToolProvider`)

```java
Skills skills = Skills.from(FileSystemSkillLoader.loadSkills(Path.of("skills")));

AssistenteBanco assistente = AiServices.builder(AssistenteBanco.class)
    .chatModel(model)                                   // BedrockChatModel (modelo-agnóstico)
    .systemMessage("Você é o assistente do banco.\n"
        + "Skills disponíveis:\n" + skills.formatAvailableSkills())
    .toolProvider(skills.toolProvider())               // expõe activate_skill / read_skill_resource
    .build();
```

O `ToolProvider` das skills é **dinâmico** e **controlado por ativação**: sempre expõe
`activate_skill` (e `read_skill_resource` quando há recursos), mas só revela as tools escopadas de
uma skill **depois** que o modelo chamou `activate_skill` — rastreado em memória pelo atributo
`activated_skill`, nunca enviado ao provedor. É a **terceira** estratégia de "o que o modelo vê",
sobre o mesmo `ToolProvider` da Lição 7 (estático / busca vetorial / **ativação**); as duas últimas
**compõem**.

## 5 · A versão certa: *lockstep* + BOM

`langchain4j-skills:X.Y.Z-betaN` depende de `langchain4j:X.Y.Z`. Derive a coordenada do seu core:

| Seu core | Coordenada de skills |
| --- | --- |
| `1.15.1` (embarcado pelo `micronaut-langchain4j 2.0.1`, Lição 12) | `langchain4j-skills:1.15.1-beta25` |
| `1.16.2` (a pilha agêntica, Lição 14) | `langchain4j-skills:1.16.2-beta26` |

Melhor: deixe o `langchain4j-bom` do seu core resolver a versão. A fonte está nas tags estáveis
`1.15.1`/`1.16.2` — **não existe tag git `1.15.1-beta25`** (o *beta* é só do artefato).

## 6 · Bedrock (honesto)

Modelo-agnóstico: liga via `ChatModel`/`AiServices`/`ToolProvider`, e `BedrockChatModel` implementa
`ChatModel`. O único requisito é *tool calling*, que o Claude no Bedrock tem. O fluxo básico
(`activate_skill` + `read_skill_resource`) é o confirmado; a integração opcional com *tool search*
sobre o Bedrock **não** foi verificada ponta a ponta — não tratar como garantida.

## Fonte primária

O *javadoc* da classe `Skills.java` na tag **1.16.2** e o tutorial `docs/tutorials/skills.md` no
repositório do langchain4j; a metadata/POMs no Maven Central (lockstep de versão); e a spec aberta
em `agentskills.io`.
