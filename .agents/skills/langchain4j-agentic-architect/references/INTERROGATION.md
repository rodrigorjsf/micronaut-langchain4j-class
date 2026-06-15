# Interrogation

A relentless-but-targeted interview that pins the user's *real* goal before any
analysis or code. Modeled on grill-me, scoped to agentic-flow architecture and
skill migration.

## Rules

1. **One question at a time.** Never dump a checklist. Ask, get the answer, let it
   steer the next question.
2. **Always recommend an answer.** Give your recommended answer and a one-line
   reason, so the user can simply confirm.
3. **Explore before you ask.** If the codebase can answer it, read the code
   instead. Only ask what code cannot settle (intent, constraints, priorities,
   SLAs, risk tolerance).
4. **Walk the tree, resolve dependencies.** Don't ask about gating before you know
   the tool count and which flows are conditional.
5. **Stop when no remaining branch changes the recommendation.** Leave no loose
   ends; don't over-interrogate once the path is set.

## Phase 0 — Pin the mode (one question, always first)

> "What do you want out of this? (a) audit an agentic backend for skill-migration
> opportunities; (b) migrate one specific flow into a skill; (c) design a new
> agentic flow and choose its gating (static vs skill); (d) update or refactor an
> existing skill."

Infer a recommended mode from what the user already said. The mode decides the
ordering of Steps 1–2 in SKILL.md:

- **(a) audit / (b) migrate / (d) update** → run the **light scan first**, then
  ask only what code can't answer.
- **(c) greenfield design** → interrogation leads; little code to scan yet.

## Light scan (run first in modes a/b/d)

Best-effort ripgrep patterns to answer questions before asking them. Adjust to the
project's layout; treat hits as leads, not proof.

```bash
# Is langchain4j-skills already on the classpath / in use?
rg -n "langchain4j-skills|Skills\.from|FileSystemSkillLoader|ClassPathSkillLoader|formatAvailableSkills"

# How big is the system prompt, and is it full of conditional procedure?
rg -n "@SystemMessage|systemMessage\(" --type java -A3

# How many tools, and how are they gated today (static / retrieval / activation)?
rg -c "@Tool" --type java
rg -n "\.tools\(|\.toolProvider\(|toolSearchStrategy|VectorToolSearchStrategy" --type java

# Flow clusters: tools that name one scenario (candidates to share one skill)
rg -n "@Tool" -A2 --type java

# Loop bound and identity seam
rg -n "maxToolCallingRoundTrips" --type java
rg -n "@ToolMemoryId|@MemoryId" --type java
```

## Decision tree (ask only the branches the scan left open)

### A. The real pain

- What's actually wrong: **system prompt too big / expensive**, **wrong tool
  picked among many**, **a new capability to add**, or **a flow you already
  believe should be a skill**? *(Rec: name the dominant symptom; prompt bloat and
  too-many-tools are the two that skills address — other symptoms may belong to the
  tool-architect skill instead.)*

### B. Flow conditionality (the core migration signal)

- For the flow(s) in question: do they matter in **every conversation**, or in a
  **narrow slice**? *(Rec: narrow slice → strong migrate signal; every
  conversation → keep static, the activation round-trip is pure overhead.)*
- Does the flow carry **reference knowledge** (limit tables, policy text, examples)
  currently inlined in the prompt? *(Rec: if yes, that knowledge is a load-on-demand
  resource — a further migrate signal.)*

### C. Activation feasibility

- Is there a **clean natural-language trigger** for the flow the model could
  recognize? *(Rec: if you can't state it in one sentence, the model won't reliably
  activate — fix the trigger before migrating, or don't migrate.)*

### D. Latency & criticality

- Is this flow on a **latency-sensitive path**, and does it **move money or mutate
  state**? *(Rec: tight SLA → weigh the extra round-trip; money/state → remember
  activation is not authorization, keep the code-side checks.)*

### E. Identity seam

- Where does **caller identity** come from — session / token / the memory-id
  injection mechanism, or a tool parameter? *(Rec: server-side; a model-supplied
  identity is a red flag and migration must not entrench it. Defer the deep
  tool-contract fix to the tool-architect skill.)*

### F. Constraints (mostly from build files)

- LangChain4j **version**? Is **`langchain4j-skills`** already a dependency?
  **AiServices** or low-level API? Model **provider**? *(Rec: read `pom.xml` /
  `build.gradle`; the version fixes the skills coordinate via lockstep — confirm
  only what's ambiguous.)*

### G. Target

- Do you want **a report only**, or should I **implement** the migration(s)? *(Rec:
  report first, then implement the picks one flow at a time.)*

## Exit

When the remaining branches no longer change your recommendation, summarize the
resolved decisions in two or three lines and confirm before moving on. That
summary is the brief the rest of the skill works from.
