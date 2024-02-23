package org.sccmckenzie.aoc2023.day6;


import java.io.FileNotFoundException;
import java.util.ArrayList;
import java.util.List;

public class Main {
    public static void main(String[] args) throws FileNotFoundException {
        List<RaceRecord> raceRecords = RaceUtils.readRaceRecords("input.txt");

        List<Integer> recordSetters = new ArrayList<>();

        for (RaceRecord raceRecord : raceRecords) {
            Race race = new Race(raceRecord.getTime());
            int numRecordSetters = 0;
            for (Integer distance : race.getPossibleDistances()) {
                if (distance > raceRecord.getDistance()) {
                    numRecordSetters++;
                }
            }
            recordSetters.add(numRecordSetters);
        }

        Integer out = 1;
        for (Integer element : recordSetters) {
            out = Math.multiplyExact(element, out);
        }

        System.out.println(out);


    }
}