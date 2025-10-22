/*
 * Click nbfs://nbhost/SystemFileSystem/Templates/Licenses/license-default.txt to change this license
 * Click nbfs://nbhost/SystemFileSystem/Templates/Classes/Class.java to edit this template
 */
package itsc.pkg1213.project.pkg2;

/**
 * The Event class represents a generic event that can occur randomly in the game.
 * Each event has a name and an active status.
 */
public class Event implements Score {
    //Varaiable to hold the name of the event
    private String name;
    // Boolean flag to indicate whether the event is currently active
    private boolean active = false;

    /**
     * Constructor for creating a new Event.
     * 
     * @param name The name of the event. This name is used to identify the event.
     */
    public Event(String name) {
        this.name = name;
    }

    /**
     * Gets the name of the event.
     *
     * @return the name of the event
     */
    public String getName() {
        return name;
    }
    
     /**
     * Checks if the event is currently active.
     * 
     * @return true if the event is active, false otherwise.
     */
    public boolean isActive() {
        return active;
    }
    
    /**
     * Sets the active status of the event.
     * 
     * @param active A boolean value indicating the new active status of the event.
     */
    public void setActive(boolean active) {
        this.active = active;
    }
    
    /**
     * Provides the impact of the event on the game's score.
     * This is an implementation of the scoreImpact method from the Score interface.
     * 
     * @return An integer representing the impact of this event on the game's score.
     *         For a generic event, this impact is 0.
     */
    @Override
    public int scoreImpact() {
        return 0;
    }

}
