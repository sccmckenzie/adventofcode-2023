package org.example;

import lombok.Getter;
import java.util.List;

public class Hand {

    @Getter
    private final List<Card> cards;

    @Getter
    private final int bid;

    @Getter
    private final HandType handType;

    public Hand(List<Card> cards, int bid) {
        this.cards = cards;
        this.bid = bid;
        this.handType = CardsUtils.calculateHandType(this);
    }

}
