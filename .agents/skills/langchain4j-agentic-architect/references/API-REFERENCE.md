# API Reference — langchain4j-skills & the gating substrate (PERISHABLE)

> ⚠️ **Grounded against `langchain4j-skills 1.16.2-beta26` (core `1.16.2`) only.**
> Every identifier below is version-specific and is the *first* thing to rot when
> the project is on another version. **Before you emit any code:** detect the
> project's LangChain4j version (Step 0) and re-verify each name against that
> version's source / javadoc. If the version differs, treat this file as
> hypotheses, not facts. The durable design rules in ARCHITECTURE-RUBRIC.md and
> SKILL-MIGRATION.md do **not** rot — only this file does.

Primary source: the tagged source tree at
https://github.com/langchain4j/langchain4j/tree/1.16.2 (notably `langchain4j-skills/`
and `langchain4j-core/.../service/tool/`), the tutorials at
https://docs.langchain4j.dev, the open format at https://agentskills.io, and the
module metadata / POMs on Maven Central.

## 1. Version: lockstep + BOM

- `langchain4j-skills:X.Y.Z-betaN` depends on core `langchain4j:X.Y.Z`. Derive the
  skills coordinate from your core version; do not pair mismatched versions.
  - core `1.15.1` → `langchain4j-skills:1.15.1-beta25` (a coordinate a user may have
    named).
  - core `1.16.2` → `langchain4j-skills:1.16.2-beta26` (what this file is grounded
    against).
- Prefer letting the `langchain4j-bom` of your core resolve the version.
- ⚠️ There is **no git tag** for the `-beta` artifact — read source at the stable
  core tags (`1.15.1`, `1.16.2`). The `-beta` lives only on the published artifact.
- The whole module is `@Experimental` / beta — the surface can change between
  versions. Re-verify.

## 2. The skill object model

- **`Skill`** is an **interface** — `name()`, `description()`, `content()`,
  `resources()`, plus `Skill.builder()`. ⚠️ There is **no `@Skill` annotation** and
  **no `AiServices.skills(...)`** method. A skill is registered through the
  tool-provider, not through an annotation.
- A file-backed skill is a directory with a `SKILL.md`: YAML front matter (`name` +
  `description`, always visible to the model) + Markdown body (loaded on activation) +
  optional bundled resources (loaded on demand). This is the open agentskills.io
  format, originally created by Anthropic and released as an open standard (see
  https://www.anthropic.com/engineering and https://agentskills.io).
- Loaders: **`FileSystemSkillLoader`** (`loadSkills(Path)` / `loadSkill(Path)`) and
  **`ClassPathSkillLoader`** (the same, from the classpath, including inside JARs).
- ⚠️ This is the **activation** module. Do **not** confuse it with the sibling shell
  module (`ShellSkills`, `langchain4j-experimental-skills-shell`), which executes
  shell commands. `langchain4j-skills` loads content into context — no filesystem
  access at inference, no arbitrary code execution.

## 3. Wiring (over the ToolProvider substrate)

- **`Skills`** (class) is the entry point:
  - `Skills.from(<loaded skills>)` — build from loaded `Skill`s.
  - `.toolProvider()` — the dynamic `ToolProvider` to pass to
    `AiServices...toolProvider(...)`.
  - `.formatAvailableSkills()` — the catalog listing (the always-visible skill names +
    descriptions) to place in the system message.
- The skills `ToolProvider` is **dynamic and activation-controlled**: it always
  exposes the activation meta-tool (and a resource-reading meta-tool when a skill has
  resources), but reveals a skill's scoped tools **only after** the model has
  activated that skill.
- Auto-generated meta-tools: **`activate_skill`** (loads a skill body into context)
  and **`read_skill_resource`** (loads a bundled resource on demand). The activated
  skill is tracked server-side under an `activated_skill` attribute — never sent to
  the model provider as data.

## 4. The one substrate — the three gating strategies

`langchain4j-skills` is **not** a separate mechanism; it is the third **gating
strategy** over the same `ToolProvider` substrate the other two use:

- **static** — `AiServices...tools(...)`: every tool, every turn.
- **retrieval** — a vector tool-search strategy injects the top-K tools for the
  message (its own `@Experimental` surface; **not** verified end-to-end on every
  provider).
- **activation** — skills: tools hidden until the owning skill is activated.

Retrieval and activation **compose** (a large backend can do both). This is the fact
that lets you reason about migration as a change of *gating strategy*, not a rewrite.
The only hard requirement is that the model supports tool calling (a.k.a. function
calling — see https://platform.openai.com/docs/guides/function-calling for the
vendor-neutral concept), which the mainstream providers do.

## 5. The loop bound (rubric check 1)

- The agentic loop's max tool-calling round-trips is configured on the AI Services
  builder. ⚠️ The default is **large** (intended for convenience, not production).
  Cap it to a small value in production so a misbehaving or adversarial loop is
  bounded. Re-verify the exact method name and default for the project's version — it
  is a perishable identifier.

## 6. Provider note — a flagged example, not a directive

This skill is **provider-agnostic**. `langchain4j-skills` is model-agnostic: it wires
through any `ChatModel` / `AiServices` / `ToolProvider`. Provider choice changes the
*surrounding* surface (e.g. how prompt caching or embeddings are configured), which
is exactly why Step 0 re-grounds against the project's actual setup. Detect the
provider, then use that provider's names — do not assume any one of them.
