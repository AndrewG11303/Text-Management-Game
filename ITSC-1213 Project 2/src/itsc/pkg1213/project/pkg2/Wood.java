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
 * The Wood class represents a type of resource in the game.
 * This class extends the abstract Resource class, specifically for managing wood as a resource.
 */
public class Wood extends Resource{
    
    /**
     * Constructor for creating a new Wood resource.
     *
     * @param quantity The initial quantity of wood available.
     * @param isCritical A boolean indicating whether wood is a critical resource, 
     *                   where running out of it may affect game progression or outcomes.
     */
    public Wood(int quantity, boolean isCritical) {
        // Call the constructor of the superclass (Resource) with the name "Wood"
        super("Wood");
        // Set the initial quantity of wood
        this.setQuantity(quantity);
        // Set whether wood is critical resource
        this.setIsCritical(isCritical);
    }
}
