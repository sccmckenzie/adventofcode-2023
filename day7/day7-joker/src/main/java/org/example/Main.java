package org.example;

import java.io.FileNotFoundException;
import java.util.*;

public class Main {
    public static void main(String[] args) throws FileNotFoundException {
        List<Hand> hands = CardsUtils.readHands("input.txt");

        hands.sort(new HandTypeComparator());

        int out = 0;

        for (int i = 0; i < hands.size(); i++) {
            out += hands.get(i).getBid() * (i + 1);
        }

        System.out.println(out);
    }
}