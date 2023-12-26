import re
import polars as pl

input_path = 'input_partial.txt'
seeds = pl.Series(dtype=pl.UInt32)
current_mapping = None
almanac = pl.DataFrame(
    {
        "mapping": pl.Series(dtype=pl.Categorical),
        "coord_dest": pl.Series(dtype=pl.UInt32),
        "coord_source": pl.Series(dtype=pl.UInt32),
    }
)
with open(input_path, 'r') as file:
    for line in file:
        line = line.strip()
        if re.fullmatch("^seeds:.+$", line) is not None:
            seeds = pl.Series("seed", re.findall("\\d+", line)).cast(pl.UInt32)
        elif re.fullmatch("^.+\\smap:$", line) is not None:
            current_mapping = pl.Series("mapping",
                                        [re.match("^\\S+", line).group(0)], dtype=pl.Categorical)
        elif re.fullmatch("^[\\d\\s]+$", line) is not None:
            line_num = [int(x) for x in re.findall("\\d+", line)]
            coord_dest = pl.Series(
                "coord_dest", range(line_num[0], line_num[0] + line_num[2])).cast(pl.UInt32)
            coord_source = pl.Series(
                "coord_source", range(line_num[1], line_num[1] + line_num[2])).cast(pl.UInt32)
            almanac = pl.concat(
                [
                    almanac,
                    pl.DataFrame(
                        [
                            pl.Series("coord_dest", coord_dest),
                            pl.Series("coord_source", coord_source)
                        ]
                    ).select(current_mapping,
                             pl.col("coord_dest"),
                             pl.col("coord_source"))
                ]
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