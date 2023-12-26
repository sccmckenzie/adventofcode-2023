import re
import polars as pl

# predefine variables, mostly for first iteration
input_path = 'input_demo.txt'
seeds = pl.Series(dtype=pl.UInt64)
map_coord = {}
map_current = None

# read seeds and mapping categories
# not fully parsing yet
with open(input_path, 'r') as file:
    for num, line in enumerate(file, 1):
        line = line.strip()

        match_seed = re.fullmatch("^seeds:.+$", line)
        match_mapname = re.fullmatch("^.+\\smap:$", line)
        match_intonly = re.fullmatch("^[\\d\\s]+$", line)

        if match_seed is not None:
            seeds = pl.Series("seed", re.findall("\\d+", line)).cast(pl.UInt64)
        elif match_mapname is not None:
            map_current = line.replace(' map:', '')
            map_coord[map_current] = {"start": num, "end": num}
        elif match_intonly is not None:
            map_coord[map_current]["end"] = num

# create enum object (now that we have all possible values)
# e.g. 'seed-to-soil', 'soil-to-fertilizer'
map_enum = pl.Enum(list(map_coord.keys()))

# predefine empty almanac for first iteration
almanac = pl.LazyFrame(
    {
        "mapping": pl.Series(dtype=map_enum),
        "dest_lower": pl.Series(dtype=pl.UInt64),
        "source_lower": pl.Series(dtype=pl.UInt64),
        "length": pl.Series(dtype=pl.UInt64)
    }
)

for key in map_coord:
    start = map_coord[key]["start"]
    end = map_coord[key]["end"]
    almanac = pl.concat(
        [
            almanac,
            pl.scan_csv(input_path,
                        has_header=False,
                        separator=' ',
                        skip_rows=start,
                        n_rows=(end - start),
                        new_columns=['dest_lower', 'source_lower', 'length'],
                        dtypes=[pl.Utf8] * 3)
            .select(
                pl.Series("mapping", [key], dtype=map_enum),
                pl.all().cast(dtype=pl.UInt64))
        ]
    )

almanac = almanac.with_columns(
    (pl.col("source_lower") + pl.col("length") - 1).alias("source_upper"))
out = pl.DataFrame(seeds)


for num, mapping in enumerate(list(map_coord.keys())):
    source, dest = mapping.split('-to-')
    existing_fields = out.columns
    out = out.lazy()
    out = (
        out
        .join(
            almanac.filter(pl.col("mapping") == pl.Series(
            [mapping], dtype=map_enum)),
            how="cross"
        )
        .with_columns(
            ((pl.col(source) >= pl.col("source_lower")) &
            (pl.col(source) <= pl.col("source_upper")))
            .alias("is_captured")
        )
        .with_columns(
            pl.when(pl.col("is_captured")).then(pl.col("dest_lower") + pl.col(source) - pl.col("source_lower")).alias(dest)
        )
        .group_by(existing_fields + ["mapping"])
        .agg(pl.col(dest).max().alias(dest))
        .with_columns(pl.when(pl.col(dest).is_null()).then(pl.col(source)).otherwise(pl.col(dest)).alias(dest))
        .select(existing_fields + [dest])
    ).collect()

min_location = out.group_by(True).agg(
    pl.min("location")
)

print(min_location)
