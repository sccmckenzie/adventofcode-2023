library(tidyverse)

input <- read_delim("day2/input.txt", delim = ": ", col_names = c("game_id", "raw_observations"))

input_clean <- input |> 
  mutate(game_id = str_extract(game_id, "\\d+") |> as.integer(),
         raw_observations = str_split(raw_observations, "; ")) |> 
  unnest_longer(col = raw_observations) |> 
  mutate(draw_id = row_number(), .by = game_id) |> 
  mutate(raw_observations = str_split(raw_observations, ", ")) |> 
  unnest_longer(col = raw_observations) |> 
  separate_wider_delim(raw_observations, names = c("amount", "color"), delim = " ") |> 
  mutate(amount = as.integer(amount)) |> 
  relocate(draw_id, color, amount, .after = game_id)


total_red <- 12
total_green <- 13
total_blue <- 14

total <- enframe(c("red" = total_red, "green" = total_green, "blue" = total_blue), name = "color", value = "limit")

input_clean |> 
  left_join(total, by = join_by(color)) |> 
  mutate(is_game_valid = !as.logical(max(amount > limit)), .by = c(game_id)) |> 
  filter(is_game_valid) |> 
  distinct(game_id) |> 
  summarize(total = sum(game_id))

input_clean |> 
  group_by(game_id, color) |> 
  summarize(min_required_amount = max(amount)) |> 
  summarize(game_power = prod(min_required_amount)) |> 
  summarize(total_power = sum(game_power))
