package MainMenu;

import javafx.fxml.FXML;
import javafx.fxml.FXMLLoader;
import javafx.fxml.Initializable;
import javafx.scene.Parent;
import javafx.scene.control.*;
import javafx.scene.layout.HBox;
import javafx.scene.layout.VBox;
import javafx.geometry.Insets;
import javafx.geometry.Pos;
import javafx.scene.layout.Priority;

import java.io.IOException;
import java.net.URL;
import java.util.*;
import java.util.stream.Collectors;

public class CharacterCreationController implements Initializable {
    // —— injected from FXML ——
    @FXML private HBox              rootPane;
    @FXML private VBox              summaryPane;
    @FXML private ListView<String>  summaryList;

    @FXML private Label             headerLabel;
    @FXML private ComboBox<String>  nameField;
    @FXML private ComboBox<Integer> chakraCountBox;
    @FXML private VBox              chakraTypesContainer;
    @FXML private RadioButton       jinchYes, jinchNo;
    @FXML private ComboBox<String>  jinchurikiBox;
    @FXML private Button            confirmButton, backButton;

    // —— internal state ——
    private ToggleGroup                   jinchGroup;
    private int                           totalPlayers  = 1;
    private int                           currentPlayer = 1;
    private final List<Player>           createdPlayers = new ArrayList<>();
    private final List<ComboBox<String>> chakraSelectors = new ArrayList<>();
    private VBox                         formPane; // reference to form container

    private static final List<String> ALL_NATURES = List.of(
            "Fire", "Water", "Earth", "Wind", "Lightning"
    );
    private static final List<String> ALL_BEASTS = List.of(
            "Shukaku – One‑Tail (Wind & Earth)",
            "Matabi – Two‑Tails (Fire)",
            "Isobu – Three‑Tails (Water & Yin)",
            "Son Goku – Four‑Tails (Fire & Earth)",
            "Kokuo – Five‑Tails (Fire & Water)",
            "Saiken – Six‑Tails (Fire & Earth)",
            "Chomei – Seven‑Tails (Wind & Bug)",
            "Gyuki – Eight‑Tails (Lightning)",
            "Kurama (Yang) – Nine‑Tails (Fire, Wind & Yang)",
            "Kurama (Yin)  – Nine‑Tails (Fire, Wind & Yin)",
            "Complete Kurama (Locked) – Nine‑Tails (Fire, Wind, Yin & Yang)"
    );

    @Override
    public void initialize(URL loc, ResourceBundle rb) {
        // hide the summary list by default (single‑player mode)
        summaryPane.setVisible(false);
        summaryPane.setManaged(false);

        // build "1…5" chakra‑count list
        for (int i = 1; i <= 5; i++) {
            chakraCountBox.getItems().add(i);
        }
        chakraCountBox.setValue(1);
        chakraCountBox.valueProperty().addListener((o,oldV,newV) ->
                rebuildChakraTypeSelectors(newV)
        );
        rebuildChakraTypeSelectors(1);

        // Jinchūriki yes/no toggles
        jinchGroup = new ToggleGroup();
        jinchYes.setToggleGroup(jinchGroup);
        jinchNo.setToggleGroup(jinchGroup);
        // full beast list initially
        jinchurikiBox.getItems().setAll(ALL_BEASTS);
        jinchurikiBox.setVisible(false);
        jinchurikiBox.setManaged(false);
        jinchGroup.selectedToggleProperty().addListener((o,oldT,newT) -> {
            boolean show = (newT == jinchYes);
            jinchurikiBox.setVisible(show);
            jinchurikiBox.setManaged(show);
        });

        // center the header label
        headerLabel.setAlignment(Pos.CENTER);
        headerLabel.setMaxWidth(Double.MAX_VALUE);
        VBox.setVgrow(headerLabel, Priority.NEVER);

        // Make summary list text larger
        summaryList.setStyle("-fx-font-size: 20px;");

        // button handlers
        confirmButton.setOnAction(e -> handleConfirm());
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

    /** rebuilds the N chakra‐nature dropdowns */
    private void rebuildChakraTypeSelectors(int count) {
        chakraSelectors.clear();
        chakraTypesContainer.getChildren().clear();

        for (int i = 1; i <= count; i++) {
            ComboBox<String> cb = new ComboBox<>();
            cb.setPrefWidth(200);  // tighter width
            cb.setPrefHeight(40);
            cb.setStyle("-fx-font-size: 20px;");
            cb.setPromptText("Nature " + i);
            cb.getItems().setAll(ALL_NATURES);
            cb.valueProperty().addListener((o,oldV,newV) ->
                    refreshNatureOptions()
            );
            chakraSelectors.add(cb);
            chakraTypesContainer.getChildren().add(cb);
        }

        refreshNatureOptions();
    }

    /** prevents duplicate natures across dropdowns */
    private void refreshNatureOptions() {
        List<String> chosen = chakraSelectors.stream()
                .map(ComboBox::getValue)
                .filter(Objects::nonNull)
                .collect(Collectors.toList());

        for (ComboBox<String> cb : chakraSelectors) {
            String me = cb.getValue();
            List<String> allowed = ALL_NATURES.stream()
                    .filter(n -> n.equals(me) || !chosen.contains(n))
                    .collect(Collectors.toList());
            cb.getItems().setAll(allowed);
            if (me != null && allowed.contains(me)) {
                cb.setValue(me);
            } else {
                cb.setValue(null);
            }
        }
    }

    /** Confirm: record player, advance or finish */
    private void handleConfirm() {
        String name = nameField.getEditor().getText().trim();
        List<String> natures = chakraSelectors.stream()
                .map(ComboBox::getValue).toList();
        boolean isJinch = jinchYes.isSelected();
        String beast = isJinch ? jinchurikiBox.getValue() : "None";

        // multiplayer flow
        if (totalPlayers > 1) {
            if (currentPlayer == 1) {
                summaryPane.setVisible(true);
                summaryPane.setManaged(true);
            }

            createdPlayers.add(new Player(name, natures, beast));
            summaryList.getItems().add(
                    String.format("P%d: %s | %s | %s",
                            currentPlayer, name, natures, beast)
            );

            // filter out used beasts
            Set<String> used = createdPlayers.stream()
                    .map(p -> p.bested)
                    .collect(Collectors.toSet());
            var allowed = ALL_BEASTS.stream()
                    .filter(b -> !used.contains(b))
                    .collect(Collectors.toList());
            jinchurikiBox.getItems().setAll(allowed);
            if (!allowed.contains(beast)) {
                jinchurikiBox.setValue(null);
            }
        }

        // advance or finish
        if (currentPlayer < totalPlayers) {
            currentPlayer++;
            headerLabel.setText("Create Player " + currentPlayer);
            nameField.getEditor().clear();
            chakraCountBox.setValue(1);
            jinchGroup.selectToggle(null);
            jinchurikiBox.setValue(null);
        } else {
            // All players created - disable the form and show completion message
            disableFormAfterCompletion();
            System.out.println("All players created—launch your game!");
            // TODO: swap to your actual game scene
        }
    }

    /** Disables the form after all players have been created */
    private void disableFormAfterCompletion() {
        headerLabel.setText("All Players Created!");
        headerLabel.setStyle("-fx-font-size: 48px; -fx-text-fill: green;");
        
        // Disable all form controls
        nameField.setDisable(true);
        chakraCountBox.setDisable(true);
        for (ComboBox<String> cb : chakraSelectors) {
            cb.setDisable(true);
        }
        jinchYes.setDisable(true);
        jinchNo.setDisable(true);
        jinchurikiBox.setDisable(true);
        confirmButton.setDisable(true);
        
        // Change confirm button text to indicate completion
        confirmButton.setText("Completed");
        confirmButton.setStyle("-fx-font-size: 20px; -fx-background-color: lightgray;");
    }

    /**
     * Kick off single vs. multiplayer layouts.
     * In multiplayer we show the summary left, in single we center the form.
     */
    public void startCreation(int total) {
        this.totalPlayers  = total;
        this.currentPlayer = 1;
        headerLabel.setText("Create Player 1");

        // Reset state for new creation session
        createdPlayers.clear();
        summaryList.getItems().clear();
        
        // Re-enable form controls in case this is a restart
        nameField.setDisable(false);
        chakraCountBox.setDisable(false);
        for (ComboBox<String> cb : chakraSelectors) {
            cb.setDisable(false);
        }
        jinchYes.setDisable(false);
        jinchNo.setDisable(false);
        jinchurikiBox.setDisable(false);
        confirmButton.setDisable(false);
        confirmButton.setText("Confirm");
        confirmButton.setStyle("-fx-font-size: 20px;");
        headerLabel.setStyle("-fx-font-size: 48px;");

        if (total > 1) {
            summaryPane.setVisible(true);
            summaryPane.setManaged(true);
            rootPane.setSpacing(150);
            rootPane.setPadding(new Insets(20,50,20,20));
            rootPane.setAlignment(Pos.TOP_LEFT);
        } else {
            summaryPane.setVisible(false);
            summaryPane.setManaged(false);
            rootPane.setSpacing(0);
            rootPane.setPadding(Insets.EMPTY);
            rootPane.setAlignment(Pos.CENTER);
        }
    }

    private static class Player {
        final String name;
        final List<String> natures;
        final String bested;
        Player(String name, List<String> natures, String beast) {
            this.name    = name;
            this.natures = new ArrayList<>(natures);
            this.bested  = beast;
        }
    }
}