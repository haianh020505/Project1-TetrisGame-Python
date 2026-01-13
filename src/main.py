"""
Tetris Game - Điểm Khởi Đầu Chính

Đây là file chính chạy game Tetris.

Bao gồm:
- Vòng lặp game (cập nhật và vẽ)
- Xử lý đầu vào
- Render tất cả các phần tử hình ảnh
"""

import pygame
import sys
from config import *
from game import GameState
from tetromino import TetrominoType


class TetrisGame:
    """
    Class game chính xử lý vòng lặp game và rendering.
    """
    
    def __init__(self):
        """Khởi tạo pygame và tạo cửa sổ game"""
        pygame.init()
        
        # Tạo cửa sổ game
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Tetris")
        
        # Tạo đồng hồ để kiểm soát tốc độ khung hình
        self.clock = pygame.time.Clock()
        
        # Tạo font cho render văn bản
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 32)
        self.font_small = pygame.font.Font(None, 24)
        self.font_tiny = pygame.font.Font(None, 20)
        
        # Tạo trạng thái game
        self.game_state = GameState()
        
        # Hệ thống đầu vào DAS/ARR (Delayed Auto Shift / Auto Repeat Rate)
        self.left_das_timer = 0.0      # Bộ đếm DAS cho phím trái
        self.right_das_timer = 0.0     # Bộ đếm DAS cho phím phải
        self.left_key_held = False     # Phím trái có đang được giữ không?
        self.right_key_held = False    # Phím phải có đang được giữ không?
        self.left_in_arr = False       # Phím trái có ở chế độ lặp lại tự động không?
        self.right_in_arr = False      # Phím phải có ở chế độ lặp lại tự động không?
        
        self.last_frame_time = pygame.time.get_ticks() / 1000.0

    def run(self):
        """
        Vòng lặp game chính.
        
        Vòng lặp này:
        1. Xử lý đầu vào từ người chơi
        2. Cập nhật trạng thái game
        3. Vẽ mọi thứ lên màn hình
        4. Lặp lại 60 lần mỗi giây
        """
        running = True
        
        while running:
            # Tính thời gian từ khung hình cuối (delta time)
            current_time = pygame.time.get_ticks() / 1000.0
            delta_time = current_time - self.last_frame_time
            self.last_frame_time = current_time
            
            # Xử lý sự kiện (đầu vào bàn phím, đóng cửa sổ, v.v.)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    # Lưu điểm cao trước khi thoát (ngăn mất dữ liệu)
                    if self.game_state.score > self.game_state.high_score:
                        self.game_state.save_high_score(self.game_state.score)
                    running = False
                
                # Xử lý phím nhấn (hành động một lần)
                if event.type == pygame.KEYDOWN:
                    if not self.game_state.game_over and self.game_state.state == GameState.STATE_PLAYING:
                        # Xoay
                        if event.key == pygame.K_UP or event.key == pygame.K_x:
                            self.game_state.rotate_clockwise()
                        elif event.key == pygame.K_z:
                            self.game_state.rotate_counterclockwise()
                        
                        # Rơi nhanh
                        elif event.key == pygame.K_SPACE:
                            self.game_state.hard_drop()
                        
                        # Giữ mảnh
                        elif event.key == pygame.K_c:
                            self.game_state.hold_piece()
                        
                        # Di chuyển Trái/Phải - phản hồi ngay lập tức khi nhấn phím
                        elif event.key == pygame.K_LEFT:
                            self.game_state.move_left()
                            self.left_key_held = True
                            self.left_das_timer = 0.0
                            self.left_in_arr = False
                        
                        elif event.key == pygame.K_RIGHT:
                            self.game_state.move_right()
                            self.right_key_held = True
                            self.right_das_timer = 0.0
                            self.right_in_arr = False
                    
                    # Khởi động lại (hoạt động ngay cả khi game over)
                    if event.key == pygame.K_r:
                        self.game_state.reset()
                    
                    # Thoát
                    if event.key == pygame.K_ESCAPE:
                        # Lưu điểm cao trước khi thoát (ngăn mất dữ liệu)
                        if self.game_state.score > self.game_state.high_score:
                            self.game_state.save_high_score(self.game_state.score)
                        running = False
                
                # Xử lý phím thả (reset bộ đếm DAS/ARR)
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_LEFT:
                        self.left_key_held = False
                        self.left_das_timer = 0.0
                        self.left_in_arr = False
                    
                    elif event.key == pygame.K_RIGHT:
                        self.right_key_held = False
                        self.right_das_timer = 0.0
                        self.right_in_arr = False
            
            # Xử lý di chuyển liên tục (hệ thống DAS/ARR cho phím được giữ)
            if not self.game_state.game_over and self.game_state.state == GameState.STATE_PLAYING:
                keys = pygame.key.get_pressed()
                
                # Di chuyển trái với DAS/ARR
                if self.left_key_held and keys[pygame.K_LEFT]:
                    self.left_das_timer += delta_time
                    
                    # Kiểm tra xem đã qua độ trễ DAS chưa (bắt đầu lặp lại tự động)
                    if not self.left_in_arr and self.left_das_timer >= DAS_DELAY:
                        self.left_in_arr = True
                        self.left_das_timer = 0.0
                    
                    # Nếu ở chế độ lặp lại tự động, di chuyển với tốc độ ARR
                    if self.left_in_arr and self.left_das_timer >= ARR_DELAY:
                        self.game_state.move_left()
                        self.left_das_timer = 0.0
                
                # Di chuyển phải với DAS/ARR
                if self.right_key_held and keys[pygame.K_RIGHT]:
                    self.right_das_timer += delta_time
                    
                    # Kiểm tra xem đã qua độ trễ DAS chưa (bắt đầu lặp lại tự động)
                    if not self.right_in_arr and self.right_das_timer >= DAS_DELAY:
                        self.right_in_arr = True
                        self.right_das_timer = 0.0
                    
                    # Nếu ở chế độ lặp lại tự động, di chuyển với tốc độ ARR
                    if self.right_in_arr and self.right_das_timer >= ARR_DELAY:
                        self.game_state.move_right()
                        self.right_das_timer = 0.0
                
                # Kiểm tra xem rơi chậm có đang hoạt động không
                soft_drop = keys[pygame.K_DOWN]
                
                # Cập nhật trạng thái game
                self.game_state.update(delta_time, soft_drop)
            else:
                # Trong khi hoạt ảnh, chỉ cập nhật không có đầu vào
                self.game_state.update(delta_time, False)
            
            # Vẽ mọi thứ
            self.draw()
            
            # Cập nhật màn hình và giới hạn ở 60 FPS
            pygame.display.flip()
            self.clock.tick(60)
        
        pygame.quit()
        sys.exit()

    def draw(self):
        """Vẽ tất cả các phần tử game lên màn hình"""
        # Xóa màn hình với màu nền
        self.screen.fill(COLOR_BACKGROUND)
        
        # Vẽ lưới game và các mảnh
        self.draw_grid()
        self.draw_locked_pieces()
        self.draw_ghost_piece()
        self.draw_current_piece()
        
        # Vẽ UI (điểm, mảnh tiếp theo, v.v.)
        self.draw_ui()
        
        # Vẽ màn hình game over nếu cần
        if self.game_state.game_over:
            self.draw_game_over()

    def draw_grid(self):
        """
        Vẽ lưới game (các đường nền).
        
        Điều này cho người chơi thấy vị trí của mỗi ô khối.
        """
        # Vẽ các ô lưới
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                px = GRID_OFFSET_X + x * BLOCK_SIZE
                py = GRID_OFFSET_Y + y * BLOCK_SIZE
                
                # Vẽ viền ô
                pygame.draw.rect(self.screen, COLOR_GRID, 
                               (px, py, BLOCK_SIZE, BLOCK_SIZE), 1)
        
        # Vẽ viền xung quanh lưới
        border_rect = pygame.Rect(
            GRID_OFFSET_X - 2,
            GRID_OFFSET_Y - 2,
            GRID_WIDTH * BLOCK_SIZE + 4,
            GRID_HEIGHT * BLOCK_SIZE + 4
        )
        pygame.draw.rect(self.screen, COLOR_TEXT, border_rect, 2)

    def draw_locked_pieces(self):
        """
        Vẽ tất cả các mảnh đã khóa trên lưới.
        
        Bao gồm hiệu ứng hoạt ảnh xóa hàng.
        """
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                color = self.game_state.grid[y][x]
                
                if color is not None:
                    px = GRID_OFFSET_X + x * BLOCK_SIZE
                    py = GRID_OFFSET_Y + y * BLOCK_SIZE
                    
                    # Kiểm tra xem hàng này có đang được xóa không (hoạt ảnh)
                    if (self.game_state.state == GameState.STATE_LINE_CLEAR_ANIMATION and 
                        y in self.game_state.lines_being_cleared):
                        
                        # Tính tiến trình hoạt ảnh (0.0 đến 1.0)
                        progress = self.game_state.line_clear_timer / LINE_CLEAR_ANIMATION
                        
                        # Tạo hiệu ứng mờ dần và co lại
                        alpha = int(255 * (1.0 - progress))
                        shrink = progress * (BLOCK_SIZE - 2) * 0.5
                        size = (BLOCK_SIZE - 2) - (progress * (BLOCK_SIZE - 2))
                        
                        # Tạo surface bán trong suốt cho hoạt ảnh
                        surf = pygame.Surface((int(size), int(size)))
                        surf.set_alpha(alpha)
                        surf.fill(color)
                        
                        # Vẽ khối co lại
                        self.screen.blit(surf, (px + 1 + shrink, py + 1 + shrink))
                        
                        # Vẽ viền mờ dần
                        outline_surf = pygame.Surface((int(size + 2), int(size + 2)))
                        outline_surf.set_alpha(alpha)
                        outline_surf.fill(COLOR_BACKGROUND)
                        outline_rect = outline_surf.get_rect()
                        pygame.draw.rect(outline_surf, COLOR_WHITE, outline_rect, 2)
                        self.screen.blit(outline_surf, (px + shrink, py + shrink))
                    else:
                        # Rendering bình thường
                        # Vẽ khối đầy
                        pygame.draw.rect(self.screen, color, 
                                       (px + 1, py + 1, BLOCK_SIZE - 2, BLOCK_SIZE - 2))
                        # Vẽ viền trắng
                        pygame.draw.rect(self.screen, COLOR_WHITE,
                                       (px, py, BLOCK_SIZE, BLOCK_SIZE), 2)

    def draw_ghost_piece(self):
        """
        Vẽ mảnh ma (bóng cho thấy mảnh sẽ rơi ở đâu).
        
        Điều này giúp người chơi thấy mảnh của họ sẽ đi đâu.
        """
        ghost_y = self.game_state.calculate_ghost_y()
        blocks = self.game_state.current_piece.get_blocks()
        color = self.game_state.current_piece.get_color()
        
        # Tính offset dọc cho mảnh ma
        y_offset = ghost_y - self.game_state.current_piece.y
        
        for x, y in blocks:
            new_y = y + y_offset
            if new_y >= 0:
                px = GRID_OFFSET_X + x * BLOCK_SIZE
                py = GRID_OFFSET_Y + new_y * BLOCK_SIZE
                
                # Tạo surface bán trong suốt
                surf = pygame.Surface((BLOCK_SIZE - 2, BLOCK_SIZE - 2))
                surf.set_alpha(COLOR_GHOST_ALPHA)
                surf.fill(color)
                
                # Vẽ khối ma
                self.screen.blit(surf, (px + 1, py + 1))
                
                # Vẽ viền ma
                pygame.draw.rect(self.screen, (*color, COLOR_GHOST_ALPHA),
                               (px, py, BLOCK_SIZE, BLOCK_SIZE), 1)

    def draw_current_piece(self):
        """Vẽ mảnh đang rơi hiện tại"""
        blocks = self.game_state.current_piece.get_blocks()
        color = self.game_state.current_piece.get_color()
        
        for x, y in blocks:
            if y >= 0:  # Chỉ vẽ các khối nhìn thấy được
                px = GRID_OFFSET_X + x * BLOCK_SIZE
                py = GRID_OFFSET_Y + y * BLOCK_SIZE
                
                # Vẽ khối đầy
                pygame.draw.rect(self.screen, color,
                               (px + 1, py + 1, BLOCK_SIZE - 2, BLOCK_SIZE - 2))
                # Vẽ viền trắng
                pygame.draw.rect(self.screen, COLOR_WHITE,
                               (px, py, BLOCK_SIZE, BLOCK_SIZE), 2)

    def draw_ui(self):
        """
        Vẽ bảng giao diện người dùng.
        
        Hiển thị:
        - Điểm số
        - Điểm cao
        - Cấp độ
        - Số hàng đã xóa
        - Xem trước mảnh tiếp theo
        - Xem trước mảnh đã giữ
        - Hướng dẫn điều khiển
        """
        ui_x = UI_OFFSET_X
        ui_y = UI_OFFSET_Y
        
        # Điểm số
        text = self.font_small.render("SCORE", True, COLOR_TEXT)
        self.screen.blit(text, (ui_x, ui_y))
        ui_y += 30
        
        text = self.font_medium.render(str(self.game_state.score), True, COLOR_WHITE)
        self.screen.blit(text, (ui_x, ui_y))
        ui_y += 50
        
        # Điểm cao
        text = self.font_small.render("HIGH SCORE", True, COLOR_TEXT)
        self.screen.blit(text, (ui_x, ui_y))
        ui_y += 30
        
        text = self.font_medium.render(str(self.game_state.high_score), True, COLOR_WHITE)
        self.screen.blit(text, (ui_x, ui_y))
        ui_y += 50
        
        # Cấp độ
        text = self.font_small.render("LEVEL", True, COLOR_TEXT)
        self.screen.blit(text, (ui_x, ui_y))
        ui_y += 30
        
        text = self.font_medium.render(str(self.game_state.level), True, COLOR_WHITE)
        self.screen.blit(text, (ui_x, ui_y))
        ui_y += 50
        
        # Số hàng
        text = self.font_small.render("LINES", True, COLOR_TEXT)
        self.screen.blit(text, (ui_x, ui_y))
        ui_y += 30
        
        text = self.font_medium.render(str(self.game_state.lines_cleared), True, COLOR_WHITE)
        self.screen.blit(text, (ui_x, ui_y))
        ui_y += 50
        
        # Mảnh tiếp theo
        text = self.font_small.render("NEXT", True, COLOR_TEXT)
        self.screen.blit(text, (ui_x, ui_y))
        ui_y += 30
        
        self.draw_preview_piece(self.game_state.next_piece_type, ui_x, ui_y)
        ui_y += 120
        
        # Mảnh đã giữ
        text = self.font_small.render("HOLD", True, COLOR_TEXT)
        self.screen.blit(text, (ui_x, ui_y))
        ui_y += 30
        
        if self.game_state.held_piece_type is not None:
            self.draw_preview_piece(self.game_state.held_piece_type, ui_x, ui_y)
        ui_y += 120
        
        # Điều khiển
        text = self.font_tiny.render("CONTROLS", True, COLOR_TEXT)
        self.screen.blit(text, (ui_x, ui_y))
        ui_y += 25
        
        controls = [
            "← → Di chuyển",
            "↓ Rơi chậm",
            "Space Rơi nhanh",
            "Z/X Xoay",
            "C Giữ",
            "R Khởi động lại"
        ]
        
        for control in controls:
            text = self.font_tiny.render(control, True, COLOR_TEXT)
            self.screen.blit(text, (ui_x, ui_y))
            ui_y += 20

    def draw_preview_piece(self, piece_type, x, y):
        """
        Vẽ xem trước một mảnh (cho màn hình KẾ TIẾP và ĐÃ GIỮ).
        
        Args:
            piece_type: Loại mảnh cần xem trước
            x, y: Vị trí để vẽ xem trước
        """
        shape = TetrominoType.get_shape(piece_type)
        color = TetrominoType.get_color(piece_type)
        preview_size = 20
        
        for i in range(len(shape)):
            for j in range(len(shape[i])):
                if shape[i][j] == 1:
                    px = x + j * preview_size
                    py = y + i * preview_size
                    
                    # Vẽ khối
                    pygame.draw.rect(self.screen, color,
                                   (px + 1, py + 1, preview_size - 2, preview_size - 2))
                    pygame.draw.rect(self.screen, COLOR_WHITE,
                                   (px, py, preview_size, preview_size), 1)

    def draw_game_over(self):
        """Vẽ lớp phủ game over"""
        # Vẽ lớp phủ bán trong suốt
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        # Vẽ chữ "GAME OVER"
        text = self.font_large.render("GAME OVER", True, COLOR_WHITE)
        text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        self.screen.blit(text, text_rect)
        
        # Vẽ chữ "Nhấn R để Khởi động lại"
        text = self.font_small.render("PRESS R TO RESTART", True, COLOR_TEXT)
        text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20))
        self.screen.blit(text, text_rect)


def main():
    """
    Điểm khởi đầu của chương trình.
    
    Tạo game và bắt đầu vòng lặp chính.
    """
    game = TetrisGame()
    game.run()


# Điều này đảm bảo main() chỉ chạy khi file này được thực thi trực tiếp
if __name__ == "__main__":
    main()

