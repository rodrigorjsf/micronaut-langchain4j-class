---
paths:
  - "curso/**/*.md"
---

# Source drafts (curso/*.md)

`curso/*.md` files are the source drafts a lesson is distilled from — the working text behind each `lessons/00NN-*.html`. See `content-grounding.md` (auto-loaded with this) for the language, grounding, Bedrock, and version rules that also apply here (code blocks and acronyms appear in drafts too).

## Numbering discipline

Drafts use **"Módulo N"** numbering — this is the source-draft namespace ONLY. It must NEVER leak into learner-facing output (`lessons/**`, `index.html`), which uses "Lição N". When normalizing a draft, keep "Módulo N" internal so a regenerated lesson does not carry it forward. (The Módulo→Lição offset is non-constant — do not assume a fixed mapping.)
