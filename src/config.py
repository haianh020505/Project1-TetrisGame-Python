"""
Constants and Configuration for Tetris Game

This file contains all the constant values used throughout the game:
- Grid dimensions
- Colors for each tetromino piece
- Game timing settings
- Scoring rules
"""
import pygame

# Grid dimensions (in blocks)
GRID_WIDTH = 10   # 10 blocks wide
GRID_HEIGHT = 20  # 20 blocks tall
BLOCK_SIZE = 30   # Each block is 30x30 pixels

# Screen dimensions (in pixels)
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 650

# Position of the game grid on screen
GRID_OFFSET_X = 50
GRID_OFFSET_Y = 50

# Position of the UI panel (score, next piece, etc.)
UI_OFFSET_X = GRID_OFFSET_X + (GRID_WIDTH * BLOCK_SIZE) + 50
UI_OFFSET_Y = 50

# Game timing (in seconds)
INITIAL_FALL_SPEED = 1.0      # How many seconds before piece falls one row
FAST_DROP_SPEED = 0.05        # Speed when holding down arrow
LOCK_DELAY = 0.5              # Time piece stays at bottom before locking
LINE_CLEAR_ANIMATION = 0.3    # Duration of line clear animation
MOVE_DELAY = 0.15             # Delay between repeated left/right moves

# Scoring system (points awarded for clearing lines)
SCORE_SINGLE = 100    # Clear 1 line
SCORE_DOUBLE = 300    # Clear 2 lines
SCORE_TRIPLE = 500    # Clear 3 lines
SCORE_TETRIS = 800    # Clear 4 lines (Tetris!)
SCORE_SOFT_DROP = 1   # Points per row for soft drop
SCORE_HARD_DROP = 2   # Points per row for hard drop

# Colors (RGB format)
# Background and UI colors
COLOR_BACKGROUND = (25, 25, 30)      # Dark gray background
COLOR_GRID = (50, 50, 65)            # Grid lines
COLOR_TEXT = (230, 230, 230)         # White text
COLOR_GHOST_ALPHA = 77               # Transparency for ghost piece (0-255)

# Tetromino colors (each piece type has its own color)
COLOR_I = (0, 230, 230)    # Cyan - I piece (straight line)
COLOR_O = (230, 230, 0)    # Yellow - O piece (square)
COLOR_T = (180, 0, 230)    # Purple - T piece
COLOR_S = (0, 230, 0)      # Green - S piece
COLOR_Z = (230, 0, 0)      # Red - Z piece
COLOR_J = (0, 0, 230)      # Blue - J piece
COLOR_L = (230, 128, 0)    # Orange - L piece
COLOR_WHITE = (255, 255, 255)  # White for outlines

# File to save high score
HIGHSCORE_FILE = "highscore.txt"

