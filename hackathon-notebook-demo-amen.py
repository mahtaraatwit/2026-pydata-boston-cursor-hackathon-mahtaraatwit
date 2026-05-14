# /// script
# dependencies = [
#     "anywidget==0.11.0",
#     "kaleido==1.3.0",
#     "marimo",
#     "plotly==6.7.0",
#     "polars==1.40.1",
#     "traitlets==5.15.0",
# ]
# requires-python = ">=3.14"
# ///

import marimo

__generated_with = "0.23.6"
app = marimo.App(width="medium")


@app.cell
def _():
    import json
    import marimo as mo
    import polars as pl
    from pathlib import Path

    import anywidget
    import traitlets
    import plotly.graph_objects as go

    from ired_protein_viewer import ProteinStructureViewer

    ROOT = Path(__file__).resolve().parent
    return ProteinStructureViewer, ROOT, go, json, mo, pl


@app.cell(hide_code=True)
def intro_ired_markdown(mo):
    mo.md(r"""
    # IRED Novartis data (quick look)

    Plate metadata plus two assay tables from an **imine reductase** campaign
    ([Ma *et al.*, *ACS Catal.* **2021**](https://doi.org/10.1021/acscatal.1c02786)):
    **conversion** (`mean` in `si_002`) and **enantiomeric excess** (`si_003`).
    """)
    return


@app.cell(hide_code=True)
def load_layouts(ROOT, pl):
    layouts_path = ROOT / "data" / "ired-novartis" / "layouts.csv"
    df_layouts = pl.read_csv(layouts_path)
    df_layouts.head(10)
    return


@app.cell(hide_code=True)
def load_conversion_top_mean(ROOT, pl):
    conversion_path = ROOT / "data" / "ired-novartis" / "cs1c02786_si_002.csv"
    df_conversion = pl.read_csv(conversion_path)
    df_conversion.select(["mutation", "mean", "count"]).sort("mean", descending=True).head(10)
    return (df_conversion,)


@app.cell(hide_code=True)
def chirality_by_experiment(ROOT, pl):
    chirality_path = ROOT / "data" / "ired-novartis" / "cs1c02786_si_003.csv"
    df_chirality = pl.read_csv(chirality_path)
    experiment_summary = (
        df_chirality.group_by("experiment")
        .agg(
            pl.len().alias("n_variants"),
            pl.col("r_enantiomeric_excess").mean().alias("mean_ee"),
            pl.col("r_enantiomeric_excess").max().alias("max_ee"),
        )
        .sort("n_variants", descending=True)
    )
    experiment_summary
    return (df_chirality,)


@app.cell(hide_code=True)
def inner_join_chirality_conversion(df_chirality, df_conversion):
    mutation_both = (
        df_chirality.select(["mutation", "r_enantiomeric_excess", "experiment"])
        .join(df_conversion.select(["mutation", "mean"]), on="mutation", how="inner")
        .sort("r_enantiomeric_excess", descending=True)
    )
    mutation_both.head(12)
    return


@app.cell(hide_code=True)
def load_master_table_preview(ROOT, mo, pl):
    master_path = ROOT / "data" / "ired-novartis" / "ired-master-table.csv"
    master_cols = pl.scan_csv(master_path).collect_schema().names()
    df_master_preview = pl.read_csv(master_path, n_rows=4000)
    mo.vstack(
        [
            mo.md(
                "## Master screening table (`ired-master-table.csv`)\n\n"
                f"**Columns ({len(master_cols)}):** `{'`, `'.join(master_cols)}`\n\n"
                "Preview (first rows; full file is larger):"
            ),
            df_master_preview.select(
                ["sample_id", "layout_code", "row", "column", "mutation", "plate_code"]
            ).head(8),
        ]
    )
    return


@app.cell(hide_code=True)
def structure_section_markdown(mo):
    mo.md(r"""
    ## Sequence → PDB mapping and structure views

    We align single-point assay numbering to **7OG3** chain **A**, build residue-level effect JSON maps,
    then render:

    1. **Interactive** 3D (3Dmol.js via anywidget): cartoon + molecular surface colored by assay signal.
    2. **Static PNGs** (Plotly + Kaleido): Cα trace colored by the same maps (good for slides or README exports).
    """)
    return


@app.cell(hide_code=True)
def build_df_single_point(df_conversion, pl):
    df_single_point = (
        df_conversion.filter(pl.col("mutation").is_not_null())
        .filter(~pl.col("mutation").str.contains(";"))
        .filter(pl.col("mutation").str.contains(r"^[A-Z]\d+[A-Z]$"))
        .with_columns(
            [
                pl.col("mutation")
                .str.extract(r"^[A-Z](\d+)[A-Z]$", 1)
                .cast(pl.Int64)
                .alias("position"),
                pl.col("mutation")
                .str.extract(r"^[A-Z]\d+([A-Z])$", 1)
                .alias("mut_aa"),
            ]
        )
    )

    df_single_point.head(10)

    return (df_single_point,)


@app.cell(hide_code=True)
def build_position_effect_tables(df_chirality, df_single_point, pl):
    df_single_point_chirality = (
        df_chirality.filter(pl.col("mutation").is_not_null())
        .filter(~pl.col("mutation").str.contains(";"))
        .filter(pl.col("mutation").str.contains(r"^[A-Z]\d+[A-Z]$"))
        .with_columns(
            pl.col("mutation")
            .str.extract(r"^[A-Z](\d+)[A-Z]$", 1)
            .cast(pl.Int64)
            .alias("position")
        )
    )

    df_position_effect_conversion = (
        df_single_point.group_by("position")
        .agg(pl.col("mean").mean().alias("avg_conversion"))
        .sort("position")
    )

    df_position_effect_chirality = (
        df_single_point_chirality.group_by("position")
        .agg(pl.col("r_enantiomeric_excess").mean().alias("avg_chirality"))
        .sort("position")
    )

    df_position_effect_conversion_max = (
        df_single_point.group_by("position")
        .agg(pl.col("mean").max().alias("max_conversion"))
        .sort("position")
    )

    df_position_effect_chirality_max = (
        df_single_point_chirality.group_by("position")
        .agg(pl.col("r_enantiomeric_excess").max().alias("max_chirality"))
        .sort("position")
    )

    all_positions = (
        pl.concat(
            [
                df_position_effect_conversion.select("position"),
                df_position_effect_conversion_max.select("position"),
                df_position_effect_chirality.select("position"),
                df_position_effect_chirality_max.select("position"),
            ]
        )
        .unique()
        .sort("position")
    )

    df_position_effects = (
        all_positions.join(df_position_effect_conversion, on="position", how="left")
        .join(df_position_effect_conversion_max, on="position", how="left")
        .join(df_position_effect_chirality, on="position", how="left")
        .join(df_position_effect_chirality_max, on="position", how="left")
    )

    df_position_effects.head(12)

    return (
        df_position_effect_chirality,
        df_position_effect_chirality_max,
        df_position_effect_conversion,
        df_position_effect_conversion_max,
    )


@app.cell(hide_code=True)
def pdb_sequence_validation_and_effect_maps(
    ROOT,
    df_position_effect_chirality,
    df_position_effect_chirality_max,
    df_position_effect_conversion,
    df_position_effect_conversion_max,
    df_single_point,
    json,
    mo,
    pl,
):
    AA3_TO_AA1 = {
        "ALA": "A",
        "ARG": "R",
        "ASN": "N",
        "ASP": "D",
        "CYS": "C",
        "GLN": "Q",
        "GLU": "E",
        "GLY": "G",
        "HIS": "H",
        "ILE": "I",
        "LEU": "L",
        "LYS": "K",
        "MET": "M",
        "MSE": "M",
        "PHE": "F",
        "PRO": "P",
        "SER": "S",
        "THR": "T",
        "TRP": "W",
        "TYR": "Y",
        "VAL": "V",
    }


    def parse_pdb_chain_residues(pdb_text: str, chain_id: str) -> dict[int, str]:
        residues: dict[int, str] = {}
        for line in pdb_text.splitlines():
            if len(line) < 27:
                continue
            record = line[0:6].strip()
            if record not in {"ATOM", "HETATM"}:
                continue
            if line[21:22] != chain_id:
                continue
            resname = line[17:20].strip()
            try:
                resseq = int(line[22:26])
            except ValueError:
                continue
            aa = AA3_TO_AA1.get(resname)
            if aa is None:
                continue
            residues[resseq] = aa
        return residues


    def build_effect_map(table, value_col: str) -> dict[str, float]:
        out: dict[str, float] = {}
        for row in table.iter_rows(named=True):
            val = row[value_col]
            if val is None:
                continue
            pdb_res = int(row["position"]) + pdb_residue_offset
            out[str(pdb_res)] = float(val)
        return out


    pdb_path = ROOT / "data" / "ired-novartis" / "7OG3.pdb"
    pdb_text = pdb_path.read_text()
    pdb_chain = "A"
    pdb_residues = parse_pdb_chain_residues(pdb_text, pdb_chain)

    wt_by_position = (
        df_single_point.group_by("position")
        .agg(pl.col("mutation").str.slice(0, 1).first().alias("wt_aa"))
        .sort("position")
    )

    positions = wt_by_position.get_column("position").to_list()
    wt_aas = wt_by_position.get_column("wt_aa").to_list()

    best_offset = 0
    best_score = -1
    for offset in range(-20, 21):
        score = 0
        for pos, wt in zip(positions, wt_aas):
            pdb_aa = pdb_residues.get(pos + offset)
            if pdb_aa == wt:
                score += 1
        if score > best_score:
            best_score = score
            best_offset = offset

    pdb_residue_offset = best_offset

    mapping_rows = []
    for pos, wt in zip(positions, wt_aas):
        pdb_resi = pos + pdb_residue_offset
        pdb_aa = pdb_residues.get(pdb_resi)
        mapping_rows.append(
            {
                "assay_position": pos,
                "pdb_residue": pdb_resi,
                "wt_aa": wt,
                "pdb_aa": pdb_aa,
                "match": pdb_aa == wt if pdb_aa is not None else False,
                "has_structure": pdb_aa is not None,
            }
        )

    df_pdb_mapping_validation = pl.DataFrame(mapping_rows)

    mapping_matched = df_pdb_mapping_validation.filter(pl.col("match")).height
    mapping_mismatch = df_pdb_mapping_validation.filter(
        pl.col("has_structure") & (~pl.col("match"))
    ).height
    mapping_unmapped = df_pdb_mapping_validation.filter(
        ~pl.col("has_structure")
    ).height

    # Mean maps (legacy + new names)
    effects_conversion_mean = build_effect_map(
        df_position_effect_conversion, "avg_conversion"
    )
    effects_chirality_mean = build_effect_map(
        df_position_effect_chirality, "avg_chirality"
    )

    # Max maps
    effects_conversion_max = build_effect_map(
        df_position_effect_conversion_max, "max_conversion"
    )
    effects_chirality_max = build_effect_map(
        df_position_effect_chirality_max, "max_chirality"
    )

    # Keep original names for compatibility
    effects_conversion_json = json.dumps(effects_conversion_mean)
    effects_chirality_json = json.dumps(effects_chirality_mean)

    # Explicit mean/max names for new controls
    effects_conversion_mean_json = json.dumps(effects_conversion_mean)
    effects_conversion_max_json = json.dumps(effects_conversion_max)
    effects_chirality_mean_json = json.dumps(effects_chirality_mean)
    effects_chirality_max_json = json.dumps(effects_chirality_max)

    mo.vstack(
        [
            mo.md(
                f"PDB mapping chain **{pdb_chain}**, residue offset **{pdb_residue_offset}** "
                f"(best agreement with assay wild-type letters): matched **{mapping_matched}**, "
                f"mismatch **{mapping_mismatch}**, unmapped **{mapping_unmapped}**."
            ),
            df_pdb_mapping_validation.filter(
                pl.col("has_structure") & (~pl.col("match"))
            ).head(12),
        ]
    )

    return (
        effects_chirality_max_json,
        effects_chirality_mean_json,
        effects_conversion_max_json,
        effects_conversion_mean_json,
        pdb_chain,
        pdb_text,
    )


@app.cell(hide_code=True)
def structure_viewer_markdown(mo):
    mo.md(r"""
    ### Interactive 3D controls

    Use the dropdowns, then scroll to the viewer. **Conversion** uses a blue–white–red ramp; **chirality** uses purple–white–orange.
    """)
    return


@app.cell(hide_code=True)
def protein_structure_coloring_controls(mo):
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
    return aggregation_mode_dropdown, color_mode_dropdown


@app.cell(hide_code=True)
def structure_viewer_color_legend(
    aggregation_mode_dropdown,
    color_mode_dropdown,
    effects_chirality_max_json,
    effects_chirality_mean_json,
    effects_conversion_max_json,
    effects_conversion_mean_json,
    json,
    mo,
):
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
        f"""
    ### Color legend ({mode}, {aggregation})

    - **Low {metric}** → **{low_color}** (min = `{vmin:.4f}`)
    - **Mid-range values** → **white**
    - **High {metric}** → **{high_color}** (max = `{vmax:.4f}`)
    - **Gray residues** → no measurement available
    """
    )
    return


@app.cell(hide_code=True)
def protein_structure_viewer_init(
    ProteinStructureViewer,
    effects_chirality_max_json,
    effects_chirality_mean_json,
    effects_conversion_max_json,
    effects_conversion_mean_json,
    pdb_chain,
    pdb_text,
):
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
    return (structure_viewer,)


@app.cell(hide_code=True)
def protein_structure_viewer_show(
    aggregation_mode_dropdown,
    color_mode_dropdown,
    mo,
    structure_viewer,
):
    structure_viewer.color_mode = color_mode_dropdown.value
    structure_viewer.aggregation_mode = aggregation_mode_dropdown.value
    mo.ui.anywidget(structure_viewer)
    return


@app.cell(hide_code=True)
def protein_static_png_exports(
    effects_chirality_mean_json,
    effects_conversion_mean_json,
    go,
    json,
    mo,
    pdb_chain,
    pdb_text,
):
    def _pdb_ca_chain_a(pdb_text: str, chain: str):
        rows = []
        for line in pdb_text.splitlines():
            if len(line) < 54:
                continue
            if line[0:6].strip() != "ATOM":
                continue
            if line[21:22] != chain:
                continue
            if line[12:16].strip() != "CA":
                continue
            try:
                resi = int(line[22:26])
                x = float(line[30:38])
                y = float(line[38:46])
                z = float(line[46:54])
            except ValueError:
                continue
            rows.append((resi, x, y, z))
        return rows


    conv_map = json.loads(effects_conversion_mean_json)
    chiral_map = json.loads(effects_chirality_mean_json)
    ca_rows = _pdb_ca_chain_a(pdb_text, pdb_chain)

    xs_c = []
    ys_c = []
    zs_c = []
    vals_c = []
    texts_c = []
    for resi, x, y, z in ca_rows:
        v = conv_map.get(str(resi))
        xs_c.append(x)
        ys_c.append(y)
        zs_c.append(z)
        vals_c.append(float(v) if v is not None else float("nan"))
        texts_c.append(f"PDB res {resi}<br>mean conv: {v}")

    fig_conv = go.Figure(
        data=go.Scatter3d(
            x=xs_c,
            y=ys_c,
            z=zs_c,
            mode="markers",
            marker=dict(
                size=4,
                color=vals_c,
                colorscale="RdYlBu_r",
                showscale=True,
                colorbar=dict(title="mean conv"),
            ),
            text=texts_c,
            hovertemplate="%{text}<extra></extra>",
        )
    )
    fig_conv.update_layout(
        title="Cα trace colored by average conversion (static PNG)",
        height=480,
        width=640,
        scene=dict(aspectmode="data"),
        margin=dict(l=0, r=0, t=40, b=0),
    )

    xs_h = []
    ys_h = []
    zs_h = []
    vals_h = []
    texts_h = []
    for resi, x, y, z in ca_rows:
        v = chiral_map.get(str(resi))
        xs_h.append(x)
        ys_h.append(y)
        zs_h.append(z)
        vals_h.append(float(v) if v is not None else float("nan"))
        texts_h.append(f"PDB res {resi}<br>mean EE: {v}")

    fig_chiral = go.Figure(
        data=go.Scatter3d(
            x=xs_h,
            y=ys_h,
            z=zs_h,
            mode="markers",
            marker=dict(
                size=4,
                color=vals_h,
                colorscale="PuOr",
                showscale=True,
                colorbar=dict(title="mean EE"),
            ),
            text=texts_h,
            hovertemplate="%{text}<extra></extra>",
        )
    )
    fig_chiral.update_layout(
        title="Cα trace colored by average chirality (static PNG)",
        height=480,
        width=640,
        scene=dict(aspectmode="data"),
        margin=dict(l=0, r=0, t=40, b=0),
    )

    png_conv = fig_conv.to_image(format="png", scale=2)
    png_chiral = fig_chiral.to_image(format="png", scale=2)

    mo.vstack(
        [
            mo.md("### Raster snapshots (Plotly + Kaleido)"),
            mo.hstack([mo.image(png_conv), mo.image(png_chiral)]),
        ]
    )

    return


if __name__ == "__main__":
    app.run()
