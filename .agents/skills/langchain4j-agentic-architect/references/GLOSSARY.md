# Glossary

Use these terms exactly — consistency is the analytical point. This skill works
at **flow / architecture altitude**; for tool-*contract* vocabulary (tool
contract, blast radius, return shape) defer to the `langchain4j-tool-architect`
skill.

- **Agentic flow** — one end-to-end capability the agent performs: the
  instructions, the bounded set of tools, and the reference knowledge needed to
  handle one *kind* of request from start to finish. The unit this skill scores.

- **Agentic loop** — the cycle the AI Service runs: the model proposes tool calls,
  the runtime executes them and feeds results back, repeating until the model
  returns a final answer. Bounded by a max-round-trips cap (a perishable knob — see
  API-REFERENCE.md).

- **System-prompt budget** — the finite token and attention space of the system
  message. Every conditional procedure parked there is spent on *every* turn,
  whether or not the turn needs it. The budget is the resource skills reclaim.

- **Tool surface** — the set of tool contracts the model can see in one turn. It
  has a token cost and a precision cost (more tools → more chance of the wrong
  pick). Shared term with the tool-architect skill.

- **Gating strategy** — how the visible surface is chosen for a turn:
  - **Static** — every tool, every turn (`.tools(...)`).
  - **Retrieval** — vector tool-search injects the top-K tools for the message.
  - **Activation** — skills: tools stay hidden until the model activates the skill
    that owns them.
  All three are implemented over one `ToolProvider` substrate; retrieval and
  activation compose.

- **Skill (langchain4j sense)** — a directory with a `SKILL.md`: YAML front matter
  (`name` + `description`, always visible to the model) plus a Markdown body and
  optional resources (loaded only on activation). Packaged with the
  `dev.langchain4j:langchain4j-skills` module, which implements the open
  agentskills.io `SKILL.md` format. Model-agnostic — it needs only tool calling.
  Not a vendor's managed-skills product, and not the sibling shell module.

- **Progressive disclosure** — the design principle behind skills: keep the
  always-visible surface tiny (a catalog of skill names + descriptions), and load
  a skill's full instructions and resources on demand when it is activated.

- **Activation** — the runtime act of the model calling the activation meta-tool,
  after which that skill's body and scoped tools enter context. Tracked
  server-side; the activation state is never sent to the model provider as data.

- **Activation trigger** — the natural-language condition, written into a skill's
  `description`, that tells the model when to activate it. A vague trigger is the
  main reason a migrated flow silently fails to fire.

- **Activation round-trip** — the extra model turn spent calling the activation
  meta-tool before a flow's tools appear. The latency cost of activation, and the
  core counter-signal against migrating a hot-path flow.

- **Skill candidate** — an agentic flow whose signals (conditional relevance,
  procedural weight, cohesion, externalizable knowledge, clean trigger) mark it as
  worth migrating. Scored, not assumed.

- **Identity seam** — the place where caller identity and authorization enter the
  request: server-side, from session / token / the memory-id injection mechanism,
  never from a model-supplied argument. Migration must not move this seam.
