# Report Format — portable Markdown

The findings report is a **single Markdown file**. Markdown is the portable
choice: it renders in any harness, terminal, PR, or editor, and its Mermaid
fences render in GitHub, GitLab, VS Code, and Obsidian — so you keep before/after
diagrams **without assuming a browser**. Do not emit HTML and do not try to open
anything.

Save it to a path that won't pollute the repo — prefer the OS temp dir
(`$TMPDIR` or `/tmp`, `%TEMP%` on Windows) as `tool-architecture-review-<n>.md`,
or a project `docs/` / `reports/` dir if the user wants it tracked. Tell the user
the absolute path.

## Structure

```
# Tool architecture review — <project / tool name>

<one-line scope: what was analyzed, which mode, LangChain4j version + provider detected>

## Summary
- N findings: X critical, Y high, Z medium, W low
- Surface: <tool count> tools, <gating strategy>, <read>/<write> split
- Headline risk: <the one sentence that matters most>

## Findings
<one card per finding, ordered by severity>

## Top recommendation
<the single change to make first, and why — anchor/link to its card>
```

## Severity scale

Use plain, renderer-safe labels (optionally with an emoji):

- 🔴 **CRITICAL** — exploitable security flaw or money/state at risk now.
- 🟠 **HIGH** — wrong-tool selection, identity on a contract, leaking errors.
- 🟡 **MEDIUM** — token cost, weak descriptions, granularity smell.
- 🟢 **LOW** — naming, polish, nice-to-have.

## Finding card template

Each finding is one section. Keep prose sparse; the diagram and the grounded fix
carry the weight.

```
### <short title — names the change, e.g. "Move customerId off the contract">

**Severity:** 🟠 HIGH · **Test failed:** Identity test · **OWASP:** LLM06 / LLM02
**Where:** `CardTools.getInvoice(...)` — `src/main/java/.../CardTools.java`

**Problem.** One sentence. What is wrong and why it bites.

**Recommendation.** One or two sentences, then a grounded code snippet. Every
API identifier in the snippet must be verified against the project's LangChain4j
version (see API-REFERENCE.md). If unverified, say so explicitly.

**Before / after.**

​```mermaid
flowchart LR
  subgraph Before
    M1[Model] -->|"customerId = ?"| T1["getInvoice(customerId, month)"]
    T1 --> B1[(Backend)]
    M1 -.injection sets id.-> T1
  end
  subgraph After
    M2[Model] -->|"month only"| T2["getInvoice(month)"]
    T2 --> S2{{"server: id from session\nauthorize in code"}}
    S2 --> B2[(Backend)]
  end
  classDef vuln stroke:#dc2626,stroke-width:2px;
  class T1 vuln
​```

**Source:** <primary-source URL the rule is grounded in>
```

## Diagram guidance

- Use Mermaid `flowchart` for "model → tool → backend" and where identity enters.
  Use `sequenceDiagram` for "before: N round-trips; after: 1" (granularity /
  surface-budget findings).
- Keep diagrams small — a `Before` and `After` subgraph side by side is enough.
- Mark the vulnerable/shallow node red via `classDef` so the failure reads at a
  glance.
- If a diagram needs a paragraph to be understood, simplify the diagram.
- Plain ASCII tables/boxes are an acceptable fallback if a target renderer lacks
  Mermaid — never block on rendering.

## Tone

Name the failing **test** and the **glossary** terms (tool contract, surface,
intention vs identity, read/write) in every card — that vocabulary is the report's
spine. State the problem in one sentence; if a sentence can be a bullet, make it
a bullet. Recommendations are concrete and grounded, never "consider improving."

## Mode notes

- **Audit mode:** present all cards, then **stop and ask which to pursue** — do
  not finalize new tool contracts in the report itself.
- **Single-tool / create mode:** the report can be one card plus the proposed
  contract, then go straight to the grill-and-implement loop.
