# Protein engineering demo: golden path

`hackathon-demo.py` — runbook for a ~20 minute demo. **Main section:** prompts you can paste into an agent chat verbatim. Below that: cell order, UI checklist, and recovery notes.

Distilled from [cursor-chat-f20cbaac.md](cursor-chat-f20cbaac.md).

---

## Pre-demo setup

Start the notebook:

```bash
uvx marimo edit --sandbox --no-token hackathon-demo.py
```

Confirm files exist:

- `data/ired-novartis/cs1c02786_si_002.csv`
- `data/ired-novartis/cs1c02786_si_003.csv`
- `data/ired-novartis/7OG3.pdb`

Code cells are hidden for presentation; run cells top-to-bottom when showing the finished app live.

---

## Copy-paste prompts (in order)

Use the following as standalone messages to an assistant. Each block is meant to be copied as a whole (triple-click inside the fence).

---

### Prompt 1 — Marimo pair programming

```
Read the marimo-pair skill in this repo and connect to the marimo notebook running on port <PORT>. Verify you can execute code via marimo code mode (smoke test like 1+1 and opening marimo._code_mode context).
```

Replace `<PORT>` with your server port (for example `2719`).

**Finished notebook:** no agent step — optional aside that live edits should go through marimo code mode.

---

### Prompt 2 — Data in repo

```
We're doing a protein engineering notebook. Start from the Novartis IRED data under data/ired-novartis on GitHub (same layout as ericmjl/odsc-2026-agentic-data-science tree data/ired-novartis). Make sure this repo has the supplementary CSVs we need: cs1c02786_si_002.csv (conversion) and cs1c02786_si_003.csv (chirality), plus whatever else is required for the demo, under data/ired-novartis/.
```

**Finished notebook:** run `data_loading_markdown`, `load_conversion_table`, `chirality_loading_markdown`, `load_chirality_table`.

---

### Prompt 3 — Load and inspect with Polars

```
In the live marimo session: add named markdown + code cells that load the conversion and chirality supplementary CSVs with Polars into df_conversion and df_chirality, display each table, and explain in markdown which file is which (002 conversion / 003 chirality with r_enantiomeric_excess).
```

**Finished notebook:** cells through `load_chirality_table`.

---

### Prompt 4 — Correlation at mutant intersection

```
I want to see whether conversion and chirality relate. On the intersection of mutants (join on mutation), prepare a dataset with mutation, mean from df_conversion, and r_enantiomeric_excess from df_chirality. Plot a Plotly scatter of mean vs r_enantiomeric_excess for intersecting mutants, and Plotly ECDFs of both value columns. Skip a full pair plot if it doesn’t add much — scatter + ECDFs are enough.
```

**Finished notebook:** `correlation_analysis_markdown` → `prepare_intersection_dataset` → `plotly_intersection_scatter` → `scatter_interpretation_note` → `plotly_value_ecdfs`.

---

### Prompt 5 — Interpret scatter

```
Add a short markdown cell right after the intersection scatter that states clearly that I don’t see a strong correlation between r_enantiomeric_excess and mean in that scatter.
```

**Finished notebook:** ensure `scatter_interpretation_note` has been run.

---

### Prompt 6 — Single-point heatmap

```
Filter df_conversion to single-point mutants only: mutation must not contain ";", and should match canonical WTposMUT single-letter pattern. Parse position and mutated amino-acid letter. Build a Plotly heatmap: x = position, y = mutation letter, color = mean. Join chirality where available. Hover should show the exact mutation string and r_enantiomeric_excess when present.

Below the heatmap, add markdown noting that I see hotspot positions with potentially strong beneficial mutational effects.
```

**Finished notebook:** `single_point_heatmap_markdown` → `plot_single_point_heatmap` → `single_point_heatmap_interpretation_note`.

---

### Prompt 7 — Average effect by position

```
Average mutational effect by integer position: line plot x = position, y = average mutational effect (from the single-point conversion data). Keep named cells and markdown context.
```

**Finished notebook:** `average_effect_by_position_markdown` → `plot_average_effect_by_position`.

---

### Prompt 8 — Positional tables + PDB mapping

```
From single-point data, build per-position average effects for conversion and for chirality (from chirality single-point rows). Then map assay positions to PDB 7OG3 chain A: parse the PDB, find the best residue index offset by matching wild-type letters, report match/mismatch/unmapped counts, and export JSON maps keyed by PDB residue number for conversion and chirality effects (later extended to mean and max per mode if needed).

Add markdown explaining that we validate numbering before coloring structure.
```

**Finished notebook:** `build_position_effect_tables` → `structure_mapping_markdown` → `pdb_sequence_validation_and_effect_maps`.

---

### Prompt 9 — Anywidget + 3Dmol viewer

```
Implement an inline anywidget backed by 3Dmol.js that loads 7OG3 PDB text, colors protein by residue-level effect maps passed as JSON from Python, toggles color mode conversion vs chirality, and supports mutational effect summary mean vs max with distinct maps. Use cartoon plus molecular surface with synchronized coloring; show non-water HETATM as ball-and-stick for ligand/cofactor. Put dropdown/UI controls in cells that marimo will reliably render (don’t hide the controls inside a stack with the widget only). Split marimo cells if needed so dropdown reactivity works.

Add markdown describing the widget and controls for a literate notebook.
```

**Finished notebook:** `widget_engineering_markdown` → `define_protein_structure_viewer_widget` → `structure_viewer_markdown` → `protein_structure_coloring_controls` → `structure_viewer_color_legend` → `protein_structure_viewer_init` → `protein_structure_viewer_show` → `structure_viewer_interpretation_note`.

---

### Prompt 10 — Click tooltip and polish

```
Add click (not hover) tooltips on residues: chain, residue number, WT amino-acid letter, current color mode, mean/max summary, and the numeric value used for coloring. Clicking whitespace should dismiss the tooltip reliably (handle atom-click vs background-click ordering). Wire ribbon and surface to the same color scale.

Restore coloring if widget traits and JSON maps drift after refactors.
```

**Finished notebook:** re-run `define_protein_structure_viewer_widget` through `protein_structure_viewer_show` after changes.

---

### Prompt 11 — Literate narrative

```
Improve the notebook markdown: intro goal, why two tables are separate, correlation section intent, single-point heatmap interpretation, positional averaging, sequence-to-structure validation, viewer controls (mode + mean/max, colormaps), and a short section before the spot-check table explaining we validate numbers against Polars aggregates.
```

**Finished notebook:** run `viewer_validation_markdown` before the spot check.

---

## Cell run order (finished notebook)

1. `notebook_imports`
2. `intro_markdown`
3. `data_loading_markdown`
4. `load_conversion_table`
5. `chirality_loading_markdown`
6. `load_chirality_table`
7. `correlation_analysis_markdown`
8. `prepare_intersection_dataset`
9. `plotly_intersection_scatter`
10. `scatter_interpretation_note`
11. `plotly_value_ecdfs`
12. `single_point_heatmap_markdown`
13. `plot_single_point_heatmap`
14. `single_point_heatmap_interpretation_note`
15. `average_effect_by_position_markdown`
16. `plot_average_effect_by_position`
17. `build_position_effect_tables`
18. `structure_mapping_markdown`
19. `pdb_sequence_validation_and_effect_maps`
20. `widget_engineering_markdown`
21. `define_protein_structure_viewer_widget`
22. `structure_viewer_markdown`
23. `protein_structure_coloring_controls`
24. `structure_viewer_color_legend`
25. `protein_structure_viewer_init`
26. `protein_structure_viewer_show`
27. `structure_viewer_interpretation_note`
28. `viewer_validation_markdown`
29. `structure_viewer_spot_check_verify`

---

## Live UI checklist (audience)

- [ ] Toggle **conversion** ↔ **chirality** and point at the legend.
- [ ] Toggle **mean** ↔ **max** and explain the difference in one sentence.
- [ ] Click two or three residues and read tooltip fields (including WT AA).
- [ ] Click empty background; tooltip should dismiss.
- [ ] Point out ligand/cofactor ball-and-stick vs colored protein.

---

## Recovery

| Symptom | Try |
|--------|-----|
| Stale or blank 3D view | Re-run `define_protein_structure_viewer_widget`, `protein_structure_viewer_init`, `protein_structure_viewer_show`. |
| Controls not updating coloring | Re-run `protein_structure_coloring_controls`, `structure_viewer_color_legend`, `protein_structure_viewer_show`. |
| Gray or wrong colors | Re-run `pdb_sequence_validation_and_effect_maps` then viewer cells so JSON maps and widget traits match. |
| Nuclear | Restart kernel; execute the **Cell run order** list from the top. |

---

## Three-line close (optional)

- Conversion and chirality can decouple — treat them as separate objectives.
- Hotspots in sequence matter when mapped onto structure.
- Interactive mode + mean/max + residue drill-down helps prioritize the next mutations.
