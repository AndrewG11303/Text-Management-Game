/*
 * Click nbfs://nbhost/SystemFileSystem/Templates/Licenses/license-default.txt to change this license
 * Click nbfs://nbhost/SystemFileSystem/Templates/Classes/Class.java to edit this template
 */
package itsc.pkg1213.project.pkg2;
import java.util.ArrayList;

/**
 * The IronMine class extends the Generator class to represent a specific type of generator in the game.
 * This class is responsible for managing an iron mine, which generates iron resources.
 */
public class IronMine extends Generator {
    
    /**
     * Constructor for the IronMine generator.
     *
     * @param constructionCost       A list of resources required to construct the iron mine. 
     *                               Each resource in the list details the type and quantity needed.
     * @param resourceProductionRate The rate at which the iron mine produces iron per unit of time.
     *                               This determines the efficiency of the iron mine.
     */
    public IronMine(ArrayList<Resource> constructionCost, int resourceProductionRate) {
        super("Iron Mine", constructionCost, resourceProductionRate, new Iron(0,false), GeneratorType.IRON_MINE);
        // 'super' calls the constructor of the parent Generator class with specific parameters for an Iron Mine
        // 'new Iron(0, false)' creates a new Iron resource instance that this generator will produce
    }

    @Override
    public void produceResources() {
        // Specific logic for Iron Mine to produce resources
        // This method would contain the functionality of how the Iron Mine contributes to the game's resource pool
    }
}