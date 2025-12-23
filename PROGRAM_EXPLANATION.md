# 📘 Program Structure and Game Loop Explanation

## For First-Year University Students

This document explains how the Tetris game works at a high level, focusing on the main concepts and flow.

---

## 🏗️ Program Structure

The program is organized into 4 main Python files:

```
┌─────────────────────────────────────────────────┐
│              main.py (Entry Point)              │
│  • Game loop                                    │
│  • User input handling                          │
│  • Drawing everything on screen                 │
└────────────┬────────────────────────────────────┘
             │ uses
             ↓
┌─────────────────────────────────────────────────┐
│         game.py (Game Logic)                    │
│  • Manages game state                           │
│  • Collision detection                          │
│  • Line clearing                                │
│  • Scoring                                      │
└────────────┬────────────────────────────────────┘
             │ uses
             ↓
┌─────────────────────────────────────────────────┐
│       tetromino.py (Pieces)                     │
│  • Defines 7 piece shapes                       │
│  • Rotation logic                               │
│  • Random piece generation                      │
└────────────┬────────────────────────────────────┘
             │ uses
             ↓
┌─────────────────────────────────────────────────┐
│     config.py (Configuration)                    │
│  • Colors, sizes, timings                       │
│  • Game settings                                │
└─────────────────────────────────────────────────┘
```

### Why This Structure?

1. **Separation of Concerns**: Each file has one main job
2. **Easy to Understand**: You can read one file at a time
3. **Easy to Modify**: Want to change colors? Edit `src/config.py`
4. **Reusable**: `Tetromino` class can be used in other projects

---

## 🎮 The Game Loop

The game loop is the heart of any game. It runs continuously (60 times per second) and does three things:

```python
while game_is_running:
    # 1. GET INPUT
    # What keys is the player pressing?
    
    # 2. UPDATE
    # Move pieces, check collisions, update score
    
    # 3. DRAW
    # Show everything on screen
    
    # 4. WAIT
    # Wait until it's time for the next frame
```

### Detailed Game Loop Flow

```
┌─────────────────────────────────────────────┐
│         START GAME LOOP                     │
└──────────────┬──────────────────────────────┘
               │
               ↓
┌─────────────────────────────────────────────┐
│  1. CALCULATE TIME                          │
│     • How much time passed since last frame?│
│     • Store as 'delta_time'                 │
└──────────────┬──────────────────────────────┘
               │
               ↓
┌─────────────────────────────────────────────┐
│  2. HANDLE INPUT (Event-based)              │
│     • Did player press a key?               │
│     • Up/X/Z → Rotate piece                 │
│     • Space → Hard drop                     │
│     • C → Hold piece                        │
│     • R → Restart game                      │
│     • Esc → Quit                            │
└──────────────┬──────────────────────────────┘
               │
               ↓
┌─────────────────────────────────────────────┐
│  3. HANDLE CONTINUOUS INPUT                 │
│     • Is player holding a key?              │
│     • Left arrow → Move left (with delay)   │
│     • Right arrow → Move right (with delay) │
│     • Down arrow → Soft drop active         │
└──────────────┬──────────────────────────────┘
               │
               ↓
┌─────────────────────────────────────────────┐
│  4. UPDATE GAME STATE                       │
│     • Call game_state.update()              │
│     • This does:                            │
│       - Make piece fall                     │
│       - Check for collisions                │
│       - Lock piece if on ground too long    │
│       - Clear completed lines               │
│       - Spawn new piece                     │
│       - Check for game over                 │
└──────────────┬──────────────────────────────┘
               │
               ↓
┌─────────────────────────────────────────────┐
│  5. DRAW EVERYTHING                         │
│     • Clear screen                          │
│     • Draw grid lines                       │
│     • Draw locked pieces                    │
│     • Draw ghost piece                      │
│     • Draw current piece                    │
│     • Draw UI (score, next piece, etc.)     │
│     • Draw game over screen (if needed)     │
└──────────────┬──────────────────────────────┘
               │
               ↓
┌─────────────────────────────────────────────┐
│  6. UPDATE DISPLAY                          │
│     • Show everything to player             │
│     • pygame.display.flip()                 │
└──────────────┬──────────────────────────────┘
               │
               ↓
┌─────────────────────────────────────────────┐
│  7. WAIT FOR NEXT FRAME                     │
│     • clock.tick(60) → 60 FPS               │
│     • Ensures consistent game speed         │
└──────────────┬──────────────────────────────┘
               │
               ↓
               │  Game still running?
               │
               └────────→ YES → Go back to step 1
               │
               ↓ NO
┌─────────────────────────────────────────────┐
│         END GAME, CLEANUP                   │
└─────────────────────────────────────────────┘
```

---

## 🔄 Key Game Systems

### 1. Piece Movement System

```
Player presses LEFT
    ↓
Check: Would piece collide if moved left?
    ↓
NO collision → Move piece left
YES collision → Do nothing (piece stays in place)
```

### 2. Collision Detection

Before any movement, we check:

```python
For each block in the piece:
    new_position = current_position + movement
    
    # Check boundaries
    if new_position is outside grid:
        return COLLISION
    
    # Check locked blocks
    if grid has a block at new_position:
        return COLLISION

return NO_COLLISION
```

### 3. Automatic Falling

```
Every frame:
    fall_timer += time_since_last_frame
    
    if fall_timer >= fall_speed:
        fall_timer = 0
        
        if piece_can_move_down:
            piece.y += 1
        else:
            start_lock_timer
```

### 4. Lock Delay System

This gives players time to adjust pieces at the bottom:

```
When piece touches ground:
    lock_timer starts counting
    
    if lock_timer >= 0.5 seconds:
        Lock piece into grid
        Check for line clears
        Spawn next piece
    
If piece moves off ground:
    lock_timer = 0 (reset)
```

### 5. Line Clearing Algorithm

```
1. CHECK PHASE
   For each row in grid (top to bottom):
       if all_blocks_filled:
           add row to lines_to_clear
   
2. ANIMATION PHASE (if lines found)
   Show shrinking/fading animation for 0.3 seconds
   
3. CLEAR PHASE
   For each line_to_clear (bottom to top):
       Remove row from grid
   
   Add new empty rows at top
   
4. SCORING PHASE
   Count how many lines cleared
   base_score = lookup_score(num_lines)
   final_score = base_score × current_level
   Add to player's score
```

### 6. Rotation with Wall Kicks

Wall kicks allow pieces to rotate even when close to walls:

```
Player presses ROTATE
    ↓
Try rotating piece in place
    ↓
Can it rotate? 
    YES → Done!
    NO → Try wall kicks ↓
    
Try moving piece slightly and rotating:
    Try (+1, 0)  → right 1 square
    Try (-1, 0)  → left 1 square
    Try (0, -1)  → up 1 square
    Try (+1, -1) → diagonal
    Try (-1, -1) → diagonal
    
If any works → Use that position
If none work → Rotation fails
```

---

## 📊 Data Structures

### The Grid (2D List)

```python
grid = [
    [None, None, Color, None, ...],  # Row 0 (top)
    [None, Color, Color, None, ...], # Row 1
    [Color, Color, Color, Color, ...], # Row 2
    ...
]

# None means empty space
# Color means a block is locked there
```

### A Tetromino Piece

```python
piece = {
    'type': 'T',           # Which piece (I, O, T, S, Z, J, L)
    'x': 4,                # Horizontal position
    'y': 0,                # Vertical position
    'rotation': 0,         # Rotation state (0, 1, 2, 3)
    'shape': [             # 4x4 grid
        [0, 0, 0, 0],
        [0, 1, 0, 0],      # 1 = filled, 0 = empty
        [1, 1, 1, 0],
        [0, 0, 0, 0]
    ]
}
```

---

## ⏱️ Timing System

The game uses several timers to control behavior:

1. **Fall Timer**: Makes pieces fall automatically
   - Resets every time piece drops one row
   - Speed increases with level

2. **Lock Timer**: Delay before piece locks at bottom
   - Starts when piece touches ground
   - Gives player 0.5 seconds to adjust
   - Resets if piece moves off ground

3. **Move Timer**: Prevents too-fast left/right movement
   - 0.15 second delay between moves
   - Makes control feel better

4. **Line Clear Timer**: Animation duration
   - 0.3 seconds for fade/shrink effect
   - Game pauses input during animation

---

## 🎯 Game State Management

The game has different states:

### STATE_PLAYING
- Normal gameplay
- Accept all input
- Pieces fall and move
- Check collisions

### STATE_LINE_CLEAR_ANIMATION
- Lines are being cleared
- Show animation effect
- Ignore player input (except restart/quit)
- When animation done → remove lines, update score

### GAME_OVER
- Pieces reached the top
- Show "GAME OVER" overlay
- Only accept R (restart) or Esc (quit)
- Save high score if needed

---

## 🔢 Scoring System Details

```
Base Scores:
├── 1 line  (Single) = 100 points
├── 2 lines (Double) = 300 points
├── 3 lines (Triple) = 500 points
└── 4 lines (Tetris) = 800 points

Final Score = Base Score × Current Level

Example:
- Clear 4 lines on Level 3
- Score = 800 × 3 = 2,400 points!

Bonus Points:
- Soft drop: +1 per row
- Hard drop: +2 per row
```

---

## 🎨 Rendering Order (Bottom to Top)

Drawing happens in this order (back to front):

1. **Background** (dark gray)
2. **Grid lines** (light gray outlines)
3. **Locked pieces** (colored blocks in grid)
4. **Ghost piece** (semi-transparent preview)
5. **Current piece** (fully opaque)
6. **UI panel** (score, next, hold, controls)
7. **Game over overlay** (if game over)

---

## 🧩 The 7-Bag Randomizer

How pieces are chosen fairly:

```
1. Create a bag with all 7 piece types
   Bag = [I, O, T, S, Z, J, L]

2. Shuffle the bag randomly
   Bag = [T, Z, I, O, L, S, J] (example)

3. Draw pieces one by one
   Next piece = J (pop from bag)
   Next piece = S (pop from bag)
   ...

4. When bag is empty → Refill and shuffle again

This ensures:
- You'll see each piece type before seeing any repeat
- No "piece droughts" (no starving for I-pieces!)
- Fair distribution over time
```

---

## 💾 High Score Persistence

```
When game over:
    if current_score > high_score:
        Save to file "highscore.txt"

When game starts:
    Try to read "highscore.txt"
    if file exists:
        Load high_score from file
    else:
        high_score = 0
```

---

## 🎓 Key Programming Concepts Used

1. **Classes and Objects**
   - `Tetromino` class for pieces
   - `GameState` class for game logic
   - `TetrisGame` class for rendering

2. **2D Lists**
   - Grid representation
   - Piece shape matrices

3. **Game Loop Pattern**
   - Input → Update → Render → Repeat

4. **Collision Detection**
   - Boundary checking
   - Grid checking

5. **State Management**
   - Different game states
   - State transitions

6. **File I/O**
   - Saving/loading high score

7. **Event Handling**
   - Keyboard input
   - Different types of input (press vs hold)

---

## 🚀 Running the Program

```bash
# Install pygame
pip install pygame

# Run the game
python main.py
```

The game window opens, and the game loop starts running at 60 FPS!

---

## 📖 Further Learning

To understand the code better:

1. **Start with `src/config.py`**: See all the game settings
2. **Read `tetromino.py`**: Understand piece shapes
3. **Study `game.py`**: Learn the game logic
4. **Explore `main.py`**: See the game loop and rendering

Try modifying values in `src/config.py` to see how they affect the game!

---

**Happy Learning! 🎓**

