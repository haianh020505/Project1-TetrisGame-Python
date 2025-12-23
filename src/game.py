"""
Game State and Logic

This file contains the main game logic including:
- Board management (grid of locked blocks)
- Collision detection
- Piece movement and rotation
- Line clearing
- Scoring system
- Game state management
"""

import pygame
import os
from config import *
from tetromino import Tetromino, BagRandomizer


class GameState:
    """
    Manages the complete state of the Tetris game.
    
    This includes:
    - The game grid (locked pieces)
    - Current falling piece
    - Next piece preview
    - Held piece
    - Score, level, lines cleared
    - Game over status
    """
    
    # Game states for animations
    STATE_PLAYING = 0
    STATE_LINE_CLEAR_ANIMATION = 1
    
    def __init__(self):
        """Initialize a new game"""
        # Create the grid (2D list of colors, None means empty)
        self.grid = [[None for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        
        # Initialize piece randomizer (7-bag system)
        self.bag_randomizer = BagRandomizer()
        
        # Create first piece and preview next piece
        self.current_piece = Tetromino(self.bag_randomizer.next())
        self.next_piece_type = self.bag_randomizer.peek()
        
        # Hold piece system
        self.held_piece_type = None
        self.can_hold = True  # Can only hold once per piece
        
        # Scoring and progression
        self.score = 0
        self.high_score = self.load_high_score()
        self.level = 1
        self.lines_cleared = 0
        
        # Game state
        self.game_over = False
        self.state = self.STATE_PLAYING
        
        # Timers for game mechanics
        self.fall_timer = 0.0          # Timer for automatic piece falling
        self.lock_timer = 0.0          # Timer before piece locks at bottom
        self.is_on_ground = False      # Is current piece touching ground?
        
        # Line clear animation
        self.line_clear_timer = 0.0
        self.lines_being_cleared = []  # List of row indices being cleared

    def update(self, delta_time, soft_drop):
        """
        Update game state each frame.
        
        Args:
            delta_time: Time elapsed since last frame (in seconds)
            soft_drop: True if player is holding down arrow
        """
        if self.game_over:
            return

        # Handle line clear animation
        if self.state == self.STATE_LINE_CLEAR_ANIMATION:
            self.line_clear_timer += delta_time
            
            # When animation finishes, actually clear the lines
            if self.line_clear_timer >= LINE_CLEAR_ANIMATION:
                self.complete_line_clear()
                self.state = self.STATE_PLAYING
                self.line_clear_timer = 0.0
                self.lines_being_cleared = []
            return

        # Calculate fall speed based on level and soft drop
        if soft_drop:
            fall_speed = FAST_DROP_SPEED
        else:
            fall_speed = INITIAL_FALL_SPEED / self.level
        
        self.fall_timer += delta_time

        # Check if piece is on the ground
        was_on_ground = self.is_on_ground
        self.is_on_ground = self.check_collision(0, 1)

        # If on ground, start lock timer
        if self.is_on_ground:
            self.lock_timer += delta_time
            # Lock piece after delay
            if self.lock_timer >= LOCK_DELAY:
                self.lock_piece()
        else:
            self.lock_timer = 0.0

        # Make piece fall automatically
        if self.fall_timer >= fall_speed:
            self.fall_timer = 0.0
            if not self.is_on_ground:
                self.current_piece.y += 1
                # Award points for soft drop
                if soft_drop:
                    self.score += SCORE_SOFT_DROP

        # Reset lock timer if piece moved off ground
        if was_on_ground and not self.is_on_ground:
            self.lock_timer = 0.0

    def move_left(self):
        """Try to move the current piece left"""
        if not self.check_collision(-1, 0):
            self.current_piece.x -= 1

    def move_right(self):
        """Try to move the current piece right"""
        if not self.check_collision(1, 0):
            self.current_piece.x += 1

    def rotate_clockwise(self):
        """
        Try to rotate the piece clockwise.
        
        If direct rotation fails, try wall kicks:
        small adjustments to position that might make rotation work.
        """
        # Create a test piece to try rotation
        test_piece = self.current_piece.copy()
        test_piece.rotate_clockwise()

        # Try direct rotation
        if not self.check_collision_piece(test_piece):
            self.current_piece = test_piece
            return

        # Try wall kicks (small position adjustments)
        kicks = [(1, 0), (-1, 0), (0, -1), (1, -1), (-1, -1)]
        for dx, dy in kicks:
            test_piece.x = self.current_piece.x + dx
            test_piece.y = self.current_piece.y + dy
            if not self.check_collision_piece(test_piece):
                self.current_piece = test_piece
                return

    def rotate_counterclockwise(self):
        """
        Try to rotate the piece counter-clockwise.
        
        Similar to clockwise but in opposite direction.
        """
        test_piece = self.current_piece.copy()
        test_piece.rotate_counterclockwise()

        # Try direct rotation
        if not self.check_collision_piece(test_piece):
            self.current_piece = test_piece
            return

        # Try wall kicks
        kicks = [(1, 0), (-1, 0), (0, -1), (1, -1), (-1, -1)]
        for dx, dy in kicks:
            test_piece.x = self.current_piece.x + dx
            test_piece.y = self.current_piece.y + dy
            if not self.check_collision_piece(test_piece):
                self.current_piece = test_piece
                return

    def hard_drop(self):
        """
        Instantly drop the piece to the bottom.
        
        Award points based on distance dropped.
        """
        ghost_y = self.calculate_ghost_y()
        drop_distance = ghost_y - self.current_piece.y
        
        # Award points for hard drop
        self.score += drop_distance * SCORE_HARD_DROP
        
        self.current_piece.y = ghost_y
        self.lock_piece()

    def hold_piece(self):
        """
        Hold the current piece for later use.
        
        Can only hold once per piece (until it locks).
        If already holding a piece, swap with it.
        """
        if not self.can_hold:
            return

        current_type = self.current_piece.piece_type

        if self.held_piece_type is not None:
            # Swap with held piece
            self.current_piece = Tetromino(self.held_piece_type)
            self.held_piece_type = current_type
        else:
            # Hold current and spawn next
            self.held_piece_type = current_type
            self.spawn_next_piece()

        self.can_hold = False

    def check_collision(self, dx, dy):
        """
        Check if moving the current piece by (dx, dy) would cause a collision.
        
        Args:
            dx: Horizontal movement
            dy: Vertical movement
            
        Returns:
            True if collision would occur, False otherwise
        """
        blocks = self.current_piece.get_blocks()
        
        for x, y in blocks:
            new_x = x + dx
            new_y = y + dy
            
            # Check boundaries
            if new_x < 0 or new_x >= GRID_WIDTH or new_y >= GRID_HEIGHT:
                return True
            
            # Check collision with locked blocks (ignore blocks above grid)
            if new_y >= 0 and self.grid[new_y][new_x] is not None:
                return True
        
        return False

    def check_collision_piece(self, piece):
        """
        Check if a specific piece would collide with grid or boundaries.
        
        Used for testing rotations.
        
        Args:
            piece: The Tetromino to check
            
        Returns:
            True if collision would occur, False otherwise
        """
        blocks = piece.get_blocks()
        
        for x, y in blocks:
            # Check boundaries
            if x < 0 or x >= GRID_WIDTH or y >= GRID_HEIGHT:
                return True
            
            # Check collision with locked blocks
            if y >= 0 and self.grid[y][x] is not None:
                return True
        
        return False

    def calculate_ghost_y(self):
        """
        Calculate where the piece would land if dropped straight down.
        
        This is used to show the ghost piece (preview of landing position).
        
        Returns:
            The y-coordinate where the piece would land
        """
        ghost_y = self.current_piece.y
        
        # Create a test piece to move down
        test_piece = self.current_piece.copy()
        
        # Keep moving down until collision
        while not self.check_collision_piece(test_piece):
            ghost_y = test_piece.y
            test_piece.y += 1
        
        return ghost_y

    def lock_piece(self):
        """
        Lock the current piece into the grid.
        
        This happens when:
        - Piece reaches bottom and lock delay expires
        - Player does a hard drop
        
        After locking:
        1. Add piece blocks to grid
        2. Check for line clears
        3. Spawn next piece
        4. Check for game over
        """
        blocks = self.current_piece.get_blocks()
        color = self.current_piece.get_color()

        # Add piece blocks to grid
        for x, y in blocks:
            if 0 <= y < GRID_HEIGHT and 0 <= x < GRID_WIDTH:
                self.grid[y][x] = color

        # Check for completed lines
        self.check_line_clears()
        
        # Spawn next piece
        self.spawn_next_piece()
        
        # Reset hold ability
        self.can_hold = True
        self.lock_timer = 0.0
        self.is_on_ground = False

    def spawn_next_piece(self):
        """
        Spawn the next piece from the bag.
        
        Check if it can spawn (if not, game over).
        """
        next_type = self.bag_randomizer.next()
        self.current_piece = Tetromino(next_type)
        self.next_piece_type = self.bag_randomizer.peek()
        self.fall_timer = 0.0

        # Check for game over (piece can't spawn)
        if self.check_collision_piece(self.current_piece):
            self.game_over = True
            # Update high score if needed
            if self.score > self.high_score:
                self.high_score = self.score
                self.save_high_score(self.high_score)

    def check_line_clears(self):
        """
        Check for completed lines and start clear animation.
        
        A line is complete when all blocks in the row are filled.
        """
        lines_to_clear = []

        # Check each row
        for y in range(GRID_HEIGHT):
            # Check if all blocks in row are filled
            if all(self.grid[y][x] is not None for x in range(GRID_WIDTH)):
                lines_to_clear.append(y)

        # If lines found, start animation
        if lines_to_clear:
            self.lines_being_cleared = lines_to_clear
            self.state = self.STATE_LINE_CLEAR_ANIMATION
            self.line_clear_timer = 0.0

    def complete_line_clear(self):
        """
        Actually remove the cleared lines and update score.
        
        Called after the line clear animation finishes.
        """
        if not self.lines_being_cleared:
            return

        num_lines = len(self.lines_being_cleared)

        # Remove cleared lines (start from bottom to avoid index issues)
        for y in sorted(self.lines_being_cleared, reverse=True):
            del self.grid[y]

        # Add new empty lines at top
        for _ in range(num_lines):
            self.grid.insert(0, [None for _ in range(GRID_WIDTH)])

        # Update score based on number of lines cleared
        score_table = {
            1: SCORE_SINGLE,
            2: SCORE_DOUBLE,
            3: SCORE_TRIPLE,
            4: SCORE_TETRIS,
        }
        base_score = score_table.get(num_lines, 0)
        self.score += base_score * self.level

        # Update lines cleared counter
        self.lines_cleared += num_lines

        # Update level (every 10 lines increases level)
        self.level = (self.lines_cleared // 10) + 1

        # Update high score
        if self.score > self.high_score:
            self.high_score = self.score

    def reset(self):
        """Reset the game to initial state (restart)"""
        self.__init__()

    def load_high_score(self):
        """
        Load the high score from file.
        
        Returns:
            The saved high score, or 0 if file doesn't exist
        """
        try:
            if os.path.exists(HIGHSCORE_FILE):
                with open(HIGHSCORE_FILE, 'r') as f:
                    return int(f.read().strip())
        except:
            pass
        return 0

    def save_high_score(self, score):
        """
        Save the high score to file.
        
        Args:
            score: The score to save
        """
        try:
            with open(HIGHSCORE_FILE, 'w') as f:
                f.write(str(score))
        except:
            pass

