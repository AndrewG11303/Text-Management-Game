package MainMenu;

import javafx.fxml.FXML;
import javafx.fxml.FXMLLoader;
import javafx.fxml.Initializable;
import javafx.scene.Parent;
import javafx.scene.control.Button;
import javafx.scene.layout.VBox;

import java.io.IOException;
import java.net.URL;
import java.util.ResourceBundle;

public class ModeSelectionController implements Initializable {
    @FXML private VBox   rootPane;
    @FXML private Button singlePlayerButton;
    @FXML private Button multiplayerButton;
    @FXML private Button backButton;

    @Override
    public void initialize(URL loc, ResourceBundle rb) {
        singlePlayerButton.setOnAction(e -> {
            try {
                FXMLLoader loader = new FXMLLoader(
                        getClass().getResource("/MainMenu/CharacterCreation.fxml")
                );
                Parent charRoot = loader.load();
                CharacterCreationController ctrl = loader.getController();
                ctrl.startCreation(1);
                rootPane.getScene().setRoot(charRoot);
            } catch (IOException ex) {
                ex.printStackTrace();
            }
        });

        multiplayerButton.setOnAction(e -> {
            try {
                Parent pcRoot = FXMLLoader.load(
                        getClass().getResource("/MainMenu/PlayerCountSelection.fxml")
                );
                rootPane.getScene().setRoot(pcRoot);
            } catch (IOException ex) {
                ex.printStackTrace();
            }
        });

        backButton.setOnAction(e -> {
            try {
                Parent mainRoot = FXMLLoader.load(
                        getClass().getResource("/MainMenu/MainMenu.fxml")
                );
                rootPane.getScene().setRoot(mainRoot);
            } catch (IOException ex) {
                ex.printStackTrace();
            }
        });
    }
}