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
 * The Score interface defines a common behavior for objects in the game
 * that can impact the player's score. It's used to abstract the scoring
 * mechanism so that different game elements (like resources or generators)
 * can contribute to the score in their unique ways.
 */

public interface Score {
     /**
     * Calculates the impact of an object on the player's score.
     * Implementing classes will provide their specific logic to quantify
     * how they affect the score. This method should return an integer
     * representing the contribution or impact on the overall game score.
     * 
     * For example, a resource might return its quantity as its score impact,
     * while a generator might return a value based on its production rate
     * and the number of units constructed.
     *
     * @return An integer representing the score impact of the object.
     */
    int scoreImpact();
}
