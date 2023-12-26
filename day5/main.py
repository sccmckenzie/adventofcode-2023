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



(
    pl.LazyFrame(seeds)
    .join(
        almanac.filter(pl.col("mapping") == pl.Series(
            ["seed-to-soil"], dtype=map_enum)),
        how="cross"
    )
    .with_columns(
        ((pl.col("seed") >= pl.col("source_lower")) &
         (pl.col("seed") <= pl.col("source_upper")))
        .alias("is_captured")
    )
    .with_columns(
        pl.when(pl.col("is_captured")).then(pl.col("dest_lower") + pl.col("seed") - pl.col("source_lower")).alias("dest")
    )
    .group_by(["seed", "mapping"])
    .agg(pl.col("dest").max().alias("soil"))
    .with_columns(soil=pl.when(pl.col("soil").is_null()).then(pl.col("seed")).otherwise(pl.col("soil")))
    .collect()
)

# full_mapping = pl.DataFrame(seeds).join(
#     almanac.filter(pl.col("mapping") == "seed-to-soil").rename({"coord_source": "seed"}),
#     on="seed",
#     how="left"
# ).select(
#     pl.col("seed"),
#     pl.when(pl.col("coord_dest").is_null()).then(pl.col("seed")).otherwise(pl.col("coord_dest")).alias("soil")
# ).join(
#     almanac.filter(pl.col("mapping") == "soil-to-fertilizer").rename({"coord_source": "soil"}),
#     on="soil",
#     how="left"
# ).select(
#     pl.col("seed"),
#     pl.col("soil"),
#     pl.when(pl.col("coord_dest").is_null()).then(pl.col("soil")).otherwise(pl.col("coord_dest")).alias("fertilizer")
# ).join(
#     almanac.filter(pl.col("mapping") == "fertilizer-to-water").rename({"coord_source": "fertilizer"}),
#     on="fertilizer",
#     how="left"
# ).select(
#     pl.col("seed"),
#     pl.col("soil"),
#     pl.col("fertilizer"),
#     pl.when(pl.col("coord_dest").is_null()).then(pl.col("fertilizer")).otherwise(pl.col("coord_dest")).alias("water")
# ).join(
#     almanac.filter(pl.col("mapping") == "water-to-light").rename({"coord_source": "water"}),
#     on="water",
#     how="left"
# ).select(
#     pl.col("seed"),
#     pl.col("soil"),
#     pl.col("fertilizer"),
#     pl.col("water"),
#     pl.when(pl.col("coord_dest").is_null()).then(pl.col("water")).otherwise(pl.col("coord_dest")).alias("light")
# ).join(
#     almanac.filter(pl.col("mapping") == "light-to-temperature").rename({"coord_source": "light"}),
#     on="light",
#     how="left"
# ).select(
#     pl.col("seed"),
#     pl.col("soil"),
#     pl.col("fertilizer"),
#     pl.col("water"),
#     pl.col("light"),
#     pl.when(pl.col("coord_dest").is_null()).then(pl.col("light")).otherwise(pl.col("coord_dest")).alias("temperature")
# ).join(
#     almanac.filter(pl.col("mapping") == "temperature-to-humidity").rename({"coord_source": "temperature"}),
#     on="temperature",
#     how="left"
# ).select(
#     pl.col("seed"),
#     pl.col("soil"),
#     pl.col("fertilizer"),
#     pl.col("water"),
#     pl.col("light"),
#     pl.col("temperature"),
#     pl.when(pl.col("coord_dest").is_null()).then(pl.col("temperature")).otherwise(pl.col("coord_dest")).alias("humidity")
# ).join(
#     almanac.filter(pl.col("mapping") == "humidity-to-location").rename({"coord_source": "humidity"}),
#     on="humidity",
#     how="left"
# ).select(
#     pl.col("seed"),
#     pl.col("soil"),
#     pl.col("fertilizer"),
#     pl.col("water"),
#     pl.col("light"),
#     pl.col("temperature"),
#     pl.col("humidity"),
#     pl.when(pl.col("coord_dest").is_null()).then(pl.col("humidity")).otherwise(pl.col("coord_dest")).alias("location")
# )

# min_location = full_mapping.group_by(True).agg(
#     pl.min("location")
# )

# print(min_location)
