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
