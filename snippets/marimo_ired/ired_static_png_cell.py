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
