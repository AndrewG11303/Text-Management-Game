/*
 * Click nbfs://nbhost/SystemFileSystem/Templates/Licenses/license-default.txt to change this license
 * Click nbfs://nbhost/SystemFileSystem/Templates/Classes/Class.java to edit this template
 */
// Define the package for the class
package itsc.pkg1213.project.pkg2;
import java.util.ArrayList;

/**
 * The LumberMill class extends the Generator class to represent a specific type of resource generator in the game.
 * This class is responsible for managing a lumber mill, which generates wood resources.
 */
public class LumberMill extends Generator {
    /**
     * Constructor for the LumberMill generator.
     *
     * @param constructionCost       A list of resources required to construct the lumber mill.
     *                               Each resource in the list details the type and quantity needed.
     * @param resourceProductionRate The rate at which the lumber mill produces wood per unit of time.
     *                               This determines the efficiency of the lumber mill.
     */
    public LumberMill(ArrayList<Resource> constructionCost, int resourceProductionRate) {
        super("Lumber Mill", constructionCost, resourceProductionRate, new Wood(0, false), GeneratorType.LUMBER_MILL);
        // 'super' calls the constructor of the parent Generator class with specific parameters for a Lumber Mill
        // 'new Wood(0, false)' creates a new Wood resource instance that this generator will produce
        // The quantity is initialized to 0 and not critical by default, but this can be changed as necessary
    }
    
    @Override
    public void produceResources() {
        // Implement production logic specific to Lumber Mill if necessary
        // This method would contain the functionality of how the Lumber Mill contributes to the game's wood resource pool
    }
}
