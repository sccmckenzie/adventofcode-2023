package org.sccmckenzie.aoc2023.day6;


import java.io.FileNotFoundException;
import java.util.ArrayList;
import java.util.List;

public class Main {
    public static void main(String[] args) throws FileNotFoundException {
        // part 1
        List<RaceRecord> raceRecords = RaceUtils.readRaceRecords("input.txt");

        List<Integer> recordSetters = new ArrayList<>();

        for (RaceRecord raceRecord : raceRecords) {
            Race race = new Race(raceRecord.getTime());
            int numRecordSetters = 0;
            for (Long distance : race.getPossibleDistances()) {
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

        // part 2
        RaceRecord bigRaceRecord = RaceUtils.readRaceRecordSquished("input.txt");

        Race bigRace = new Race(bigRaceRecord.getTime());
        long numBigRecordSetters = 0;
        for (Long distance : bigRace.getPossibleDistances()) {
            if (distance > bigRaceRecord.getDistance()) {
                numBigRecordSetters++;
            }
        }

        System.out.println(numBigRecordSetters);

    }
}