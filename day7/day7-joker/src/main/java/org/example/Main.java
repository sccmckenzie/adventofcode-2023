package org.example;

import java.io.FileNotFoundException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class Main {
    public static void main(String[] args) throws FileNotFoundException {
        List<Hand> hands = CardsUtils.readHands("input.txt");

        hands.sort(new HandTypeComparator());

        int out = 0;

        for (int i = 0; i < hands.size(); i++) {
            out += hands.get(i).getBid() * (i + 1);
        }

//        List<Object> test = new ArrayList<>();
//
//        for (Hand hand : hands) {
//            Map<Hand, HandType> obj = new HashMap<>();
//            obj.put(hand, CardsUtils.getHandType(hand));
//            test.add(obj);
//        }
        System.out.println(out);
    }
}