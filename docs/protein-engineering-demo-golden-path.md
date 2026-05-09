# Protein Engineering Demo: Golden Path Script

This is the canonical walkthrough for a ~20 minute demo using `hackathon-demo.py`.

## Demo Goal

Show an end-to-end agentic protein engineering workflow:
- load conversion and chirality datasets,
- identify mutational signal patterns,
- map those effects onto structure `7OG3`,
- interactively explore mode (`conversion`/`chirality`) and summary (`mean`/`max`),
- inspect residue-level values with click tooltips.

## Pre-Demo Setup (2 minutes)

- Start marimo notebook:
  - `uvx marimo edit --sandbox --no-token hackathon-demo.py`
- Open the notebook URL and confirm all cells are runnable.
- Confirm files exist:
  - `data/ired-novartis/cs1c02786_si_002.csv`
  - `data/ired-novartis/cs1c02786_si_003.csv`
  - `data/ired-novartis/7OG3.pdb`
- Keep code hidden (already configured) for presentation mode.

## Golden Path: Cell-by-Cell Run Order

Run cells in this order and narrate with the talk track below:

1. `intro_markdown`
2. `data_loading_markdown`
3. `load_conversion_table`
4. `chirality_loading_markdown`
5. `load_chirality_table`
6. `correlation_analysis_markdown`
7. `prepare_intersection_dataset`
8. `plotly_intersection_scatter`
9. `scatter_interpretation_note`
10. `plotly_value_ecdfs`
11. `single_point_heatmap_markdown`
12. `plot_single_point_heatmap`
13. `single_point_heatmap_interpretation_note`
14. `average_effect_by_position_markdown`
15. `plot_average_effect_by_position`
16. `build_position_effect_tables`
17. `pdb_sequence_validation_and_effect_maps`
18. `structure_viewer_markdown`
19. `protein_structure_coloring_controls`
20. `structure_viewer_color_legend`
21. `protein_structure_viewer_init`
22. `protein_structure_viewer_show`
23. `structure_viewer_interpretation_note`
24. `structure_viewer_spot_check_verify`

## Talk Track (Narration Script)

### 0:00-2:00 — Framing
- "We are going from mutational assay tables to structure-aware interpretation in one notebook."
- "This uses conversion and chiral selectivity as two optimization objectives."

### 2:00-5:00 — Data Ingestion
- Run `load_conversion_table` and `load_chirality_table`.
- "We load two complementary assay tables: conversion and enantiomeric excess."
- "The downstream flow keeps these separate so we can compare objectives cleanly."

### 5:00-8:00 — Correlation Check
- Run scatter + interpretation + ECDF cells.
- "At mutant intersection, conversion and chirality are not strongly correlated."
- "That means optimizing one objective may not automatically optimize the other."

### 8:00-12:00 — Sequence-Level Mutational Landscapes
- Run single-point heatmap + interpretation + positional average plot.
- "This highlights positional hotspots and identifies where mutation matters most."
- "Hotspots indicate exploitable sequence regions for directed engineering."

### 12:00-15:00 — Structure Mapping
- Run mapping/validation cell.
- "We map assay positions to PDB residues and validate wild-type consistency."
- "Then we project per-position summaries into structure-space."

### 15:00-19:00 — Interactive Structure Analysis
- Run controls/legend/init/show.
- Demo interactions live:
  - Toggle `Color mode`: `conversion` -> `chirality`
  - Toggle `Mutational effect summary`: `mean` -> `max`
  - Click a residue to show tooltip (chain, residue, WT AA, mode, summary, value)
  - Click whitespace to dismiss tooltip
- "Now we can compare objective-specific structural patterns interactively."
- "The same scaffold supports both average and best-case mutational perspectives."

### 19:00-20:00 — Close
- Run `structure_viewer_spot_check_verify`.
- "Spot checks confirm map values match the underlying aggregated tables."
- "This gives confidence that structural colors are faithful to assay data."

## Audience-Facing Key Messages

- Conversion and chirality can decouple; multi-objective thinking is required.
- Sequence-space hotspots become actionable when mapped into structure context.
- Interactive visualization helps prioritize mutation campaigns by site and objective.

## Live Demo Interaction Checklist

- Change color mode and mention legend updates.
- Change mean/max and explain why max can surface opportunistic pockets.
- Click at least 2-3 residues and read the tooltip aloud.
- Click background once to show tooltip dismissal behavior.
- Briefly point out ligand/cofactor displayed as ball-and-stick.

## Backup / Recovery Notes

- If widget appears stale, re-run:
  - `define_protein_structure_viewer_widget`
  - `protein_structure_viewer_init`
  - `protein_structure_viewer_show`
- If controls do not propagate, re-run:
  - `protein_structure_coloring_controls`
  - `structure_viewer_color_legend`
  - `protein_structure_viewer_show`
- If needed, restart notebook kernel and re-run cells in the listed order.
