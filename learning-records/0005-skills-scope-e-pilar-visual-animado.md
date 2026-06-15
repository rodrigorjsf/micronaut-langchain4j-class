# "Skills" = o módulo `langchain4j-skills`; e o pilar visual vira diagrama de decisão animado

Status: active

Dois esclarecimentos do usuário em 2026-06-15 que mudam como ensinamos daqui em diante.

## 1 · Escopo de "skills" — a dependência Java, não a feature da Anthropic

Quando o usuário diz **skills**, refere-se à dependência Java real
`dev.langchain4j:langchain4j-skills` (a versão citada, `1.15.1-beta25`, casa com o core 1.15.1),
**não** à feature gerenciada de Agent Skills da Anthropic.

- A Lição 20 (`0020-agent-skills.html`) e o rascunho `curso/modulo-18-skills.md` foram **reescritos**:
  o módulo implementa o padrão **aberto** `SKILL.md` (agentskills.io) **sobre o `ToolProvider`**;
  progressive disclosure via `activate_skill`/`read_skill_resource`; `Skill` é **interface** (sem
  `@Skill`); modelo-agnóstico → roda no Bedrock; versão em **lockstep** com o core (+BOM); **não** é
  o módulo `…-skills-shell` (`ShellSkills`, que executa shell). Aterrado na tríplice verificação
  contra a tag 1.16.2.
- **Convergência:** skills, `ToolSearchStrategy` (busca vetorial) e `.tools(...)` estático são as
  **três estratégias de *tool gating*** sobre o **mesmo `ToolProvider`** — a espinha que liga as
  Lições 7 e 20. Ver [[GLOSSARY.md]] (seção Agent Skills) e [[NOTES.md]].

## 2 · Pilar visual — diagrama de decisão **animado**, com impacto

O usuário reforçou (mensagens de 2026-06-15) que os diagramas devem ser **HTML/SVG modernos,
coloridos e animados**, e — quando aplicável — ter **estrutura de fluxo com processos decisórios e
o impacto de cada escolha** (losangos = decisões; folhas = opção/API **e a consequência**), não
pipelines lineares.

- **Técnica validada** (de-riscada contra `scripts/validate_lessons.py`): SVG inline; paleta via
  **`style="fill:var(--accent)"`** (CSS inline) — **nunca** o atributo `fill="var(--accent)"`, que
  não resolve `var()`. Animação por **CSS num segundo `<style>` no corpo** (o validador só checa o
  primeiro `<style>`, do head; um bloco escopado depois é seguro e mantém a identidade byte-idêntica).
  Sempre com `@media (prefers-reduced-motion)` + `@media print`. Detalhe em
  [[.claude/rules/lesson-authoring.md]] ("Visual teaching").
- Aplicado primeiro na Lição 7 (decisão de *gating* de tools) e replicado nas Lições 20 (progressive
  disclosure) e 22 (capstone macro + micro). Prévias de aprovação em `docs/previews/`.
- A correção do landmine `fill="var()"` foi propagada para `NOTES.md` e `lesson-authoring.md` para
  não reincidir.
