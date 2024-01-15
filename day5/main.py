import re
import polars as pl

# predefine variables, mostly for first iteration
input_path = 'input.txt'
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

# populate almanac
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

# define source upper
almanac = almanac.with_columns(
    (pl.col("source_lower") + pl.col("length") - 1).alias("source_upper"))

# initiate output object
# out = pl.DataFrame(seeds)

# traverse almanac for each seed
# for num, mapping in enumerate(map_enum.categories):
#     source, dest = mapping.split('-to-')
#     existing_fields = out.columns
#     out = out.lazy()
#     out = (
#         out
#         .join(
#             almanac.filter(pl.col("mapping") == pl.Series(
#             [mapping], dtype=map_enum)),
#             how="cross"
#         )
#         .with_columns(
#             ((pl.col(source) >= pl.col("source_lower")) &
#             (pl.col(source) <= pl.col("source_upper")))
#             .alias("is_captured")
#         )
#         .with_columns(
#             pl.when(pl.col("is_captured")).then(pl.col("dest_lower") + pl.col(source) - pl.col("source_lower")).alias(dest)
#         )
#         .group_by(existing_fields + ["mapping"])
#         .agg(pl.col(dest).max().alias(dest))
#         .with_columns(pl.when(pl.col(dest).is_null()).then(pl.col(source)).otherwise(pl.col(dest)).alias(dest))
#         .select(existing_fields + [dest])
#     ).collect()

# find min location
# min_location = out.group_by(True).agg(
#     pl.min("location")
# )

# print(min_location)

# Part 2
ranges_source = (
pl.DataFrame(seeds)
    .with_row_count(name="grp")
    .with_columns((pl.col("grp") // 2),
                  pl.Series("nm", ["lower", "size"] * (seeds.len() // 2)))
    .pivot(values="seed", index="grp", columns="nm")
    .select(pl.col("grp"),
            pl.col("lower"),
            (pl.col("lower") + pl.col("size") - 1).alias("upper"))
)

almanac2 = almanac.collect().select(pl.exclude("length"))

bound_status = pl.Enum(["below", "captured", "above"])

def find_ranges(ranges_source: pl.DataFrame, ranges_destination: pl.DataFrame) -> pl.DataFrame:
    ranges_matching = (
        ranges_source
            .join(
                ranges_destination,
                how="cross"
            )
            .with_columns(
                pl.when(pl.col("source_lower") < pl.col("lower"))
                    .then(-1)
                    .when(pl.col("source_lower") > pl.col("upper"))
                    .then(1)
                    .otherwise(0)
                    .alias("bound_status_left"),
                pl.when(pl.col("source_upper") < pl.col("lower"))
                    .then(-1)
                    .when(pl.col("source_upper") > pl.col("upper"))
                    .then(1)
                    .otherwise(0)
                    .alias("bound_status_right")
            )
            .with_columns(
                pl.when((pl.col('bound_status_left') == -1) & 
                        (pl.col('bound_status_right').is_in([0, 1])))
                        .then('lower')
                        .when(pl.col('bound_status_left') == 0)
                        .then('source_lower')
                        .otherwise(None)    
                        .alias('captured_source_start'),
                pl.when((pl.col('bound_status_left').is_in([-1, 0])) & 
                        (pl.col('bound_status_right') == 1))
                        .then('upper')
                        .when(pl.col('bound_status_right') == 0)
                        .then('source_upper')
                        .otherwise(None)
                        .alias('captured_source_end')
            )
            .filter(
                pl.col('captured_source_start').is_not_null()
                # captured_source_end should also be non-null where captured_source_start is non null
                # in a production setting violations of this assumption should raise exception
            )
            .select(
                pl.col('grp'),
                pl.col('lower'),
                pl.col('upper'),
                pl.col('captured_source_start'),
                pl.col('captured_source_end'),
                (pl.col('captured_source_start') - pl.col('source_lower') + pl.col('dest_lower'))
                .alias('captured_dest_start'),
                (pl.col('captured_source_end') - pl.col('source_lower') + pl.col('dest_lower'))
                .alias('captured_dest_end'),
            )
            # .filter(
            #     (pl.col('captured_dest_end') - pl.col('captured_dest_start')) !=
            #      (pl.col('captured_source_end') - pl.col('captured_source_start'))
            # ) # this should always return 0 records

    )

    out = (
            ranges_matching
            .select(pl.col("captured_dest_start").alias("lower"),
                    pl.col("captured_dest_end").alias("upper"))
    )
    
    for grp in ranges_source.select("grp").to_series().to_list():
        ranges_matching_grp = ranges_matching.filter(pl.col('grp') == grp)
        if ranges_matching_grp.height == 0:
            out = out.vstack(
                pl.DataFrame(
                    {
                        "lower": ranges_source.filter(pl.col('grp') == grp).select("lower").to_series(),
                        "upper": ranges_source.filter(pl.col('grp') == grp).select("upper").to_series(),
                    }
                ))
        else:
            # for min matching range (y), does lower bound match input range global lower bound?
            range_min = ranges_matching_grp.sort('captured_source_start').slice(0, 1)
            if range_min.filter(pl.col('lower') == pl.col('captured_source_start')).height == 1:
                pass
            else:
                out = out.vstack(
                    pl.DataFrame(
                        {
                            "lower": range_min.select("lower").to_series(),
                            "upper": range_min.select("captured_source_start").to_series() - 1,
                        }
                ))
            # for max matching range (y), does upper bound match input range global upper bound?
            range_max = ranges_matching_grp.sort('captured_source_end', descending=True).slice(0, 1)
            if range_max.filter(pl.col('upper') == pl.col('captured_source_end')).height == 1:
                pass
            else:
                out = out.vstack(
                    pl.DataFrame(
                        {
                            "lower": range_min.select("captured_source_end").to_series() + 1,
                            "upper": range_min.select("upper").to_series(),
                        }
                ))
            # are there any gaps between neighboring matching ranges?
            if ranges_matching_grp.height > 1:
                for i in range(0, ranges_matching_grp.height - 1):
                    is_gap_between_neighbors = (
                        ranges_matching_grp.slice(i, 1).select(pl.col("captured_source_end") + 1).to_series() !=
                        ranges_matching_grp.slice(i + 1, 1).select("captured_source_start").to_series()
                    )[0]
                    if is_gap_between_neighbors:
                        out = out.vstack(
                            pl.DataFrame(
                                {
                                    "lower": ranges_matching_grp.slice(i, 1).select(pl.col("captured_source_end") + 1).to_series(),
                                    "upper": ranges_matching_grp.slice(i + 1, 1).select(pl.col("captured_source_start") - 1).to_series(),
                                }
                        ))
    
    out = out.with_row_count(name='grp')

    return out

for mapping in map_enum.categories:
    ranges_destination = (
        almanac2
            .filter(pl.col("mapping") == mapping)
            .select(pl.exclude("mapping"))
    )

    ranges_source = find_ranges(ranges_source, ranges_destination)

print(ranges_source.select('lower').min())

# test_input = (
#     almanac2
#         .filter(pl.col("mapping") == "seed-to-soil")
#         .select(pl.exclude("mapping"))
# )

# print(find_ranges(ranges_source, test_input))


# brute-force method
# global_min = None
# for i in range(0, seeds.len(), 2):
#     print(seeds[i])
#     for i in range(seeds[i], seeds[i] + seeds[i + 1], 1):
#         print(i)
#         # initiate output object
#         out = pl.DataFrame(pl.Series("seed", [i]).cast(pl.UInt64))
#         # traverse almanac for each seed
#         for num, mapping in enumerate(list(map_coord.keys())):
#             source, dest = mapping.split('-to-')
#             existing_fields = out.columns
#             out = out.lazy()
#             out = (
#                 out
#                 .join(
#                     almanac.filter(pl.col("mapping") == pl.Series(
#                     [mapping], dtype=map_enum)),
#                     how="cross"
#                 )
#                 .with_columns(
#                     ((pl.col(source) >= pl.col("source_lower")) &
#                     (pl.col(source) <= pl.col("source_upper")))
#                     .alias("is_captured")
#                 )
#                 .with_columns(
#                     pl.when(pl.col("is_captured")).then(pl.col("dest_lower") + pl.col(source) - pl.col("source_lower")).alias(dest)
#                 )
#                 .group_by(existing_fields + ["mapping"])
#                 .agg(pl.col(dest).max().alias(dest))
#                 .with_columns(pl.when(pl.col(dest).is_null()).then(pl.col(source)).otherwise(pl.col(dest)).alias(dest))
#                 .select(existing_fields + [dest])
#             ).collect()
#         print(out)
#         location_result = out.select('location').to_series()[0]
#         if global_min is None:
#             global_min = location_result
#         elif location_result < global_min:
#             global_min = location_result
        
# print(global_min)