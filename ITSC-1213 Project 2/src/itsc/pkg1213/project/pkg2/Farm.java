/*
 * Click nbfs://nbhost/SystemFileSystem/Templates/Licenses/license-default.txt to change this license
 * Click nbfs://nbhost/SystemFileSystem/Templates/Classes/Class.java to edit this template
 */
package itsc.pkg1213.project.pkg2;
import java.util.ArrayList;

/**
 * The Farm class represents a specific type of Generator in the game, specifically for producing food.
 * It extends the abstract Generator class, inheriting its properties and methods.
 */
public class Farm extends Generator {
    
     /**
     * Constructor for creating a new Farm generator.
     * 
     * @param constructionCost An ArrayList of Resource objects representing the resources required to construct the Farm.
     * @param resourceProductionRate An integer representing the rate at which the Farm produces resources (Food) per unit of time.
     */
    public Farm(ArrayList<Resource> constructionCost, int resourceProductionRate) {
        super("Farm", constructionCost, resourceProductionRate, new Food(0,false), GeneratorType.FARM);
    }

     /**
     * Method to produce resources specific to the Farm.
     * This method is an implementation of the abstract method from the Generator class.
     * The actual logic of resource production for the Farm should be implemented here.
     */
    @Override
    public void produceResources() {
    }
}