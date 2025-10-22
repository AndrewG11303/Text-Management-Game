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
 * The Stone class represents the stone resource in the game.
 * It extends the Resource class, providing specific properties for stone.
 */

public class Stone extends Resource {
      /**
     * Constructor for creating a Stone resource instance.
     *
     * @param quantity   The initial quantity of the stone resource.
     * @param isCritical A boolean indicating if this resource is critical for game progress.
     *                   If a critical resource's quantity drops to 0, it may trigger game-over conditions.
     */
    public Stone(int quantity, boolean isCritical) {
        super("Stone"); // Initialize the parent class (Resource) with the name "Stone"
        this.setQuantity(quantity); // Set the initial quantity of the stone resource
        this.setIsCritical(isCritical); // Set whether the stone is a critical resource
    }
    
}
