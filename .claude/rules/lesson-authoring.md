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

Teach non-trivial structure with COLORED diagrams (architecture / flow / sequence / state), not text + code alone — especially the real-world reference architecture of a resilient, secure, scalable agentic backend. Default technique: inline SVG embedded in the lesson HTML, reusing the palette via CSS custom properties (`fill="var(--accent)"`, `var(--gold)`, `var(--warn)`, `var(--rule)`) so figures inherit the design system. Color is mandatory, to enrich and distinguish elements. Avoid JS-dependent renderers (e.g. Mermaid) — they would break the byte-identical `<script>`; draw.io is fine when exported to inline SVG.

## Numbering discipline

Learner-facing text (lessons + `index.html`) uses **"Lição N"** numbering ONLY. "Módulo N" is source-draft numbering and must NEVER leak into lessons or `index.html`. (Review found a non-constant Módulo→Lição drift that is learner-unrecoverable — this rule prevents regeneration; the Módulo→Lição offset is non-constant, so remap each cross-reference individually.)
