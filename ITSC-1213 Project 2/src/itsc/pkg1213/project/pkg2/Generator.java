/*
 * Click nbfs://nbhost/SystemFileSystem/Templates/Licenses/license-default.txt to change this license
 * Click nbfs://nbhost/SystemFileSystem/Templates/Classes/Class.java to edit this template
 */
package itsc.pkg1213.project.pkg2;

import java.util.ArrayList;

/**
 * The Generator class represents a generic resource generating item in the game.
 * It is an abstract class, meaning it cannot be instantiated on its own but rather serves as a base for specific types of generators.
 * Generators have properties like name, construction cost, production rate, and the type of resource they produce.
 */

public abstract class Generator implements Score, Comparable<Generator> {
    private String name;// Name of the generator
    private ArrayList<Resource> constructionCost; // List of resources required to construct the generator
    private int resourceProductionRate; // Rate at which the generator produces resources
    private int numberConstructed; // Number of this type of generator constructed
    private Resource product; // Type of resource this generator produces
    private GeneratorType type; // Types of generator

 /**
     * Constructor for creating a new Generator.
     * 
     * @param name                  The name of the Generator.
     * @param constructionCost      The cost in resources required to construct the Generator.
     * @param resourceProductionRate The rate at which the Generator produces resources per unit of time.
     * @param product               The type of resource this generator produces.
     * @param type                  The type of the generator, represented by the GeneratorType enum.
     */
    
      public Generator(String name, ArrayList<Resource> constructionCost, int resourceProductionRate, Resource product, GeneratorType type) {
        this.name = name;
        this.constructionCost = constructionCost;
        this.resourceProductionRate = resourceProductionRate;
        this.product = product;
        this.type = type;
        this.numberConstructed = 0; // Initializes with zero constructed generators
    }
    
     /**
     * Abstract method that must be implemented by subclasses to define how resources are produced.
     */
      
    public abstract void produceResources();
    
    @Override
    public int compareTo(Generator other) {
         // Compares generators based on their resource production rate
        return Integer.compare(this.resourceProductionRate, other.resourceProductionRate);
    }

    @Override
    public int scoreImpact() {
        // Example implementation of score impact calculation
        return getNumberConstructed() * getResourceProductionRate();
    }

    public void setName(String name) {
        this.name = name;
    }

    public void setConstructionCost(ArrayList<Resource> constructionCost) {
        this.constructionCost = constructionCost;
    }

    public void setResourceProductionRate(int resourceProductionRate) {
        this.resourceProductionRate = resourceProductionRate;
    }

    public void setNumberConstructed(int numberConstructed) {
        this.numberConstructed = numberConstructed;
    }

    public void setProduct(Resource product) {
        this.product = product;
    }
    

    /**
     * Gets the name of the Generator.
     *
     * @return the name of the Generator
     */
    public String getName() {
        return name;
    }

    /**
     * Gets the construction cost of the Generator.
     *
     * @return the construction cost of the Generator
     */
    public ArrayList<Resource> getConstructionCost() {
        return constructionCost;
    }

    public Resource getProduct() {
        return product;
    }

    /**
     * Gets the resource production rate of the Generator.
     *
     * @return the resource production rate of the Generator
     */
    public int getResourceProductionRate() {
        return resourceProductionRate;
    }

    /**
     * Gets the number of units constructed of this Generator.
     *
     * @return the number of units constructed of the generator
     */
    public int getNumberConstructed() {
        return numberConstructed;
    }
    
    public GeneratorType getType() {
        return type;
    }
    
    public void incrementNumberConstructed() {
        this.numberConstructed++;

}
}