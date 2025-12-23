"""
Tetris Game - Main Entry Point

This is the main file that runs the Tetris game.

It contains:
- Game loop (update and draw)
- Input handling
- Rendering all visual elements
"""

import pygame
import sys
from config import *
from game import GameState
from tetromino import TetrominoType


class TetrisGame:
    """
    Main game class that handles the game loop and rendering.
    """
    
    def __init__(self):
        """Initialize pygame and create the game window"""
        pygame.init()
        
        # Create the game window
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Tetris")
        
        # Create clock for controlling frame rate
        self.clock = pygame.time.Clock()
        
        # Create fonts for text rendering
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 32)
        self.font_small = pygame.font.Font(None, 24)
        self.font_tiny = pygame.font.Font(None, 20)
        
        # Create game state
        self.game_state = GameState()
        
        # Track time for movement delay
        self.last_move_time = 0.0
        self.last_frame_time = pygame.time.get_ticks() / 1000.0

    def run(self):
        """
        Main game loop.
        
        This loop:
        1. Handles input from player
        2. Updates game state
        3. Draws everything on screen
        4. Repeats 60 times per second
        """
        running = True
        
        while running:
            # Calculate time since last frame (delta time)
            current_time = pygame.time.get_ticks() / 1000.0
            delta_time = current_time - self.last_frame_time
            self.last_frame_time = current_time
            
            # Handle events (keyboard input, window close, etc.)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                # Handle key presses (one-time actions)
                if event.type == pygame.KEYDOWN:
                    if not self.game_state.game_over and self.game_state.state == GameState.STATE_PLAYING:
                        # Rotation
                        if event.key == pygame.K_UP or event.key == pygame.K_x:
                            self.game_state.rotate_clockwise()
                        elif event.key == pygame.K_z:
                            self.game_state.rotate_counterclockwise()
                        
                        # Hard drop
                        elif event.key == pygame.K_SPACE:
                            self.game_state.hard_drop()
                        
                        # Hold piece
                        elif event.key == pygame.K_c:
                            self.game_state.hold_piece()
                    
                    # Restart (works even during game over)
                    if event.key == pygame.K_r:
                        self.game_state.reset()
                    
                    # Quit
                    if event.key == pygame.K_ESCAPE:
                        running = False
            
            # Handle continuous movement (holding keys down)
            if not self.game_state.game_over and self.game_state.state == GameState.STATE_PLAYING:
                keys = pygame.key.get_pressed()
                
                # Left/right movement with delay (prevents too-fast movement)
                if keys[pygame.K_LEFT] and current_time - self.last_move_time > MOVE_DELAY:
                    self.game_state.move_left()
                    self.last_move_time = current_time
                
                if keys[pygame.K_RIGHT] and current_time - self.last_move_time > MOVE_DELAY:
                    self.game_state.move_right()
                    self.last_move_time = current_time
                
                # Check if soft drop is active
                soft_drop = keys[pygame.K_DOWN]
                
                # Update game state
                self.game_state.update(delta_time, soft_drop)
            else:
                # During animation, just update without input
                self.game_state.update(delta_time, False)
            
            # Draw everything
            self.draw()
            
            # Update display and limit to 60 FPS
            pygame.display.flip()
            self.clock.tick(60)
        
        pygame.quit()
        sys.exit()

    def draw(self):
        """Draw all game elements on screen"""
        # Clear screen with background color
        self.screen.fill(COLOR_BACKGROUND)
        
        # Draw game grid and pieces
        self.draw_grid()
        self.draw_locked_pieces()
        self.draw_ghost_piece()
        self.draw_current_piece()
        
        # Draw UI (score, next piece, etc.)
        self.draw_ui()
        
        # Draw game over screen if needed
        if self.game_state.game_over:
            self.draw_game_over()

    def draw_grid(self):
        """
        Draw the game grid (background lines).
        
        This shows the player where each block position is.
        """
        # Draw grid cells
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                px = GRID_OFFSET_X + x * BLOCK_SIZE
                py = GRID_OFFSET_Y + y * BLOCK_SIZE
                
                # Draw cell outline
                pygame.draw.rect(self.screen, COLOR_GRID, 
                               (px, py, BLOCK_SIZE, BLOCK_SIZE), 1)
        
        # Draw border around grid
        border_rect = pygame.Rect(
            GRID_OFFSET_X - 2,
            GRID_OFFSET_Y - 2,
            GRID_WIDTH * BLOCK_SIZE + 4,
            GRID_HEIGHT * BLOCK_SIZE + 4
        )
        pygame.draw.rect(self.screen, COLOR_TEXT, border_rect, 2)

    def draw_locked_pieces(self):
        """
        Draw all the locked pieces on the grid.
        
        Includes line clear animation effects.
        """
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                color = self.game_state.grid[y][x]
                
                if color is not None:
                    px = GRID_OFFSET_X + x * BLOCK_SIZE
                    py = GRID_OFFSET_Y + y * BLOCK_SIZE
                    
                    # Check if this row is being cleared (animation)
                    if (self.game_state.state == GameState.STATE_LINE_CLEAR_ANIMATION and 
                        y in self.game_state.lines_being_cleared):
                        
                        # Calculate animation progress (0.0 to 1.0)
                        progress = self.game_state.line_clear_timer / LINE_CLEAR_ANIMATION
                        
                        # Create fading and shrinking effect
                        alpha = int(255 * (1.0 - progress))
                        shrink = progress * (BLOCK_SIZE - 2) * 0.5
                        size = (BLOCK_SIZE - 2) - (progress * (BLOCK_SIZE - 2))
                        
                        # Create semi-transparent surface for animation
                        surf = pygame.Surface((int(size), int(size)))
                        surf.set_alpha(alpha)
                        surf.fill(color)
                        
                        # Draw shrinking block
                        self.screen.blit(surf, (px + 1 + shrink, py + 1 + shrink))
                        
                        # Draw fading outline
                        outline_surf = pygame.Surface((int(size + 2), int(size + 2)))
                        outline_surf.set_alpha(alpha)
                        outline_surf.fill(COLOR_BACKGROUND)
                        outline_rect = outline_surf.get_rect()
                        pygame.draw.rect(outline_surf, COLOR_WHITE, outline_rect, 2)
                        self.screen.blit(outline_surf, (px + shrink, py + shrink))
                    else:
                        # Normal rendering
                        # Draw filled block
                        pygame.draw.rect(self.screen, color, 
                                       (px + 1, py + 1, BLOCK_SIZE - 2, BLOCK_SIZE - 2))
                        # Draw white outline
                        pygame.draw.rect(self.screen, COLOR_WHITE,
                                       (px, py, BLOCK_SIZE, BLOCK_SIZE), 2)

    def draw_ghost_piece(self):
        """
        Draw the ghost piece (shadow showing where piece will land).
        
        This helps players see where their piece will go.
        """
        ghost_y = self.game_state.calculate_ghost_y()
        blocks = self.game_state.current_piece.get_blocks()
        color = self.game_state.current_piece.get_color()
        
        # Calculate vertical offset for ghost
        y_offset = ghost_y - self.game_state.current_piece.y
        
        for x, y in blocks:
            new_y = y + y_offset
            if new_y >= 0:
                px = GRID_OFFSET_X + x * BLOCK_SIZE
                py = GRID_OFFSET_Y + new_y * BLOCK_SIZE
                
                # Create semi-transparent surface
                surf = pygame.Surface((BLOCK_SIZE - 2, BLOCK_SIZE - 2))
                surf.set_alpha(COLOR_GHOST_ALPHA)
                surf.fill(color)
                
                # Draw ghost block
                self.screen.blit(surf, (px + 1, py + 1))
                
                # Draw ghost outline
                pygame.draw.rect(self.screen, (*color, COLOR_GHOST_ALPHA),
                               (px, py, BLOCK_SIZE, BLOCK_SIZE), 1)

    def draw_current_piece(self):
        """Draw the currently falling piece"""
        blocks = self.game_state.current_piece.get_blocks()
        color = self.game_state.current_piece.get_color()
        
        for x, y in blocks:
            if y >= 0:  # Only draw blocks that are visible
                px = GRID_OFFSET_X + x * BLOCK_SIZE
                py = GRID_OFFSET_Y + y * BLOCK_SIZE
                
                # Draw filled block
                pygame.draw.rect(self.screen, color,
                               (px + 1, py + 1, BLOCK_SIZE - 2, BLOCK_SIZE - 2))
                # Draw white outline
                pygame.draw.rect(self.screen, COLOR_WHITE,
                               (px, py, BLOCK_SIZE, BLOCK_SIZE), 2)

    def draw_ui(self):
        """
        Draw the user interface panel.
        
        Shows:
        - Score
        - High score
        - Level
        - Lines cleared
        - Next piece preview
        - Held piece preview
        - Controls help
        """
        ui_x = UI_OFFSET_X
        ui_y = UI_OFFSET_Y
        
        # Score
        text = self.font_small.render("SCORE", True, COLOR_TEXT)
        self.screen.blit(text, (ui_x, ui_y))
        ui_y += 30
        
        text = self.font_medium.render(str(self.game_state.score), True, COLOR_WHITE)
        self.screen.blit(text, (ui_x, ui_y))
        ui_y += 50
        
        # High Score
        text = self.font_small.render("HIGH SCORE", True, COLOR_TEXT)
        self.screen.blit(text, (ui_x, ui_y))
        ui_y += 30
        
        text = self.font_medium.render(str(self.game_state.high_score), True, COLOR_WHITE)
        self.screen.blit(text, (ui_x, ui_y))
        ui_y += 50
        
        # Level
        text = self.font_small.render("LEVEL", True, COLOR_TEXT)
        self.screen.blit(text, (ui_x, ui_y))
        ui_y += 30
        
        text = self.font_medium.render(str(self.game_state.level), True, COLOR_WHITE)
        self.screen.blit(text, (ui_x, ui_y))
        ui_y += 50
        
        # Lines
        text = self.font_small.render("LINES", True, COLOR_TEXT)
        self.screen.blit(text, (ui_x, ui_y))
        ui_y += 30
        
        text = self.font_medium.render(str(self.game_state.lines_cleared), True, COLOR_WHITE)
        self.screen.blit(text, (ui_x, ui_y))
        ui_y += 50
        
        # Next piece
        text = self.font_small.render("NEXT", True, COLOR_TEXT)
        self.screen.blit(text, (ui_x, ui_y))
        ui_y += 30
        
        self.draw_preview_piece(self.game_state.next_piece_type, ui_x, ui_y)
        ui_y += 120
        
        # Hold piece
        text = self.font_small.render("HOLD", True, COLOR_TEXT)
        self.screen.blit(text, (ui_x, ui_y))
        ui_y += 30
        
        if self.game_state.held_piece_type is not None:
            self.draw_preview_piece(self.game_state.held_piece_type, ui_x, ui_y)
        ui_y += 120
        
        # Controls
        text = self.font_tiny.render("CONTROLS", True, COLOR_TEXT)
        self.screen.blit(text, (ui_x, ui_y))
        ui_y += 25
        
        controls = [
            "← → Move",
            "↓ Soft Drop",
            "Space Hard Drop",
            "Z/X Rotate",
            "C Hold",
            "R Restart"
        ]
        
        for control in controls:
            text = self.font_tiny.render(control, True, COLOR_TEXT)
            self.screen.blit(text, (ui_x, ui_y))
            ui_y += 20

    def draw_preview_piece(self, piece_type, x, y):
        """
        Draw a preview of a piece (for NEXT and HOLD displays).
        
        Args:
            piece_type: The type of piece to preview
            x, y: Position to draw the preview
        """
        shape = TetrominoType.get_shape(piece_type)
        color = TetrominoType.get_color(piece_type)
        preview_size = 20
        
        for i in range(len(shape)):
            for j in range(len(shape[i])):
                if shape[i][j] == 1:
                    px = x + j * preview_size
                    py = y + i * preview_size
                    
                    # Draw block
                    pygame.draw.rect(self.screen, color,
                                   (px + 1, py + 1, preview_size - 2, preview_size - 2))
                    pygame.draw.rect(self.screen, COLOR_WHITE,
                                   (px, py, preview_size, preview_size), 1)

    def draw_game_over(self):
        """Draw the game over overlay"""
        # Draw semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        # Draw "GAME OVER" text
        text = self.font_large.render("GAME OVER", True, COLOR_WHITE)
        text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        self.screen.blit(text, text_rect)
        
        # Draw "Press R to Restart" text
        text = self.font_small.render("Press R to Restart", True, COLOR_TEXT)
        text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20))
        self.screen.blit(text, text_rect)


def main():
    """
    Entry point of the program.
    
    Creates the game and starts the main loop.
    """
    game = TetrisGame()
    game.run()


# This ensures main() only runs when this file is executed directly
if __name__ == "__main__":
    main()

