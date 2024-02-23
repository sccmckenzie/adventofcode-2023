package org.sccmckenzie.aoc2023.day6;

import java.util.ArrayList;
import java.util.List;

import static java.lang.Math.max;

public class Race {
    private int raceTime; // milliseconds

    public Race(int raceTime) {
        this.raceTime = raceTime;
    }

    public int getDistanceTraveled(int chargeTime) {
        int distanceTraveled = (raceTime - chargeTime) * chargeTime;
        return max(distanceTraveled, 0);
    }

    public List<Integer> getPossibleDistances() {
        List<Integer> out = new ArrayList<Integer>();
        int chargeTime = 1;
        int distanceTraveled = 0;

        while (true) {
            distanceTraveled = getDistanceTraveled(chargeTime);
            if (distanceTraveled == 0) {
                break;
            }
            out.add(distanceTraveled);
            chargeTime++;
        }

        return out;
    }
}
