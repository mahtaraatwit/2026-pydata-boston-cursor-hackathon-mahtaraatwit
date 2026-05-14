"""Push IRED master + structure cells into a running marimo notebook via code_mode."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SNIP = REPO / "snippets" / "marimo_ired"
EXEC = REPO / ".agents/skills/marimo-pair/scripts/execute-code.sh"


def main() -> None:
    url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:2718"

    setup = """
import json
import marimo as mo
import polars as pl
from pathlib import Path

import anywidget
import traitlets
import plotly.graph_objects as go

from ired_protein_viewer import ProteinStructureViewer

ROOT = Path(__file__).resolve().parent
""".strip()

    master = """
master_path = ROOT / "data" / "ired-novartis" / "ired-master-table.csv"
master_cols = pl.scan_csv(master_path).collect_schema().names()
df_master_preview = pl.read_csv(master_path, n_rows=4000)
mo.vstack(
    [
        mo.md(
            "## Master screening table (`ired-master-table.csv`)\\n\\n"
            f"**Columns ({len(master_cols)}):** `{'`, `'.join(master_cols)}`\\n\\n"
            "Preview (first rows; full file is larger):"
        ),
        df_master_preview.select(
            ["sample_id", "layout_code", "row", "column", "mutation", "plate_code"]
        ).head(8),
    ]
)
""".strip()

    md_structure = """
mo.md(
    r\"\"\"
## Sequence → PDB mapping and structure views

We align single-point assay numbering to **7OG3** chain **A**, build residue-level effect JSON maps,
then render:

1. **Interactive** 3D (3Dmol.js via anywidget): cartoon + molecular surface colored by assay signal.
2. **Static PNGs** (Plotly + Kaleido): Cα trace colored by the same maps (good for slides or README exports).
\"\"\"
)
""".strip()

    md_widget = """
mo.md(
    r\"\"\"
### Interactive 3D controls

Use the dropdowns, then scroll to the viewer. **Conversion** uses a blue–white–red ramp; **chirality** uses purple–white–orange.
\"\"\"
)
""".strip()

    controls = """
color_mode_dropdown = mo.ui.dropdown(
    options=["conversion", "chirality"],
    value="conversion",
    label="Color mode",
)
aggregation_mode_dropdown = mo.ui.dropdown(
    options=["mean", "max"],
    value="mean",
    label="Mutational effect summary",
)
mo.vstack([color_mode_dropdown, aggregation_mode_dropdown])
""".strip()

    legend = """
mode = color_mode_dropdown.value
aggregation = aggregation_mode_dropdown.value

if mode == "chirality":
    effect_map = (
        json.loads(effects_chirality_max_json)
        if aggregation == "max"
        else json.loads(effects_chirality_mean_json)
    )
    low_color = "purple"
    high_color = "orange"
    metric_base = "r_enantiomeric_excess"
else:
    effect_map = (
        json.loads(effects_conversion_max_json)
        if aggregation == "max"
        else json.loads(effects_conversion_mean_json)
    )
    low_color = "blue"
    high_color = "red"
    metric_base = "conversion (mean column)"

summary_word = "maximum" if aggregation == "max" else "average"
metric = f"{summary_word} {metric_base}"

vals = [float(v) for v in effect_map.values()]
vmin = min(vals) if vals else 0.0
vmax = max(vals) if vals else 0.0

mo.md(
    f\"\"\"
### Color legend ({mode}, {aggregation})

- **Low {metric}** → **{low_color}** (min = `{vmin:.4f}`)
- **Mid-range values** → **white**
- **High {metric}** → **{high_color}** (max = `{vmax:.4f}`)
- **Gray residues** → no measurement available
\"\"\"
)
""".strip()

    viewer_init = """
structure_viewer = ProteinStructureViewer(
    pdb_text=pdb_text,
    pdb_chain=pdb_chain,
    effects_conversion_mean=effects_conversion_mean_json,
    effects_conversion_max=effects_conversion_max_json,
    effects_chirality_mean=effects_chirality_mean_json,
    effects_chirality_max=effects_chirality_max_json,
    color_mode="conversion",
    aggregation_mode="mean",
)
structure_viewer
""".strip()

    viewer_show = """
structure_viewer.color_mode = color_mode_dropdown.value
structure_viewer.aggregation_mode = aggregation_mode_dropdown.value
mo.ui.anywidget(structure_viewer)
""".strip()

    single = (SNIP / "ired_single_point_cell.py").read_text()
    pos = (SNIP / "ired_position_effects_cell.py").read_text()
    pdb = (SNIP / "ired_pdb_effect_maps_cell.py").read_text()
    static = (SNIP / "ired_static_png_cell.py").read_text()

    kernel = f"""
import marimo._code_mode as cm

async with cm.get_context() as ctx:
    for pkg in ("plotly", "kaleido", "anywidget", "traitlets"):
        ctx.packages.add(pkg)

    ctx.edit_cell("Hbol", code={setup!r})
    ctx.run_cell("Hbol")

    cid = ctx.create_cell({master!r}, name="load_master_table_preview")
    ctx.run_cell(cid)

    cid = ctx.create_cell({md_structure!r}, name="structure_section_markdown")
    ctx.run_cell(cid)

    cid = ctx.create_cell({single!r}, name="build_df_single_point")
    ctx.run_cell(cid)

    cid = ctx.create_cell({pos!r}, name="build_position_effect_tables")
    ctx.run_cell(cid)

    cid = ctx.create_cell({pdb!r}, name="pdb_sequence_validation_and_effect_maps")
    ctx.run_cell(cid)

    cid = ctx.create_cell({md_widget!r}, name="structure_viewer_markdown")
    ctx.run_cell(cid)

    cid = ctx.create_cell({controls!r}, name="protein_structure_coloring_controls")
    ctx.run_cell(cid)

    cid = ctx.create_cell({legend!r}, name="structure_viewer_color_legend")
    ctx.run_cell(cid)

    cid = ctx.create_cell({viewer_init!r}, name="protein_structure_viewer_init")
    ctx.run_cell(cid)

    cid = ctx.create_cell({viewer_show!r}, name="protein_structure_viewer_show")
    ctx.run_cell(cid)

    cid = ctx.create_cell({static!r}, name="protein_static_png_exports")
    ctx.run_cell(cid)
"""

    subprocess.run(
        ["bash", str(EXEC), "--url", url],
        input=kernel,
        text=True,
        cwd=str(REPO),
        check=True,
    )


if __name__ == "__main__":
    main()
