library(tidyverse)

input <- read_csv("day1/input.txt", col_names = c('line'))

digit_words <- c('one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine')

digit_df <- tibble(digit = as.character(1:9), word = digit_words)

translated <- input |> 
    rowwise() |> 
    mutate(digit_word = list(str_match_all(line, paste0("(?=(", str_c(digit_words, collapse = "|"), "))"))[[1]][, 2])) |> 
    mutate(first_word = ifelse(length(digit_word == 0), digit_word[1], NA_character_),
           last_word = ifelse(length(digit_word == 0), tail(digit_word, 1), NA_character_)) |> 
    left_join(digit_df, join_by(first_word == word)) |> 
    rename(first_repl = digit) |> 
    left_join(digit_df, join_by(last_word == word)) |> 
    rename(last_repl = digit) |> 
    mutate(line_forward = ifelse(is.na(first_word), line, str_replace_all(line, first_word, first_repl)),
           line_backward = ifelse(is.na(last_word), line, str_replace_all(line, last_word, last_repl)),
           digit1 = str_extract_all(line_forward, "\\d{1}"),
           digit1 = digit1[1],
           digit2 = str_extract_all(line_backward, "\\d{1}"),
           digit2 = tail(digit2, 1),
           combined = str_c(digit1, digit2) |> as.integer()) |>
    ungroup()

translated |> 
    summarize(total = sum(combined))
