package itsc.pkg1213.project.pkg2;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.Map;

/**
 * The SnowStorm class represents an event in the game that temporarily 
 * decreases the production rate of resources by generators. It extends
 * the Event class and affects all generators in the game.
 */
public class SnowStorm extends Event {
    // A map to store the original production rates of each generator
    private Map<Generator, Integer> originalRates = new HashMap<>();
    
    /**
     * Constructor for SnowStorm event. It initializes the event with the name "SnowStorm".
     */
    public SnowStorm() {
        super("SnowStorm");
    }

     /**
     * Temporarily lowers the resource production rates of all generators.
     * This method reduces each generator's production rate by 25% and stores
     * the original rates so they can be restored later.
     *
     * @param generators An ArrayList of Generator objects whose production rates
     *                   are to be temporarily lowered.
     */
   public void lowerResourceProduction(ArrayList<Generator> generators) {
        for (Generator generator : generators) {
            int currentRate = generator.getResourceProductionRate();
            originalRates.put(generator, currentRate); // Store original rate
            int loweredRate = currentRate - (currentRate * 25 / 100); // Decrease by 25%
            generator.setResourceProductionRate(loweredRate);
        }
        setActive(true); // Set the event as active
    }
    
    /**
     * Restores the resource production rates of all generators to their original values.
     * This method is typically called after the SnowStorm event ends to revert
     * the changes made by the lowerResourceProduction method.
     *
     * @param generators An ArrayList of Generator objects whose production rates
     *                   are to be restored to their original values.
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