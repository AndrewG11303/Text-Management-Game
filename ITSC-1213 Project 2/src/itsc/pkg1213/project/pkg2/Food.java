/*
 * Click nbfs://nbhost/SystemFileSystem/Templates/Licenses/license-default.txt to change this license
 * Click nbfs://nbhost/SystemFileSystem/Templates/Classes/Class.java to edit this template
 */
package itsc.pkg1213.project.pkg2;

/**
 *
 * @author Andrew
 */

/**
 * The Food class extends the Resource class and represents the food resource in the game.
 * It specializes the Resource class to represent a food resource with its specific properties.
 */
public class Food extends Resource {
    
    /**
     * Constructor for creating a new Food resource.
     * 
     * @param quantity An integer representing the initial quantity of the food resource.
     * @param isCritical A boolean indicating whether the food resource is critical for the game.
     *                   If a critical resource reaches zero, it might affect the game's outcome (e.g., ending the game).
     */
    
    public Food(int quantity, boolean isCritical) {
        
        // Calls the constructor of the parent Resource class with the name "Food"
        super("Food");
        
        // Sets the initial quantity of the food resource
        this.setQuantity(quantity);
        
        // Sets whether the food resource is critical for the game's mechanics
        this.setIsCritical(isCritical);
    }
    
}
