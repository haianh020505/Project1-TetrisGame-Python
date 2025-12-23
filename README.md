# 🎮 Tetris Game - Python Edition

A complete Tetris game implementation in Python using Pygame, designed for educational purposes and university presentations.

## 📋 Project Overview

This is a beginner-friendly implementation of the classic Tetris game with all the modern features:

- **7 Tetromino pieces** (I, O, T, S, Z, J, L) with proper colors
- **Ghost piece** showing landing position
- **Hold piece** functionality
- **Line clear animation** with visual effects
- **Scoring system** (Single, Double, Triple, Tetris)
- **Progressive difficulty** (level increases every 10 lines)
- **High score persistence** (saved to file)
- **Smooth controls** with wall kicks for rotation

## 🎯 Game Features

### Core Gameplay
- Pieces fall from the top of the grid
- Move pieces left, right, and rotate them
- Complete horizontal lines to clear them and score points
- Game ends when pieces reach the top

### Advanced Features
- **Ghost Piece**: Semi-transparent preview shows where piece will land
- **Hold System**: Save a piece for later use (press C)
- **Hard Drop**: Instantly drop piece to bottom (Space)
- **Soft Drop**: Make piece fall faster (Down arrow)
- **Wall Kicks**: Pieces can rotate near walls with smart adjustments
- **Lock Delay**: 0.5 second grace period when piece touches bottom
- **7-Bag Randomizer**: Fair piece distribution (won't starve you of any piece)
- **Level System**: Speed increases as you clear more lines

## 🎮 Controls

| Key | Action |
|-----|--------|
| **←** | Move piece left |
| **→** | Move piece right |
| **↓** | Soft drop (faster fall) |
| **Space** | Hard drop (instant drop) |
| **↑** or **X** | Rotate clockwise |
| **Z** | Rotate counter-clockwise |
| **C** | Hold piece |
| **R** | Restart game |
| **Esc** | Quit game |

## 📊 Scoring System

| Lines Cleared | Name | Base Score |
|--------------|------|------------|
| 1 line | Single | 100 × Level |
| 2 lines | Double | 300 × Level |
| 3 lines | Triple | 500 × Level |
| 4 lines | **Tetris** | 800 × Level |

**Additional Points:**
- Soft Drop: +1 point per row
- Hard Drop: +2 points per row

**Level Progression:**
- Level increases every 10 lines cleared
- Higher levels = faster falling speed
- Score multipliers increase with level

## 🚀 Installation & Running

### Prerequisites
- Python 3.7 or higher
- pip (Python package installer)

### Setup Instructions

1. **Install required packages:**
```bash
pip install -r requirements.txt
```

2. **Run the game:**
```bash
python src/main.py
```

That's it! The game will open in a new window.

## 📁 Project Structure

```
Tetris/
│
├── src/
│   ├── main.py       # Main game loop and rendering
│   ├── game.py       # Game logic and state management
│   ├── tetromino.py  # Piece definitions and randomizer
│   └── config.py     # Game configuration and constants
├── requirements.txt  # Python dependencies
├── README.md         # This file
└── highscore.txt     # Saved high score (created automatically)
```

### File Descriptions

**config.py**
- Defines all game constants (colors, sizes, timings, scoring)
- Easy to modify for customization
- Well-documented configuration values

**tetromino.py**
- Defines the 7 tetromino piece types
- Implements rotation logic (clockwise and counter-clockwise)
- BagRandomizer class for fair piece generation

**game.py**
- Main game logic and state management
- Collision detection
- Line clearing and scoring
- Piece movement and locking
- High score persistence

**main.py**
- Game loop (runs 60 times per second)
- Input handling (keyboard controls)
- Rendering all visual elements
- UI display (score, next piece, etc.)

## 🎓 Program Structure Explanation

### Game Loop (main.py)

The game follows a classic game loop pattern:

```
1. Initialize game (create window, load resources)
2. Loop forever:
   a. Handle input (keyboard)
   b. Update game state (move pieces, check collisions)
   c. Draw everything on screen
   d. Wait for next frame (60 FPS)
3. Clean up and exit
```

### Game State Management (game.py)

The `GameState` class maintains all information about the current game:
- **Grid**: 2D array of locked blocks (10 columns × 20 rows)
- **Current Piece**: The falling piece being controlled
- **Next Piece**: Preview of upcoming piece
- **Held Piece**: Piece stored for later use
- **Score, Level, Lines**: Game statistics
- **Timers**: For falling, locking, and animations

### Collision Detection

Before moving or rotating a piece, the game checks:
1. **Boundary check**: Is piece inside the grid?
2. **Block check**: Does piece overlap with locked blocks?

If either check fails, the movement is prevented.

### Line Clearing Algorithm

```
1. Check each row from top to bottom
2. If row is completely filled:
   - Mark it for clearing
3. If any rows marked:
   - Play clear animation (fade and shrink)
   - Remove marked rows
   - Add new empty rows at top
   - Calculate and award score
```

## 🎨 Customization

You can easily customize the game by editing `src/config.py`:

- **Grid size**: Change `GRID_WIDTH` and `GRID_HEIGHT`
- **Colors**: Modify `COLOR_*` values (RGB format)
- **Speed**: Adjust `INITIAL_FALL_SPEED` and level calculation
- **Scoring**: Change `SCORE_*` values
- **Timings**: Modify `LOCK_DELAY`, animation durations, etc.

## 🐛 Troubleshooting

**Game won't start:**
- Make sure pygame is installed: `pip install pygame`
- Check Python version: `python --version` (need 3.7+)

**Game runs too fast/slow:**
- The game is designed to run at 60 FPS
- Frame rate is capped in the code (see `clock.tick(60)`)

**High score not saving:**
- Make sure the program has write permissions in its directory
- Check if `highscore.txt` was created

## 📚 Learning Resources

This project demonstrates several important programming concepts:

1. **Object-Oriented Programming**: Classes for game state, pieces, etc.
2. **Game Loop**: Update-Draw cycle running at fixed FPS
3. **2D Arrays**: Grid representation and manipulation
4. **Collision Detection**: Checking piece positions
5. **State Management**: Tracking game state and transitions
6. **File I/O**: Saving and loading high scores
7. **Event Handling**: Responding to keyboard input

## 🎓 For Students

This codebase is designed to be:
- **Readable**: Clear variable names and structure
- **Well-commented**: Explanations of logic and algorithms
- **Modular**: Separated into logical files and classes
- **Beginner-friendly**: Avoids advanced Python features

Perfect for:
- Learning game development basics
- Understanding event-driven programming
- Practicing object-oriented design
- University project presentations

## 🔮 Future Enhancements

Ideas for extending this project:
- Add sound effects and background music
- Implement T-Spin detection and scoring
- Add multiplayer mode
- Create different game modes (Marathon, Sprint, Ultra)
- Add particle effects for line clears
- Implement touch controls for mobile
- Add a menu system

## 📝 License

This project is created for educational purposes. Feel free to use, modify, and share!

## 👨‍💻 Author

Created as an educational Tetris implementation for university students learning Python and game development.

---

**Have fun playing Tetris! 🎮**

