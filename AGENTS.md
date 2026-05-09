# AGENTS.md

## Notebook Authoring Rules

- Interleave explanatory markdown with code cells so the notebook is readable and presentation-ready.
- Give every cell a unique, descriptive cell name so cells are easy to reference during collaboration and demos.
- Code cells should generally be hidden to keep the notebook presentation-focused.
- **Edit notebooks only through marimo pair programming (`marimo._code_mode`)** using the repo’s marimo-pair scripts (for example `bash .agents/skills/marimo-pair/scripts/execute-code.sh --url http://localhost:<port> <<'EOF' ... EOF`). Do not edit the notebook `.py` file directly for cell changes—use code mode so the live notebook and saved app stay consistent.

## marimo Import Pattern

- Do not use `__import__("marimo").md(...)` in notebook cells.
- Use exactly one dedicated imports cell near the top of the notebook.
- That imports cell should contain all imports needed by the notebook (including `import marimo as mo`).
- Use the `mo` namespace for marimo APIs throughout the notebook (for example, `mo.md(...)` and `mo.ui.*`).
- Keep all other notebook cells free of import statements; non-import cells can contain any other code needed for the analysis.
