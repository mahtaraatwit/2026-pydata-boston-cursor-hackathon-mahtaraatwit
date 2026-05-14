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
