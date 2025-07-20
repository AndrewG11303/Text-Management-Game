/*
 * Click nbfs://nbhost/SystemFileSystem/Templates/Licenses/license-default.txt to change this license
 * Click nbfs://nbhost/SystemFileSystem/Templates/Classes/Class.java to edit this template
 */
package itsc.pkg1213.project.pkg2;

/**
 * The Resource class represents a generic resource in the game.
 * Resources have a name, a quantity, and a status of being critical or not.
 * It implements the Score and Comparable interfaces.
 */
public abstract class Resource implements Score, Comparable<Resource> {
    private String name;
    private int quantity;
    private boolean isCritical;

 /**
     * Constructor to create a new Resource.
     *
     * @param name The name of the resource.
     */
    public Resource(String name) {
        this.name = name;
        this.quantity = 0; // Quantity is initialized to 0
        this.isCritical = false; //By default, resources are not critical
    }

    /**
     * Gets the name of the resource.
     *
     * @return the name of the resource
     */
    public String getName() {
        return name;
    }

    /**
     * Gets the quantity of the resource.
     *
     * @return the quantity of the resource
     */
    public int getQuantity() {
        return quantity;
    }

    /**
     * Reports if a resource is critical. If a rsource is critical, reaching 0 ends the game.
     *
     * @return if the resource is critical
     */
    public boolean isCritical(){
        return isCritical;
    }

    public boolean isIsCritical() {
        return isCritical;
    }

    public void setName(String name) {
        this.name = name;
    }

    public void setQuantity(int quantity) {
        this.quantity = quantity;
    }

   /**
 * Reports if the resource is critical. Critical resources are essential for the game,
 * and depleting them may result in game over.
 *
 * @return A boolean value indicating if the resource is critical.
 */
    public void setIsCritical(boolean isCritical){
        this.isCritical = isCritical;
    }

    /**
     * Adds the specified amount to the quantity of the resource.
     *
     * @param amount the amount to add
     */
    public void add(int amount) {
    quantity += amount;
}

    /**
 * Consumes a specified amount of the resource. If the amount exceeds the available quantity,
 * the quantity is set to 0 and a message is displayed.
 *
 * @param amount The amount of the resource to consume.
 */
    public void consume(int amount) {
    if (quantity >= amount) {
        quantity -= amount;
    } else {
        quantity = 0;
        System.out.println("Not enough " + name + " to consume.");
    }
}
    /**
 * Compares this resource with another resource based on quantity.
 *
 * @param other Another resource to compare with.
 * @return A negative integer, zero, or a positive integer as this resource is less than,
 *         equal to, or greater than the specified resource.
 */
    @Override
    public int compareTo(Resource other) {
        return Integer.compare(this.quantity, other.quantity);
    }
    
    /**
 * Calculates the score impact of the resource, assuming the impact is its quantity.
 *
 * @return The quantity of the resource as its score impact.
 */
      @Override
    public int scoreImpact() {
        // Assuming the impact is the quantity for simplicity.
        return getQuantity();
    }
    
    /**
 * Provides a string representation of the resource including its name and quantity.
 *
 * @return A string representation of the resource.
 */
    @Override
    public String toString() {
        return name + ": Quantity = " + quantity;
    }
}