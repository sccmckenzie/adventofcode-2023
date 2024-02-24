package org.sccmckenzie.aoc2023.day6;

import java.util.ArrayList;
import java.util.List;

import static java.lang.Math.max;

public class Race {
    private long raceTime; // milliseconds

    public Race(long raceTime) {
        this.raceTime = raceTime;
    }

    public long getDistanceTraveled(long chargeTime) {
        long distanceTraveled = (raceTime - chargeTime) * chargeTime;
        return max(distanceTraveled, 0);
    }

    public List<Long> getPossibleDistances() {
        List<Long> out = new ArrayList<Long>();
        long chargeTime = 1;
        long distanceTraveled = 0;

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
