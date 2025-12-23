"""
Tetromino Classes and Piece Generation

This file defines:
- The 7 different tetromino shapes (I, O, T, S, Z, J, L)
- Tetromino class with rotation logic
- BagRandomizer for fair random piece generation (7-bag system)
"""

import random
from config import *


class TetrominoType:
    """
    Defines the 7 types of Tetris pieces.
    Each piece has a unique shape and color.
    """
    I = 'I'  # Straight line piece
    O = 'O'  # Square piece
    T = 'T'  # T-shaped piece
    S = 'S'  # S-shaped piece
    Z = 'Z'  # Z-shaped piece
    J = 'J'  # J-shaped piece
    L = 'L'  # L-shaped piece

    @staticmethod
    def all_types():
        """Returns a list of all 7 piece types"""
        return [TetrominoType.I, TetrominoType.O, TetrominoType.T,
                TetrominoType.S, TetrominoType.Z, TetrominoType.J,
                TetrominoType.L]

    @staticmethod
    def get_color(piece_type):
        """Returns the color for a given piece type"""
        colors = {
            TetrominoType.I: COLOR_I,
            TetrominoType.O: COLOR_O,
            TetrominoType.T: COLOR_T,
            TetrominoType.S: COLOR_S,
            TetrominoType.Z: COLOR_Z,
            TetrominoType.J: COLOR_J,
            TetrominoType.L: COLOR_L,
        }
        return colors[piece_type]

    @staticmethod
    def get_shape(piece_type):
        """
        Returns the shape matrix for a given piece type.
        
        Each shape is a 4x4 grid where:
        - 0 represents empty space
        - 1 represents a filled block
        
        This makes it easy to rotate and check collisions.
        """
        shapes = {
            TetrominoType.I: [
                [0, 0, 0, 0],
                [1, 1, 1, 1],
                [0, 0, 0, 0],
                [0, 0, 0, 0],
            ],
            TetrominoType.O: [
                [0, 0, 0, 0],
                [0, 1, 1, 0],
                [0, 1, 1, 0],
                [0, 0, 0, 0],
            ],
            TetrominoType.T: [
                [0, 0, 0, 0],
                [0, 1, 0, 0],
                [1, 1, 1, 0],
                [0, 0, 0, 0],
            ],
            TetrominoType.S: [
                [0, 0, 0, 0],
                [0, 1, 1, 0],
                [1, 1, 0, 0],
                [0, 0, 0, 0],
            ],
            TetrominoType.Z: [
                [0, 0, 0, 0],
                [1, 1, 0, 0],
                [0, 1, 1, 0],
                [0, 0, 0, 0],
            ],
            TetrominoType.J: [
                [0, 0, 0, 0],
                [1, 0, 0, 0],
                [1, 1, 1, 0],
                [0, 0, 0, 0],
            ],
            TetrominoType.L: [
                [0, 0, 0, 0],
                [0, 0, 1, 0],
                [1, 1, 1, 0],
                [0, 0, 0, 0],
            ],
        }
        return shapes[piece_type]


class Tetromino:
    """
    Represents a single tetromino piece that can move and rotate.
    
    Attributes:
        piece_type: The type of piece (I, O, T, S, Z, J, L)
        shape: 4x4 grid representing the piece
        x, y: Position on the game grid
        rotation: Current rotation state (0, 1, 2, or 3)
    """
    
    def __init__(self, piece_type):
        """
        Create a new tetromino piece.
        
        Args:
            piece_type: One of the TetrominoType constants
        """
        self.piece_type = piece_type
        self.shape = TetrominoType.get_shape(piece_type)
        
        # Start position: center top of grid
        self.x = GRID_WIDTH // 2 - 2
        self.y = 0
        self.rotation = 0

    def get_color(self):
        """Returns the color of this piece"""
        return TetrominoType.get_color(self.piece_type)

    def get_blocks(self):
        """
        Returns a list of (x, y) coordinates for all filled blocks in the piece.
        
        This is useful for:
        - Drawing the piece
        - Checking collisions
        - Locking the piece into the grid
        
        Returns:
            List of (x, y) tuples representing block positions
        """
        blocks = []
        for i in range(len(self.shape)):
            for j in range(len(self.shape[i])):
                if self.shape[i][j] == 1:
                    # Add piece position to get actual grid coordinates
                    blocks.append((self.x + j, self.y + i))
        return blocks

    def rotate_clockwise(self):
        """
        Rotate the piece 90 degrees clockwise.
        
        The O piece doesn't rotate (it's a square).
        
        Rotation algorithm:
        - Take the transpose of the matrix
        - Reverse each row
        """
        # O piece doesn't rotate
        if self.piece_type == TetrominoType.O:
            return

        n = len(self.shape)
        # Create new rotated shape
        rotated = [[0 for _ in range(n)] for _ in range(n)]
        
        # Rotate 90 degrees clockwise
        for i in range(n):
            for j in range(n):
                rotated[j][n - 1 - i] = self.shape[i][j]
        
        self.shape = rotated
        self.rotation = (self.rotation + 1) % 4

    def rotate_counterclockwise(self):
        """
        Rotate the piece 90 degrees counter-clockwise.
        
        Similar to clockwise rotation but in the opposite direction.
        """
        # O piece doesn't rotate
        if self.piece_type == TetrominoType.O:
            return

        n = len(self.shape)
        # Create new rotated shape
        rotated = [[0 for _ in range(n)] for _ in range(n)]
        
        # Rotate 90 degrees counter-clockwise
        for i in range(n):
            for j in range(n):
                rotated[n - 1 - j][i] = self.shape[i][j]
        
        self.shape = rotated
        self.rotation = (self.rotation + 3) % 4

    def copy(self):
        """
        Create a copy of this piece.
        
        Used for testing rotations and movements without
        affecting the original piece.
        """
        new_piece = Tetromino(self.piece_type)
        new_piece.shape = [row[:] for row in self.shape]
        new_piece.x = self.x
        new_piece.y = self.y
        new_piece.rotation = self.rotation
        return new_piece


class BagRandomizer:
    """
    Implements the 7-bag randomization system.
    
    This is the standard Tetris randomization method:
    - Put all 7 pieces in a bag
    - Shuffle the bag
    - Draw pieces one by one
    - When empty, refill and shuffle again
    
    This ensures fair distribution - you'll never go too long
    without seeing a specific piece type.
    """
    
    def __init__(self):
        """Create a new bag randomizer with a full shuffled bag"""
        self.bag = []
        self.refill_bag()

    def refill_bag(self):
        """Fill the bag with all 7 piece types and shuffle"""
        self.bag = TetrominoType.all_types()
        random.shuffle(self.bag)

    def next(self):
        """
        Get the next piece from the bag.
        
        If the bag is empty, it automatically refills.
        
        Returns:
            A TetrominoType constant
        """
        if len(self.bag) == 0:
            self.refill_bag()
        return self.bag.pop()

    def peek(self):
        """
        Look at the next piece without removing it from the bag.
        
        This is used to show the "NEXT" piece preview.
        
        Returns:
            A TetrominoType constant
        """
        if len(self.bag) == 0:
            self.refill_bag()
        return self.bag[-1]

