package org.example;

import lombok.AllArgsConstructor;
import lombok.Getter;

@AllArgsConstructor
public enum Card {
    JOKER("J"),
    TWO("2"),
    THREE("3"),
    FOUR("4"),
    FIVE("5"),
    SIX("6"),
    SEVEN("7"),
    EIGHT("8"),
    NINE("9"),
    TEN("T"),
    QUEEN("Q"),
    KING("K"),
    ACE("A");

    @Getter
    private final String symbol;

    public static Card getBySymbol(String symbol) {
        for (Card card : Card.values()) {
            if (card.symbol.equals(symbol)) {
                return card;
            }
        }
        return null; // or throw an exception if symbol not found
    }
}
