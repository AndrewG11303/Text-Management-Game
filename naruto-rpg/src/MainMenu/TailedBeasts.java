package MainMenu;

import javafx.scene.image.Image;

public class TailedBeasts {
    private final String name;
    private final String description;
    private final Image image;

    public TailedBeasts(String name, String description, String imagePath) {
        this.name = name;
        this.description = description;
        
        // Try to load the image, use a default if not found
        Image loadedImage = null;
        try {
            loadedImage = new Image(getClass().getResourceAsStream(imagePath));
        } catch (Exception e) {
            System.out.println("Could not load image for " + name + " at path: " + imagePath);
            // You could load a default "no image" placeholder here if desired
        }
        this.image = loadedImage;
    }

    public String getName() { 
        return name; 
    }
    
    public String getDescription() { 
        return description; 
    }
    
    public Image getImage() { 
        return image; 
    }

    @Override
    public String toString() {
        return description; // This is what shows in the ComboBox
    }

    // Static method to create all tailed beasts
    public static TailedBeasts[] getAllTailedBeasts() {
        return new TailedBeasts[] {
            new TailedBeasts("Shukaku", "Shukaku – One‑Tail (Wind & Earth)", "/Assets/TailedBeasts/shukaku.png"),
            new TailedBeasts("Matabi", "Matabi – Two‑Tails (Fire)", "/Assets/TailedBeasts/matabi.png"),
            new TailedBeasts("Isobu", "Isobu – Three‑Tails (Water & Yin)", "/Assets/TailedBeasts/isobu.png"),
            new TailedBeasts("Son Goku", "Son Goku – Four‑Tails (Fire & Earth)", "/Assets/TailedBeasts/songoku.png"),
            new TailedBeasts("Kokuo", "Kokuo – Five‑Tails (Fire & Water)", "/Assets/TailedBeasts/kokuo.png"),
            new TailedBeasts("Saiken", "Saiken – Six‑Tails (Fire & Earth)", "/Assets/TailedBeasts/saiken.png"),
            new TailedBeasts("Chomei", "Chomei – Seven‑Tails (Wind & Bug)", "/Assets/TailedBeasts/chomei.png"),
            new TailedBeasts("Gyuki", "Gyuki – Eight‑Tails (Lightning)", "/Assets/TailedBeasts/gyuki.png"),
            new TailedBeasts("Kurama Yang", "Kurama (Yang) – Nine‑Tails (Fire, Wind & Yang)", "/Assets/TailedBeasts/kurama_yang.png"),
            new TailedBeasts("Kurama Yin", "Kurama (Yin)  – Nine‑Tails (Fire, Wind & Yin)", "/Assets/TailedBeasts/kurama_yin.png"),
            new TailedBeasts("Complete Kurama", "Complete Kurama (Locked) – Nine‑Tails (Fire, Wind, Yin & Yang)", "/Assets/TailedBeasts/kurama_complete.png")
        };
    }
}