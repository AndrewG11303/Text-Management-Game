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
 * The Iron class extends the Resource class to represent a specific type of resource in the game.
 * This class is for managing the iron resource, including its quantity and whether it is critical.
 */
public class Iron extends Resource{
    
    /**
     * Constructor for the Iron resource.
     * 
     * @param quantity    The initial quantity of iron available.
     * @param isCritical  Indicates whether running out of this resource ends the game. 
     *                    True if it is critical (game ends if depleted), false otherwise.
     */
    public Iron(int quantity, boolean isCritical) {
        super("Iron"); // Call to the superclass constructor with the resource name
        this.setQuantity(quantity); // Set the initial quantity of iron
        this.setIsCritical(isCritical); // Set whether iron is a critical resource
    }
    
}
