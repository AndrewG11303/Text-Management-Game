# Naruto RPG Game - Code Analysis

## Overview
This is a JavaFX-based 2D Naruto RPG game inspired by "Path of a Ninja". The current implementation focuses on the main menu system and character creation workflow.

## Application Structure

### 1. Main Entry Point (`Main.java`)
- **Purpose**: Application launcher
- **Key Features**:
  - Extends JavaFX `Application`
  - Loads the main menu FXML
  - Sets up a maximized window with title "Naruto RPG"
  - Initial scene size: 900x600 (but maximized)

### 2. Main Menu System

#### MainMenuController.java
- **Purpose**: Handles the initial splash screen
- **Key Features**:
  - Displays background image from `/Assets/0710c65c16a3be8d29ba94af0a3b1460.jpg`
  - Single "PLAY" button that navigates to mode selection
  - Background image scales with window size
  - Uses AnchorPane layout for full-screen background

#### ModeSelectionController.java
- **Purpose**: Player count selection screen
- **Features**:
  - Three buttons: Single Player, Multiplayer, Back
  - Single Player → Direct to character creation (1 player)
  - Multiplayer → Player count selection screen
  - Clean VBox layout with centered buttons

#### PlayerCountSelectionController.java
- **Purpose**: Multiplayer player count selection
- **Features**:
  - ComboBox with options 2-10 players
  - Default selection: 2 players
  - Confirm → Character creation with selected count
  - Back → Return to mode selection

### 3. Character Creation System

#### CharacterCreationController.java
- **Purpose**: Complex character creation interface
- **Key Features**:

##### Layout Management:
- **Single Player Mode**: Centered form, no summary panel
- **Multiplayer Mode**: Side-by-side layout with player summary on left

##### Character Attributes:
1. **Name Selection**:
   - Editable ComboBox for custom names
   - Prompt text: "Enter name"

2. **Chakra Nature System**:
   - Dynamic dropdown count (1-5 natures)
   - Available natures: Fire, Water, Earth, Wind, Lightning
   - Prevents duplicate selection across dropdowns
   - Real-time validation and option filtering

3. **Jinchūriki System**:
   - Radio button choice (Yes/No)
   - Conditional Tailed Beast selector
   - 11 available beasts with nature descriptions
   - Beast exclusivity in multiplayer (once selected, unavailable to others)

##### Multiplayer Features:
- Player-by-player creation workflow
- Real-time summary list of created players
- Beast availability filtering
- Progress tracking ("Create Player X")

##### Data Model:
- Internal `Player` class storing:
  - Name
  - List of chakra natures
  - Selected tailed beast (or "None")

## FXML Structure

### 1. MainMenu.fxml
- **Layout**: AnchorPane with full-screen background
- **Components**: ImageView + single Play button
- **Styling**: Gold button with large font

### 2. ModeSelection.fxml
- **Layout**: Centered VBox
- **Components**: Three styled buttons
- **Padding**: Generous spacing for clean look

### 3. PlayerCountSelection.fxml
- **Layout**: Centered VBox
- **Components**: Label, ComboBox, two buttons
- **Styling**: Large fonts, consistent button sizing

### 4. CharacterCreation.fxml
- **Layout**: Complex HBox with conditional visibility
- **Left Panel**: Player summary (multiplayer only)
- **Right Panel**: Scrollable form with:
  - Header label
  - Name field
  - Chakra count selector
  - Dynamic chakra type dropdowns
  - Jinchūriki radio buttons
  - Conditional beast selector
  - Confirm/Back buttons

## Technical Implementation Details

### Navigation Pattern
- Scene root replacement for navigation
- FXMLLoader for loading new screens
- Controller communication via method calls (`startCreation()`)

### State Management
- Controllers maintain internal state
- Player data stored in `List<Player>`
- Dynamic UI updates based on selections

### UI Responsiveness
- ScrollPane for long character creation form
- Dynamic component visibility management
- Real-time validation and filtering

### Chakra Nature Logic
```java
// Prevents duplicate nature selection
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
    }
}
```

### Tailed Beast System
- 11 unique beasts with lore-accurate descriptions
- Nature affinities included in names
- Multiplayer exclusivity enforcement

## Game Flow
1. **Main Menu** → Background + Play button
2. **Mode Selection** → Single/Multi player choice
3. **Player Count** → (Multiplayer only) Select 2-10 players
4. **Character Creation** → Per-player attribute selection
5. **Game Launch** → (TODO: Not yet implemented)

## Assets Required
- Background image: `/Assets/0710c65c16a3be8d29ba94af0a3b1460.jpg`
- Potential tailed beast images (referenced in `TailedBeasts.java` but not used)

## Future Development Areas
- Actual game scene implementation
- Tailed beast image integration
- Character stat systems
- Game mechanics implementation
- Save/load functionality

## Code Quality Notes
- Clean separation of concerns
- Proper FXML controller pattern
- Responsive UI design
- Good state management
- Extensible architecture for game expansion