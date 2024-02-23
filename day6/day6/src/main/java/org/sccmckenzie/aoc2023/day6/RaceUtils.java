package org.sccmckenzie.aoc2023.day6;

import java.io.FileNotFoundException;
import java.io.FileReader;
import java.util.*;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

public class RaceUtils {
    public static List<RaceRecord> readRaceRecords(String fileName) throws FileNotFoundException {
        List<RaceRecord> out = new ArrayList<>();

        Scanner in = new Scanner(new FileReader(fileName));
        String timeRaw = in.nextLine();
        String distanceRaw = in.nextLine();

        Pattern pattern = Pattern.compile("\\b\\d+\\b");
        Matcher timeMatcher = pattern.matcher(timeRaw);
        Matcher distanceMatcher = pattern.matcher(distanceRaw);

        while (timeMatcher.find()) {
            if (!distanceMatcher.find()) {
                throw new InputMismatchException("Please check input file - number of time values not matching distance");
            }

            RaceRecord raceRecord = new RaceRecord(Integer.parseInt(timeMatcher.group()),
                    Integer.parseInt(distanceMatcher.group()));

            out.add(raceRecord);
        }

        return out;
    }
}
