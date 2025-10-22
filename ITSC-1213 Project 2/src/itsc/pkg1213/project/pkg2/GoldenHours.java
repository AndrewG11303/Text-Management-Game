package itsc.pkg1213.project.pkg2;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.Map;

/**
 * The GoldenHours class extends the Event class to represent a specific event type in the game.
 * This event boosts the resource production rate of all generators temporarily.
 */
public class GoldenHours extends Event {
    // Map to store the original production rates of the generators before the event's effect
    private Map<Generator, Integer> originalRates = new HashMap<>();

    /**
     * Constructor for GoldenHours event.
     */
    public GoldenHours() {
        super("GoldenHours"); // Call to the superclass constructor with the event name
    }

    /**
     * Boosts the resource production rate of all generators by 50%.
     * 
     * @param generators An ArrayList of Generator objects whose production rates are to be boosted.
     */
     public void boostResourceProduction(ArrayList<Generator> generators) {
        for (Generator generator : generators) {
            int currentRate = generator.getResourceProductionRate();
            originalRates.put(generator, currentRate); // Store original rate
            int boostedRate = currentRate + (currentRate * 50 / 100); // Increase by 50%
            generator.setResourceProductionRate(boostedRate);
        }
        setActive(true); // Set the event as active
    }

     /**
     * Resets the resource production rates of all generators to their original rates before the event.
     * 
     * @param generators An ArrayList of Generator objects whose production rates are to be reset.
     */
    public void resetResourceProduction(ArrayList<Generator> generators) {
        for (Generator generator : generators) {
            if (originalRates.containsKey(generator)) {
                generator.setResourceProductionRate(originalRates.get(generator));
            }
        }
        originalRates.clear(); // Clear the stored rates
    }
}
    