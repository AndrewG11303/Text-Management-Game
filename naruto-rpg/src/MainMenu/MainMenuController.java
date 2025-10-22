package MainMenu;

import javafx.fxml.FXML;
import javafx.fxml.FXMLLoader;
import javafx.fxml.Initializable;
import javafx.scene.Parent;
import javafx.scene.control.Button;
import javafx.scene.image.Image;
import javafx.scene.image.ImageView;
import javafx.scene.layout.AnchorPane;

import java.io.IOException;
import java.net.URL;
import java.util.ResourceBundle;

public class MainMenuController implements Initializable {
    @FXML private AnchorPane rootPane;
    @FXML private ImageView  backgroundImage;
    @FXML private Button     playButton;

    @Override
    public void initialize(URL loc, ResourceBundle rb) {
        try {
            Image img = new Image(
                    getClass().getResource("/Assets/0710c65c16a3be8d29ba94af0a3b1460.jpg")
                            .toExternalForm()
            );
            backgroundImage.setImage(img);
        } catch (Exception e) {
            System.out.println("Could not load background image");
        }
        
        backgroundImage.fitWidthProperty().bind(rootPane.widthProperty());
        backgroundImage.fitHeightProperty().bind(rootPane.heightProperty());

        playButton.setOnAction(e -> {
            try {
                Parent modeRoot = FXMLLoader.load(
                        getClass().getResource("/MainMenu/ModeSelection.fxml")
                );
                rootPane.getScene().setRoot(modeRoot);
            } catch (IOException ex) {
                ex.printStackTrace();
            }
        });
    }
}