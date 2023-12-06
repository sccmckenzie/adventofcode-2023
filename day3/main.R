library(tidyverse)

mat_df <- read_csv("day3/input.txt", col_names = "input") |>
  rowid_to_column(var = "y") |> 
  mutate(input = str_split(input, pattern = "")) |> 
  unnest_longer(input, indices_include = TRUE, indices_to = "x", values_to = "val") |> 
  mutate(gear_id = cumsum(val == "*"),
         val = ifelse(val == "*", str_c(val, gear_id, sep = ""), val)) |> 
  select(x, y, val)

mat_df0 <- mat_df |> 
  mutate(x_l = x - 1,
         y_l = y,
         x_ul = x - 1,
         y_ul = y - 1,
         x_u = x,
         y_u = y - 1,
         x_ur = x + 1,
         y_ur = y - 1,
         x_r = x + 1,
         y_r = y,
         x_wr = x + 1,
         y_wr = y + 1,
         x_w = x,
         y_w = y + 1,
         x_wl = x - 1,
         y_wl = y + 1,
         len = max(x)) |> 
  mutate(across(x_l:y_wl, .fns = \(x) ifelse(x > len | x < 1, NA_integer_, x)))

mat_df1 <- mat_df0 |> 
  left_join(mat_df, by = join_by(x_l == x, y_l == y), suffix = c("", "_l"), na_matches = "never") |> 
  left_join(mat_df, by = join_by(x_ul == x, y_ul == y), suffix = c("", "_ul"), na_matches = "never") |> 
  left_join(mat_df, by = join_by(x_u == x, y_u == y), suffix = c("", "_u"), na_matches = "never") |> 
  left_join(mat_df, by = join_by(x_ur == x, y_ur == y), suffix = c("", "_ur"), na_matches = "never") |> 
  left_join(mat_df, by = join_by(x_r == x, y_r == y), suffix = c("", "_r"), na_matches = "never") |> 
  left_join(mat_df, by = join_by(x_wr == x, y_wr == y), suffix = c("", "_wr"), na_matches = "never") |> 
  left_join(mat_df, by = join_by(x_w == x, y_w == y), suffix = c("", "_w"), na_matches = "never") |> 
  left_join(mat_df, by = join_by(x_wl == x, y_wl == y), suffix = c("", "_wl"), na_matches = "never") |> 
  select(x, y, contains("val"), contains("gear"))

mat_df2 <- mat_df1 |> 
  mutate(num_id = cumsum(str_detect(val, "^\\d$") & lag(!str_detect(val, "^\\d$"), default = TRUE)), 
         num_id = if_else(str_detect(val, "^\\d$"), num_id, NA_integer_),
         .after = val,
         .by = y) |> 
  filter(!is.na(num_id)) |> 
  group_by(y, num_id) |> 
  mutate(pn_adj = if_any(contains("val_"), \(x) !str_detect(x, pattern = "^(\\.|\\d)$")),
         num_full = as.integer(str_c(val, collapse = "")))

mat_df2 |> 
  group_by(num_full, .add = TRUE) |> 
  summarize(pn_adj = any(pn_adj), .groups = "drop") |> 
  filter(pn_adj) |>
  summarize(pn_sum = sum(num_full))

mat_df2 |> 
  group_by(y, num_id, num_full) |> 
  summarize(gears = list(str_subset(c_across(contains("val_")), "\\*")),
            .groups = "drop") |> 
  unnest_longer(col = gears, values_to = "gear_id") |> 
  distinct(y, num_id, num_full, gear_id) |> 
  group_by(gear_id) |> 
  mutate(adj_cnt = n()) |> 
  filter(adj_cnt == 2) |> 
  summarize(gear_ratio = prod(num_full)) |> 
  summarize(total_gear_ratio = sum(gear_ratio))
