library(tidyverse)

# Part 1
df_combined <- read_csv("day4/input.txt", col_names = "raw") |> 
  separate_wider_delim(raw, names = c("card", "winners", "hand"), delim = regex("(:|\\|)")) |> 
  mutate(card = str_extract(card, "\\d+") |> as.integer(),
         across(winners:hand, str_trim),
         across(winners:hand, \(x) str_split(x, pattern = "\\s+")))

df_winners <- df_combined |> 
  select(card, winners) |> 
  unnest_longer(col = winners)

df_hand <- df_combined |> 
  select(card, hand) |> 
  unnest_longer(col = hand)

df_hand |> 
  inner_join(df_winners, by = join_by(card, hand == winners)) |> 
  count(card) |> 
  mutate(num_points = 2 ^ (n - 1)) |> 
  summarize(total_points = sum(num_points))
  
# Part 2
df0 <- df_hand |> 
  inner_join(df_winners, by = join_by(card, hand == winners)) |> 
  count(card) %>% 
  left_join(df_hand |> distinct(card), ., by = join_by(card)) |> 
  replace_na(list(n = 0))

matches_rev <- rev(df0$n) # vector containing number of matches per card (in reverse order)
count_desc_copies <- function(num_direct_desc, lineage) {
  num_direct_desc + sum(tail(lineage, num_direct_desc))
}

cum_matches <- reduce(matches_rev, \(x, y) c(x, count_desc_copies(y, x)))
sum(cum_matches + 1)

# original method (invalid)
# df_flag <- df0 %>%  
#   mutate(len = nrow(.)) |> 
#   rowwise() |> 
#   mutate(flag = list(c(rep(0, card), rep(1, n), rep(0, len - n - card)))) |> 
#   select(card, flag) |>
#   pivot_wider(values_from = flag, names_from = card, names_prefix = "f") |> 
#   unnest_longer(everything())
# 
# bind_cols(df0, df_flag) |> 
#   rowwise() |> 
#   mutate(num_occur_root = sum(c_across(matches("f\\d+"))),
#          num_occur = 2 ^ num_occur_root,
#          .after = n) |> 
#   ungroup() |> 
#   summarize(total_cards = sum(num_occur))

# new method (verbose)
# df2 <- df0 %>%  
#   mutate(len = nrow(.)) |> 
#   rowwise() |> 
#   mutate(card,
#          n,
#          total_desc_copies = 0L,
#          flag = list(c(rep(FALSE, card), rep(TRUE, n), rep(FALSE, len - n - card))),
#          .keep = "none") |>
#   ungroup() # |> 
#   # unnest_wider(flag, names_sep = "")
# 
# for (i in nrow(df2):1) {
#   df2$total_desc_copies[i] <- df2[df2$flag[i][[1]],] %T>%
#     print() |> 
#     summarize(total_desc_copies = sum(total_desc_copies, na.rm = TRUE) + n()) |> 
#     pull(total_desc_copies)
# }


