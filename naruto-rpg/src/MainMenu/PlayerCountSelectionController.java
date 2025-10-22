package MainMenu;

import javafx.fxml.FXML;
import javafx.fxml.FXMLLoader;
import javafx.fxml.Initializable;
import javafx.scene.Parent;
import javafx.scene.control.Button;
import javafx.scene.control.ComboBox;
import javafx.scene.layout.VBox;

import java.io.IOException;
import java.net.URL;
import java.util.ResourceBundle;

public class PlayerCountSelectionController implements Initializable {
    @FXML private VBox rootPane;
    @FXML private ComboBox<Integer> playerCountBox;
    @FXML private Button confirmButton;
    @FXML private Button backButton;

    @Override
    public void initialize(URL loc, ResourceBundle rb) {
        for (int i = 2; i <= 10; i++)
            playerCountBox.getItems().add(i);
        playerCountBox.setValue(2);

        confirmButton.setOnAction(e -> {
            int count = playerCountBox.getValue();
            try {
                FXMLLoader loader = new FXMLLoader(
                        getClass().getResource("/MainMenu/CharacterCreation.fxml")
                );
                Parent root = loader.load();
                CharacterCreationController ctrl = loader.getController();
                ctrl.startCreation(count);
                rootPane.getScene().setRoot(root);
            } catch (IOException ex) {
                ex.printStackTrace();
            }
        });

        backButton.setOnAction(e -> {
            try {
                Parent mode = FXMLLoader.load(
                        getClass().getResource("/MainMenu/ModeSelection.fxml")
                );
                rootPane.getScene().setRoot(mode);
            } catch (IOException ex) {
                ex.printStackTrace();
            }
        });
    }
}