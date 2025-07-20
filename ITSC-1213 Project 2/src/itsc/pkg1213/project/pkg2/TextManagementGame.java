/*
 * Click nbfs://nbhost/SystemFileSystem/Templates/Licenses/license-default.txt to change this license
 * Click nbfs://nbhost/SystemFileSystem/Templates/Classes/Main.java to edit this template
 */
package itsc.pkg1213.project.pkg2;

import java.util.Scanner;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Random;
import java.util.InputMismatchException;
import java.util.HashMap;
import java.util.Map;

/**
 *
 * @author Andrew
 */


/**
 * The TextManagementGame class represents a text-based resource management game.
 * Players can collect resources, manage generators, and attempt to maintain resource levels.
 */
public class TextManagementGame {
    
    
    
    // Constants for base collection amounts for various resources
    private static final int BASE_WOOD_COLLECT_AMOUNT = 5;
    private static final int BASE_STONE_COLLECT_AMOUNT = 3;
    private static final int BASE_IRON_COLLECT_AMOUNT = 1;
    private static final int BASE_FOOD_COLLECT_AMOUNT = 5;
    
    // Variable to keep track of the current round number
    private int round;
    
    // List to hold all resources available in the game
    private ArrayList<Resource> resources = new ArrayList();
    
    // List to hold all generators that produce resources
    private ArrayList<Generator> generators = new ArrayList();

    // Define a Scanner for user input
    private Scanner scanner;
    
    // Random object for generating random events
    private Random random = new Random();
    
    // GoldenHours event object to represent beneficial random events
    private final GoldenHours goldenHours = new GoldenHours();
    
    // SnowStorm event object to represent detrimental random events
    private final SnowStorm snowStorm  = new SnowStorm();

    /**
     * Creates a new TextManagementGame instance with initial resource and time values.
     * TODO : Add starting resources
     */
   public TextManagementGame() {
    round = 1;
    scanner = new Scanner(System.in);
    
    // Add initial resources with starting quantities
    addResource(new Wood(20, true));
    addResource(new Stone(15, true));
    addResource(new Iron(10, true));
    addResource(new Food(30, true));
    
    // Add initial generators with starting production rates
//    addGenerator(new LumberMill(new ArrayList<>(), 5));
//    addGenerator(new StoneMine(new ArrayList<>(), 5));
//    addGenerator(new IronMine(new ArrayList<>(), 5));
//    addGenerator(new Farm(new ArrayList<>(), 5));
}

    /**
     * Determines if a random event occurs this turn based on probability.
     * @param number the chance of the event occurring (1 in 'number' chance)
     * @return true if the event should occur, false otherwise
     */
    public boolean haveEventThisTurn(int number) {
        return random.nextInt(number) == 0; // Returns true with a 1 in number chance
    }

    /**
     * Displays all resources with their quantities.
     */
    public void viewResources(){
         sortResources();
        for(Resource r : resources){
            System.out.println(r);
        }
    }

   /**
     * Displays all generators with their details.
     */
    public void viewGenerators() {
    sortGenerators(); // Sort generators before displaying

    // Initialize a map with all generator types set to a count of 0
    Map<String, Integer> generatorCounts = new HashMap<>();
    generatorCounts.put("LumberMill", 0);
    generatorCounts.put("StoneMine", 0);
    generatorCounts.put("IronMine", 0);
    generatorCounts.put("Farm", 0);

    // Update the counts for each type of generator that has been constructed
    for (Generator g : generators) {
        String generatorType = g.getClass().getSimpleName();
        generatorCounts.put(generatorType, generatorCounts.get(generatorType) + g.getNumberConstructed());
    }

    // Now print the consolidated information
    for (String generatorType : generatorCounts.keySet()) {
        int count = generatorCounts.get(generatorType);
        System.out.println(generatorType + " - Number Constructed: " + count);
    }
}
    
    public void sortResources() {
        Collections.sort(resources);
        System.out.println("Resources sorted by quantity.");
        System.out.println(" ");
    }
    
    public void sortGenerators() {
        Collections.sort(generators);
        System.out.println("Generators sorted by production rate.");
        System.out.println(" ");
    }
    
    public void addResource(Resource resource) {
        resources.add(resource);
    }
    
   public void addGenerator(Generator newGenerator) {
    for (Generator existingGenerator : generators) {
        if (existingGenerator.getClass().equals(newGenerator.getClass())) {
            existingGenerator.incrementNumberConstructed();
            return;
        }
    }
    // If it doesn't exist, add as new
    newGenerator.incrementNumberConstructed(); // Assuming the new generator starts with 0
    generators.add(newGenerator);
}


    /**
     * Checks if a Generator can be constructed and then adds it to the list of Generators
     * TODO : ADD LOGIC
     */
   public void constructGenerator() {
    System.out.println("Available Generators:");
    System.out.println("1. Lumber Mill - Cost: 5 Wood, 5 Stone - Boost overall WOOD production rate");
    System.out.println("2. Stone Mine - Cost: 10 Wood, 10 Stone - Boost overall STONE production rate");
    System.out.println("3. Iron Mine - Cost: 15 Wood, 15 Stone - Boost overall IRON production rate");
    System.out.println("4. Farm - Cost: 20 Wood, 20 Stone, 20 Iron - Boost overall FOOD production rate");
    System.out.println("5 Exit - Return to the main menu");
    System.out.println("Choose a generator to build or exit: ");

    try {
        int generatorChoice = scanner.nextInt();
        Generator chosenGenerator = null;

        ArrayList<Resource> constructionCosts;

        switch (generatorChoice) {
            case 1: // Lumber Mill
                constructionCosts = new ArrayList<>();
                constructionCosts.add(new Wood(5, false));
                constructionCosts.add(new Stone(5, false));
                chosenGenerator = new LumberMill(constructionCosts, BASE_WOOD_COLLECT_AMOUNT);
                break;
            case 2: // Stone Mine
                constructionCosts = new ArrayList<>();
                constructionCosts.add(new Wood(10, false));
                constructionCosts.add(new Stone(10, false));
                chosenGenerator = new StoneMine(constructionCosts, BASE_STONE_COLLECT_AMOUNT);
                break;
            case 3: // Iron Mine
                constructionCosts = new ArrayList<>();
                constructionCosts.add(new Wood(15, false));
                constructionCosts.add(new Stone(15, false));
                chosenGenerator = new IronMine(constructionCosts, BASE_IRON_COLLECT_AMOUNT);
                break;
            case 4: // Farm
                constructionCosts = new ArrayList<>();
                constructionCosts.add(new Wood(20, false));
                constructionCosts.add(new Stone(20, false));
                constructionCosts.add(new Iron(20, false));
                chosenGenerator = new Farm(constructionCosts, BASE_FOOD_COLLECT_AMOUNT);
                break;
            case 5:
                System.out.println("Returning to the main menu...");
                return;
            default:
                System.out.println("Please pick a valid number from 1-4 for generators or 5 to exit.");
                return;
        }

        if (chosenGenerator != null && canBuildGenerator(chosenGenerator)) {
            buildGenerator(chosenGenerator);
        } else if (generatorChoice != 5) {
            System.out.println("Not enough resources to build " + (chosenGenerator != null ? chosenGenerator.getName() : "this generator") + ".");
        }
    } catch (InputMismatchException e) {
        scanner.nextLine();
        System.out.println("Invalid input, please enter a number from 1-4 for generators or 5 to exit.");
    }
}


  private boolean canBuildGenerator(Generator generator) {
    for (Resource cost : generator.getConstructionCost()) {
        Resource playerResource = getResourceByName(cost.getName());
        if (playerResource == null || playerResource.getQuantity() < cost.getQuantity()) {
            return false; // If any resource is insufficient, return false
        }
    }
    return true; // If all resources are sufficient, return true
}
  
public void buildGenerator(Generator newGenerator) {
    if (canBuildGenerator(newGenerator)) {
        for (Resource cost : newGenerator.getConstructionCost()) {
            Resource playerResource = getResourceByName(cost.getName());
            if (playerResource != null) {
                playerResource.consume(cost.getQuantity());
            }
        }
        
        boolean generatorFound = false;
        for (Generator existingGenerator : generators) {
            if (existingGenerator.getClass().equals(newGenerator.getClass())) {
                existingGenerator.incrementNumberConstructed(); // Increment the count
                generatorFound = true;
                System.out.println("Added another " + existingGenerator.getName() + ". Total constructed: " + existingGenerator.getNumberConstructed());
                break;
            }
        }

        if (!generatorFound) {
            newGenerator.incrementNumberConstructed(); // This will set the number constructed to 1
            generators.add(newGenerator); // Only add the new generator if it wasn't found
            System.out.println(newGenerator.getName() + " built!");
        }
       
    } else {
        System.out.println("Not enough resources to build " + newGenerator.getName() + ".");
    }
}





   private Resource getResourceByName(String resourceName) {
    for (Resource resource : resources) {
        if (resource.getName().equalsIgnoreCase(resourceName)) {
            return resource;
        }
    }
    return null;
} 
    
    /** 
     * Increments the time counter and then adds more resources based on what generators are present
     * TODO : Add calculations to generate resources for the next turn
     */
public void endRound() {
    for (Generator generator : generators) {
        Resource resource = getResourceByName(generator.getProduct().getName());
        if (resource != null) {
            // Adding base production rate plus production from generators
            int totalProduction = BASE_WOOD_COLLECT_AMOUNT + (5 * generator.getNumberConstructed());
            resource.add(totalProduction);
        }
    }
    System.out.println("Round " + round + " ended.");
    round++;
}

private void resetEventEffects() {
    if (snowStorm.isActive()) {
        snowStorm.resetResourceProduction(generators);
        snowStorm.setActive(false);
    } else if (goldenHours.isActive()) {
        goldenHours.resetResourceProduction(generators);
        goldenHours.setActive(false);
    }
}


    /**
     * Checks if we are out of any critical resources
     *
     * @return returns true if we are out of any critical resources returns false otherwise
    */
    public boolean isCriticalResourceDepleted(){
        for(Resource r : resources){
            if(r.isCritical() && r.getQuantity() <= 0){
                return true;
            }
        }
        return false;
    }

   public void collectResources() {
    
    // Determine if an event is triggered this turn.
    boolean eventTriggered = haveEventThisTurn(4);

    if (snowStorm.isActive()) {
        snowStorm.lowerResourceProduction(generators);
    } else if (goldenHours.isActive()) {
        goldenHours.boostResourceProduction(generators);
    }

    
    collectResource("Wood", BASE_WOOD_COLLECT_AMOUNT, "Lumber Mill");
    collectResource("Stone", BASE_STONE_COLLECT_AMOUNT, "Stone Mine");
    collectResource("Iron", BASE_IRON_COLLECT_AMOUNT, "Iron Mine");
    collectResource("Food", BASE_FOOD_COLLECT_AMOUNT, "Farm");
    
    if (!eventTriggered) {
        if (snowStorm.isActive()) {
            snowStorm.resetResourceProduction(generators);
            snowStorm.setActive(false);
            System.out.println("The Snow Storm has ended, resource production is back to normal.");
        }
        if (goldenHours.isActive()) {
            goldenHours.resetResourceProduction(generators);
            goldenHours.setActive(false);
            System.out.println("The Golden Hours have ended, resource production is back to normal.");
        }
    }
}
    
   private void collectResource(String resourceName, int baseAmount, String generatorName) {
    Resource resource = getResourceByName(resourceName);
    if (resource != null) {
        int additionalProduced = calculateAdditionalResources(generatorName);
        int totalProduced = baseAmount;

        // Apply any active event modifiers
        if (snowStorm.isActive()) {
            additionalProduced = (int) (additionalProduced * 0.75); // Decrease by 25% for SnowStorm
        } 
        if (goldenHours.isActive()) {
            additionalProduced = (int) (additionalProduced * 1.5); // Increase by 50% for GoldenHours
        }

        totalProduced += additionalProduced; // Add additional resources from generators considering events

        System.out.println("\nYour total " + resourceName.toLowerCase() + " before collecting anything: " + resource.getQuantity());
        resource.add(totalProduced);
        System.out.println("Base " + resourceName.toLowerCase() + " collected: " + baseAmount);
        System.out.println("Extra " + resourceName.toLowerCase() + " produced by generators: " + additionalProduced);
        System.out.println("Total " + resourceName.toLowerCase() + " collected this round: " + totalProduced);
        System.out.println("Your total " + resourceName.toLowerCase() + " after collecting resources: " + resource.getQuantity());
    }
}

    
    
     private void resetResourceProduction(ArrayList<Generator> generators) {
        snowStorm.resetResourceProduction(generators);
        goldenHours.resetResourceProduction(generators);
    }


    private int calculateAdditionalResources(String generatorName) {
    int additionalResources = 0;
    for (Generator generator : generators) {
        if (generator.getName().equalsIgnoreCase(generatorName)) {
            // The production rate is multiplied by the number of generators constructed
            additionalResources += 5 * generator.getNumberConstructed();
        }
    }
    return additionalResources;
}
    
    public void simulateRandomEvent() {
    int eventType = random.nextInt(2); // 0 for SnowStorm, 1 for GoldenHours

    if (eventType == 0 && !snowStorm.isActive()) {
        snowStorm.lowerResourceProduction(generators);
        snowStorm.setActive(true);
        System.out.println("A Snow Storm has started, resource production is decreased!");
    } else if (eventType == 1 && !goldenHours.isActive()) {
        goldenHours.boostResourceProduction(generators);
        goldenHours.setActive(true);
        System.out.println("Golden Hours have begun, resource production is increased!");
    }

}





    
    private int calculateTotalScore() {
        int score = 0;
        for(Resource resource : resources) {
            score += resource.scoreImpact();
        }
        for (Generator generator : generators) {
            score += generator.scoreImpact();
        }
        return score;
    }
    
    private int calculateScore() {
    int score = 0;
    // Calculate the score from resources
    for (Resource resource : resources) {
        score += resource.getQuantity(); // Assuming the score is the quantity for simplicity
    }
    // Calculate the score from generators
    for (Generator generator : generators) {
        score += generator.getNumberConstructed() * generator.getResourceProductionRate();
    }
    return score;
}
    
    private void displayScore() {
    int totalScore = calculateTotalScore();
    System.out.println("Your total score is: " + totalScore);
}
    /**
     * Starts the game and manages the game loop.
     */
    public void start() {
        System.out.println("Welcome to the Text Management Game!"); //TODO: Change Text

        // Main game loop
        while (!isCriticalResourceDepleted()) {
            System.out.println("\nRound " + round);
            if (haveEventThisTurn(4)) {
                //TODO add logic for random events
                simulateRandomEvent();
            }
            
            System.out.println("Options:");
            System.out.println("1. Collect resources");
            System.out.println("2. Manage resources");
            System.out.println("3. Add a new Generator");
            System.out.println("4. End round");
            System.out.println("5. Show score");
            System.out.println("6. Quit game");
            System.out.print("Choose an option: ");
            
            try {
            int choice = scanner.nextInt();

            switch (choice) {
                case 1:
                    collectResources();
                    break;
                case 2:
                    System.out.println("Generators:");
                    viewGenerators();
                    System.out.println("");
                    System.out.println("Resources:");
                    viewResources();
                    break;
                case 3: 
                    constructGenerator();
                    break;
                case 4:
                    endRound();
                    break;
                case 5: 
                    displayScore();
                    break;

                case 6:
                    System.out.println("Exiting the game...");
                    scanner.close();
                    return;
                default:
                    System.out.println("Please pick a valid number from 1-6!");
            }
        } catch (InputMismatchException e) {
                scanner.nextLine(); // Consume the invalid input
                System.out.println("Please pick a valid number from 1-6!");
            }
        }
        System.out.println("Game Over! You ran out of resources.");
        System.out.println("You played for " + round + " rounds.");
        scanner.close();
    }

    public int getRound() {
        return round;
    }

    public void setRound(int round) {
        this.round = round;
    }

    public ArrayList<Resource> getResources() {
        return resources;
    }

    public void setResources(ArrayList<Resource> resources) {
        this.resources = resources;
    }

    public ArrayList<Generator> getGenerators() {
        return generators;
    }

    public void setGenerators(ArrayList<Generator> generators) {
        this.generators = generators;
    }

    public Scanner getScanner() {
        return scanner;
    }

    public void setScanner(Scanner scanner) {
        this.scanner = scanner;
    }

    public Random getRandom() {
        return random;
    }

    public void setRandom(Random random) {
        this.random = random;
    }

    /**
     * Main method to run the game
     *
     * @param args the command-line arguments (not used in this game)
     */
    public static void main(String[] args) {
        TextManagementGame game = new TextManagementGame();
        game.start(); 
        }
    }
