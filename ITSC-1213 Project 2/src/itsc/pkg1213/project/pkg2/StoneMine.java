/*
 * Click nbfs://nbhost/SystemFileSystem/Templates/Licenses/license-default.txt to change this license
 * Click nbfs://nbhost/SystemFileSystem/Templates/Classes/Class.java to edit this template
 */
package itsc.pkg1213.project.pkg2;
import java.util.ArrayList;

/**
 * The StoneMine class represents a generator specifically for mining stone in the game.
 * It extends the abstract Generator class and specializes in stone production.
 */
public class StoneMine extends Generator {
    
    /**
     * Constructor for creating a new Stone Mine generator.
     *
     * @param constructionCost An ArrayList of Resource objects representing the resources required to construct this Stone Mine.
     * @param resourceProductionRate The rate at which the Stone Mine produces stone per unit of time.
     */
   public StoneMine(ArrayList<Resource> constructionCost, int resourceProductionRate) {
        // Call the constructor of the superclass (Generator) with specific parameters for Stone Mine.
        super("Stone Mine", constructionCost, resourceProductionRate, new Stone(0, false), GeneratorType.STONE_MINE);
    }

    /**
     * An abstract method from the Generator class. 
     * This method should contain the specific logic for how the Stone Mine produces resources (stone) in the game.
     * Currently, it is not implemented and can be customized based on game logic.
     */
    @Override
    public void produceResources() {
    }
}