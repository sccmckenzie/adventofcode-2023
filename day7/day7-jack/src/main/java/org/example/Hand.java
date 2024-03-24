package org.example;

import lombok.AllArgsConstructor;
import lombok.Getter;

import java.util.List;

@AllArgsConstructor
public class Hand {

    @Getter
    private List<Card> cards;

    @Getter
    private int bid;

}
