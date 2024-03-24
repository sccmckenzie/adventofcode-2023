package org.example;

import java.util.Comparator;

public class HandTypeComparator implements Comparator<Hand> {

    @Override
    public int compare(Hand hand1, Hand hand2) {
        HandType type1 = CardsUtils.getHandType(hand1);
        HandType type2 = CardsUtils.getHandType(hand2);

        int out = type1.compareTo(type2);

        if (out == 0) {
            for (int i = 0; i < 5; i++) {
                Card card1 = hand1.getCards().get(i);
                Card card2 = hand2.getCards().get(i);

                out = card1.compareTo(card2);
                if (out != 0) break;
            }
        }
        return out;
    }
}
