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
