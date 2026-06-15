---
paths:
  - "lessons/**/*.html"
  - "lessons/index.html"
---

# Lesson authoring (HTML)

Conventions for every `lessons/00NN-*.html` and `lessons/index.html`. See `content-grounding.md` (auto-loaded with this) for language, grounding, Bedrock, and version rules that also apply.

## Template invariant — byte-identical design system

Every lesson keeps its `<style>` and `<script>` blocks BYTE-IDENTICAL to `lessons/0001-modelo-mental.html` (the Tufte design system). The CSS-variable palette is the contract: `--ink --paper --muted --rule --accent (#0b5c63) --accent-soft --gold (#9a6b00) --warn (#8a2e22) --warn-soft`. A change to `<style>` or `<script>` MUST be propagated byte-identically to ALL lessons and re-validated — never edit one in isolation.

## Required scaffold per lesson

- `.mission` anchor tying the lesson to `MISSION.md`
- Recovery quiz: 3 questions × 3 options, `data-correct` ∈ {a,b,c}, with a hidden `.explain` per question
- One recommended PRIMARY SOURCE (the highest-trust resource on the topic)
- `.ask` block (ask-the-teacher reminder), `.insight` blocks
- `.nav` (prev / index / GLOSSARY)
- `.fine` footer link to the source draft `../curso/modulo-NN`

## Visual teaching (pillar)

Teach non-trivial structure with COLORED, ANIMATED diagrams (architecture / flow / sequence / state), not text + code alone — especially the real-world reference architecture of a resilient, secure, scalable agentic backend. Color is mandatory, to enrich and distinguish elements.

**Preferred shape: decision-flow with impact.** When applicable, model the topic as a *flowchart of decisions* (diamonds = choices) whose leaves state the API/option **and its consequence** (an `impacto:` line), not as a flat linear pipeline. This teaches *why* to choose, not just *what* the steps are. (User directive, repeated.)

**Technique — inline SVG, palette via CSS, animated by CSS (no JS):**
- Reuse the palette with **inline style**, NOT presentation attributes: write `style="fill:var(--accent)"` — `fill="var(--accent)"` (attribute form) does NOT resolve `var()` and renders nothing. Use `var(--accent) #0b5c63`, `var(--gold)`, `var(--warn)`, `var(--rule)`, `var(--accent-soft)`, `var(--muted)`, `var(--ink)`; for text on dark fills use `#fff` (optionally `opacity:.85`).
- **Animate with CSS**, never JS (JS would break the byte-identical `<script>`). Add the keyframes in a **second `<style>` block placed in the body** (e.g. just before the `<figure>`). This is safe: `scripts/validate_lessons.py` captures only the FIRST `<style>` (the head design system) for its byte-identity check, so a later scoped block is ignored by the check while still applying. House idioms: flowing connectors (`stroke-dasharray` + animated `stroke-dashoffset`), a pulsing ring on the active/decision node (`@keyframes` opacity), a traveling particle on a single-path flow (`transform-box:view-box` + `transform:translateY`), hover lift on nodes.
- **Always guard motion**: include `@media (prefers-reduced-motion:reduce){...animation:none}` and `@media print{...animation:none}` in the scoped block.
- `<svg>`, `<g>`, `<rect>`, `<path>`, `<polygon>`, `<text>`, `<circle>`, `<defs>`, `<filter>`, `<feDropShadow>`, `<figure>`, `<figcaption>` are NOT parity-checked tags, so they never break validation — but any `<code>`/`<p>`/`<div>`/`<span>` you add must still open/close balanced.
- Avoid JS renderers (Mermaid etc.). draw.io is fine when exported to inline SVG.

## Numbering discipline

Learner-facing text (lessons + `index.html`) uses **"Lição N"** numbering ONLY. "Módulo N" is source-draft numbering and must NEVER leak into lessons or `index.html`. (Review found a non-constant Módulo→Lição drift that is learner-unrecoverable — this rule prevents regeneration; the Módulo→Lição offset is non-constant, so remap each cross-reference individually.)
