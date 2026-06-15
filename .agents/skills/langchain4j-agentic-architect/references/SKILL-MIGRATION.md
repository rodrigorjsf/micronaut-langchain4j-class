# Skill Migration — the scorecard + the playbook

The differentiated instrument of this skill. Part 1 decides **whether** a flow
should become a `langchain4j-skills` skill; Part 2 is **how** to perform the
migration once the user picks one. Perishable API names live in API-REFERENCE.md.

## Part 1 — The migration scorecard

Score each candidate flow on the signals for and the counter-signals against. A flow
migrates when the signals dominate **and** none of the hard vetoes (latency on a hot
path, no clean trigger) apply.

### Signals FOR migrating

1. **Conditional relevance — the strongest signal.** The flow matters in a narrow
   slice of conversations, not every turn. Progressive disclosure exists exactly to
   stop paying for these on every turn. If the flow fires in nearly every
   conversation, this signal is absent.
2. **Procedural weight in the prompt.** A sizeable, self-contained chunk of the
   system prompt is a step-by-step manual for this one scenario. The bigger that
   chunk, the more budget migration reclaims.
3. **Cohesive cluster.** The flow's instructions, a bounded set of tools, and its
   reference knowledge form one self-contained capability — they belong together and
   are used together.
4. **Externalizable knowledge.** The flow leans on reference material (limit tables,
   policy text, worked examples) currently inlined in the prompt that could instead
   load on demand as a skill resource.
5. **Deterministic activation trigger.** There is a clear natural-language condition
   the model can recognize to activate the skill ("when the customer asks about the
   global account"). State it in one sentence or it isn't clean.

### Counter-signals AGAINST migrating (keep static)

1. **Hot path / used every turn.** If the capability is needed in (almost) every
   conversation, the activation round-trip is pure overhead. Keep it static.
2. **Latency-sensitive.** Activation adds a model round-trip before the flow's tools
   appear. On a tight SLA that can dominate; measure before migrating.
3. **Lone tool, no instructions or resources.** A single tool with no procedure and
   no knowledge is just a tool. Don't wrap it in a `SKILL.md`; if its contract needs
   work, that's the tool-architect skill's job.
4. **No clean trigger.** If you can't state the activation condition in one sentence,
   the model won't reliably activate it and the flow will silently fail to fire. Fix
   the trigger first, or don't migrate.
5. **No bloat to fight.** A small backend (a lean prompt, a handful of tools) has
   nothing for progressive disclosure to reclaim. Migration adds moving parts for no
   gain.

### The non-negotiable caveat

Activation-gating is a **context-management** mechanism, **not** an authorization
boundary. Moving a money-moving or state-mutating flow behind activation does **not**
make it more secure: a model that decides to activate the skill then calls its tools
exactly as before. Authorization must stay in code, enforced from server-side
identity, for every flow whether activated or not. **Never migrate a flow "for
security."** (See ARCHITECTURE-RUBRIC.md check 4 and, for the per-tool fix, the
tool-architect skill — OWASP LLM06 / LLM02 at https://genai.owasp.org/llm-top-10/.)

### Verdict

Map each flow to exactly one verdict in the report:

- **Migrate** — signals dominate, no veto. Becomes a skill.
- **Keep static** — counter-signals dominate; leave it in the static surface.
- **Split** — part of the flow (e.g. its conditional manual + reference data)
  migrates while a hot core tool stays static.
- **Defer to tool-architect** — the real problem is a tool *contract*, not flow
  structure; this skill records it and points to the tool-architect skill.

## Part 2 — The migration playbook

Once the user picks a flow to migrate:

1. **Carve the flow.** From the map, list exactly: the prompt block (the procedure),
   the tools it uses, and the reference knowledge it cites.
2. **Create the skill directory.** One directory per skill with a `SKILL.md`:
   - `name` — kebab-case, equal to the directory name.
   - `description` — the catalog entry **and** the activation trigger in one or two
     sentences. This is the only part always visible to the model; it is what makes
     activation fire. Invest here.
   - body — the procedure moved **out of** the system prompt.
   - bundled resources — the externalized reference knowledge, loaded on demand.
3. **Shrink the system prompt.** Delete the migrated procedure from the system
   message; replace the inline catalog with the framework's available-skills listing
   (see API-REFERENCE.md). The prompt should get materially smaller — verify it did.
4. **Scope the tools to the skill** so they appear only after activation, rather than
   in the static surface.
5. **Wire it** via the skills module: load the skills, expose the activation
   meta-tools through the `ToolProvider`, and add the available-skills listing to the
   system message. Exact identifiers and the lockstep version rule are in
   API-REFERENCE.md — ground them against the project's version before emitting code.
6. **Verify the migration:**
   - the activation trigger fires on representative prompts for the scenario, and
     does **not** fire on unrelated ones;
   - the static system prompt and static tool count both shrank;
   - the agentic loop is still bounded (rubric check 1);
   - the identity / authorization seam is unchanged (rubric check 4) — activation
     must not have moved it.

## Sources

- https://agentskills.io — the open `SKILL.md` format (name + description always
  visible; body + resources on demand).
- https://docs.langchain4j.dev and https://github.com/langchain4j — the
  `langchain4j-skills` module and the tool-provider substrate.
- https://genai.owasp.org/llm-top-10/ — the authorization caveat (LLM06 / LLM02).
