package org.example;

import java.io.FileNotFoundException;
import java.io.FileReader;
import java.util.*;

public class CardsUtils {
    public static List<Hand> readHands(String fileName) throws FileNotFoundException {
        Scanner in = new Scanner(new FileReader(fileName));
        List<Hand> out = new ArrayList<>();
        while (in.hasNext()) {
            String lineRaw = in.nextLine();

            List<String> handRaw = Arrays.asList(lineRaw.substring(0, 5).split(""));

            List<Card> cards = handRaw.stream()
                    .map(Card::getBySymbol)
                    .toList();

            int bid = Integer.parseInt(lineRaw.substring(6, lineRaw.length()));

            out.add(new Hand(cards, bid));
        }

        return out;
    }

    private static Map<Card, Integer> getHandAgg(Hand hand)  {
        List<Card> cards = hand.getCards();

        Map<Card, Integer> out = new HashMap<>();
        for (Card card : cards) {
            out.put(card, out.getOrDefault(card, 0) + 1);
        }

        return out;
    }

    public static HandType getHandType(Hand hand) {
        Map<Card, Integer> handAgg = getHandAgg(hand);

        int maxValue = handAgg.values().stream()
                .mapToInt(Integer::intValue)
                .max()
                .orElse(Integer.MIN_VALUE);

        if (maxValue == 5) {
            return HandType.FIVEKIND;
        } else if (maxValue == 4) {
            return HandType.FOURKIND;
        } else if (maxValue == 3) {
            boolean fullHouse = handAgg.values().stream()
                    .anyMatch(num -> num == 2);

            if (fullHouse) {
                return HandType.FULLHOUSE;
            } else {
                return HandType.THREEKIND;
            }
        } else if (maxValue == 2) {
            long numPairs = handAgg.values().stream()
                    .filter(num -> num == 2)
                    .count();

            if (numPairs == 2) {
                return HandType.TWOPAIR;
            } else {
                return HandType.ONEPAIR;
            }
        } else {
            return HandType.HIGHCARD;
        }
    }

}
