"""
Trạng thái và Logic Game

File này chứa logic game chính bao gồm:
- Quản lý bảng (lưới các khối đã khóa)
- Phát hiện va chạm
- Di chuyển và xoay mảnh
- Xóa hàng
- Hệ thống tính điểm
- Quản lý trạng thái game
"""

import pygame
import os
from config import *
from config import get_gravity_speed
from tetromino import Tetromino, BagRandomizer


class GameState:
    """
    Quản lý trạng thái hoàn chỉnh của game Tetris.
    
    Bao gồm:
    - Lưới game (các mảnh đã khóa)
    - Mảnh đang rơi hiện tại
    - Xem trước mảnh tiếp theo
    - Mảnh đang giữ
    - Điểm số, cấp độ, số hàng đã xóa
    - Trạng thái kết thúc game
    """
    
    # Các trạng thái game cho hoạt ảnh
    STATE_PLAYING = 0
    STATE_LINE_CLEAR_ANIMATION = 1
    
    def __init__(self):
        """Khởi tạo game mới"""
        # Tạo lưới (danh sách 2D các màu, None nghĩa là ô trống)
        self.grid = [[None for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        
        # Khởi tạo bộ tạo mảnh ngẫu nhiên (hệ thống túi 7 mảnh)
        self.bag_randomizer = BagRandomizer()
        
        # Tạo mảnh đầu tiên và xem trước mảnh tiếp theo
        self.current_piece = Tetromino(self.bag_randomizer.next())
        self.next_piece_type = self.bag_randomizer.peek()
        
        # Hệ thống giữ mảnh
        self.held_piece_type = None
        self.can_hold = True  # Chỉ có thể giữ một lần mỗi mảnh
        
        # Tính điểm và tiến độ
        self.score = 0
        self.high_score = self.load_high_score()
        self.level = 1
        self.lines_cleared = 0
        self.combo_count = -1  # Bộ đếm combo: -1 nghĩa là không có combo đang hoạt động
        
        # Trạng thái game
        self.game_over = False
        self.state = self.STATE_PLAYING
        
        # Bộ đếm thời gian cho cơ chế game
        self.fall_timer = 0.0          # Bộ đếm cho mảnh rơi tự động
        self.lock_timer = 0.0          # Bộ đếm trước khi mảnh khóa ở đáy
        self.is_on_ground = False      # Mảnh hiện tại có chạm đất không?
        
        # Giới hạn reset độ trễ khóa (ngăn chặn lợi dụng xoay vô hạn)
        self.lock_reset_count = 0      # Đếm số lần độ trễ khóa được reset
        self.max_lock_resets = 15      # Số lần reset tối đa trước khi buộc khóa
        
        # Hoạt ảnh xóa hàng
        self.line_clear_timer = 0.0
        self.lines_being_cleared = []  # Danh sách chỉ số hàng đang được xóa

    def update(self, delta_time, soft_drop):
        """
        Cập nhật trạng thái game mỗi khung hình.
        
        Args:
            delta_time: Thời gian đã trôi qua kể từ khung hình cuối (tính bằng giây)
            soft_drop: True nếu người chơi đang giữ phím mũi tên xuống
        """
        if self.game_over:
            return

        # Xử lý hoạt ảnh xóa hàng
        if self.state == self.STATE_LINE_CLEAR_ANIMATION:
            self.line_clear_timer += delta_time
            
            # Khi hoạt ảnh kết thúc, thực sự xóa các hàng
            if self.line_clear_timer >= LINE_CLEAR_ANIMATION:
                self.complete_line_clear()
                self.state = self.STATE_PLAYING
                self.line_clear_timer = 0.0
                self.lines_being_cleared = []
            return

        # Tính tốc độ rơi dựa trên cấp độ và rơi chậm
        if soft_drop:
            fall_speed = FAST_DROP_SPEED
        else:
            # Sử dụng đường cong trọng lực Tetris chuẩn
            fall_speed = get_gravity_speed(self.level)
        
        self.fall_timer += delta_time

        # Kiểm tra xem mảnh có ở trên mặt đất không
        was_on_ground = self.is_on_ground
        self.is_on_ground = self.check_collision(0, 1)

        # Nếu ở trên mặt đất, bắt đầu bộ đếm khóa
        if self.is_on_ground:
            self.lock_timer += delta_time
            # Khóa mảnh sau độ trễ HOẶC nếu đạt số lần reset tối đa
            if self.lock_timer >= LOCK_DELAY or self.lock_reset_count >= self.max_lock_resets:
                self.lock_piece()
        else:
            self.lock_timer = 0.0
            self.lock_reset_count = 0  # Reset bộ đếm khi mảnh đang lơ lửng

        # Làm mảnh rơi tự động
        if self.fall_timer >= fall_speed:
            self.fall_timer = 0.0
            if not self.is_on_ground:
                self.current_piece.y += 1
                # Reset bộ đếm reset khóa khi mảnh di chuyển xuống tự nhiên
                self.lock_reset_count = 0
                # Trao điểm cho rơi chậm
                if soft_drop:
                    self.score += SCORE_SOFT_DROP

        # Reset bộ đếm khóa nếu mảnh rời khỏi mặt đất (nhưng giới hạn reset để ngăn xoay vô hạn)
        if was_on_ground and not self.is_on_ground:
            if self.lock_reset_count < self.max_lock_resets:
                self.lock_timer = 0.0
                self.lock_reset_count += 1
            # Nếu đạt số lần reset tối đa, không reset bộ đếm (mảnh sẽ khóa sớm)

    def move_left(self):
        """Thử di chuyển mảnh hiện tại sang trái"""
        if not self.check_collision(-1, 0):
            self.current_piece.x -= 1

    def move_right(self):
        """Thử di chuyển mảnh hiện tại sang phải"""
        if not self.check_collision(1, 0):
            self.current_piece.x += 1

    def rotate_clockwise(self):
        """
        Thử xoay mảnh theo chiều kim đồng hồ.
        
        Nếu xoay trực tiếp thất bại, thử wall kick:
        điều chỉnh nhỏ vị trí có thể làm cho xoay thành công.
        """
        # Tạo mảnh thử nghiệm để thử xoay
        test_piece = self.current_piece.copy()
        test_piece.rotate_clockwise()

        # Thử xoay trực tiếp
        if not self.check_collision_piece(test_piece):
            self.current_piece = test_piece
            return

        # Thử wall kick (điều chỉnh vị trí nhỏ)
        kicks = [(1, 0), (-1, 0), (0, -1), (1, -1), (-1, -1),(-2,0),(2,0)]
        for dx, dy in kicks:
            test_piece.x = self.current_piece.x + dx
            test_piece.y = self.current_piece.y + dy
            if not self.check_collision_piece(test_piece):
                self.current_piece = test_piece
                return

    def rotate_counterclockwise(self):
        """
        Thử xoay mảnh ngược chiều kim đồng hồ.
        
        Tương tự như xoay cùng chiều nhưng theo hướng ngược lại.
        """
        test_piece = self.current_piece.copy()
        test_piece.rotate_counterclockwise()

        # Thử xoay trực tiếp
        if not self.check_collision_piece(test_piece):
            self.current_piece = test_piece
            return

        # Thử wall kick
        kicks = [(1, 0), (-1, 0), (0, -1), (1, -1), (-1, -1),(-2,0),(2,0)]
        for dx, dy in kicks:
            test_piece.x = self.current_piece.x + dx
            test_piece.y = self.current_piece.y + dy
            if not self.check_collision_piece(test_piece):
                self.current_piece = test_piece
                return

    def hard_drop(self):
        """
        Thả mảnh xuống đáy ngay lập tức.
        
        Trao điểm dựa trên khoảng cách rơi.
        """
        ghost_y = self.calculate_ghost_y()
        drop_distance = ghost_y - self.current_piece.y
        
        # Trao điểm cho rơi nhanh
        self.score += drop_distance * SCORE_HARD_DROP
        
        self.current_piece.y = ghost_y
        self.lock_piece()

    def hold_piece(self):
        """
        Giữ mảnh hiện tại để sử dụng sau.
        
        Chỉ có thể giữ một lần mỗi mảnh (cho đến khi nó khóa).
        Nếu đã giữ một mảnh, hoán đổi với nó.
        """
        if not self.can_hold:
            return

        current_type = self.current_piece.piece_type

        if self.held_piece_type is not None:
            # Hoán đổi với mảnh đã giữ
            self.current_piece = Tetromino(self.held_piece_type)
            self.held_piece_type = current_type
        else:
            # Giữ mảnh hiện tại và tạo mảnh tiếp theo
            self.held_piece_type = current_type
            self.spawn_next_piece()

        self.can_hold = False

    def check_collision(self, dx, dy):
        """
        Kiểm tra xem di chuyển mảnh hiện tại theo (dx, dy) có gây va chạm không.
        
        Args:
            dx: Di chuyển ngang
            dy: Di chuyển dọc
            
        Returns:
            True nếu va chạm xảy ra, False nếu không
        """
        blocks = self.current_piece.get_blocks()
        
        for x, y in blocks:
            new_x = x + dx
            new_y = y + dy
            
            # Kiểm tra ranh giới
            if new_x < 0 or new_x >= GRID_WIDTH or new_y >= GRID_HEIGHT:
                return True
            
            # Kiểm tra va chạm với các khối đã khóa (bỏ qua các khối phía trên lưới)
            if new_y >= 0 and self.grid[new_y][new_x] is not None:
                return True
        
        return False

    def check_collision_piece(self, piece):
        """
        Kiểm tra xem một mảnh cụ thể có va chạm với lưới hoặc ranh giới không.
        
        Được sử dụng để kiểm tra xoay.
        
        Args:
            piece: Tetromino cần kiểm tra
            
        Returns:
            True nếu va chạm xảy ra, False nếu không
        """
        blocks = piece.get_blocks()
        
        for x, y in blocks:
            # Kiểm tra ranh giới
            if x < 0 or x >= GRID_WIDTH or y >= GRID_HEIGHT:
                return True
            
            # Kiểm tra va chạm với các khối đã khóa
            if y >= 0 and self.grid[y][x] is not None:
                return True
        
        return False

    def calculate_ghost_y(self):
        """
        Tính toán vị trí mảnh sẽ rơi nếu thả thẳng xuống.
        
        Được sử dụng để hiển thị mảnh ma (xem trước vị trí hạ cánh).
        
        Returns:
            Tọa độ y nơi mảnh sẽ rơi
        """
        ghost_y = self.current_piece.y
        
        # Tạo mảnh thử nghiệm để di chuyển xuống
        test_piece = self.current_piece.copy()
        
        # Tiếp tục di chuyển xuống cho đến khi va chạm
        while not self.check_collision_piece(test_piece):
            ghost_y = test_piece.y
            test_piece.y += 1
        
        return ghost_y

    def lock_piece(self):
        """
        Khóa mảnh hiện tại vào lưới.
        
        Điều này xảy ra khi:
        - Mảnh chạm đáy và độ trễ khóa hết hạn
        - Người chơi thực hiện rơi nhanh
        
        Sau khi khóa:
        1. Thêm các khối mảnh vào lưới
        2. Kiểm tra xóa hàng
        3. Tạo mảnh tiếp theo
        4. Kiểm tra kết thúc game
        """
        blocks = self.current_piece.get_blocks()
        color = self.current_piece.get_color()

        # Thêm các khối mảnh vào lưới
        for x, y in blocks:
            if 0 <= y < GRID_HEIGHT and 0 <= x < GRID_WIDTH:
                self.grid[y][x] = color

        # Kiểm tra các hàng hoàn thành
        self.check_line_clears()
        
        # Reset combo nếu không có hàng nào được xóa
        if not self.lines_being_cleared:
            self.combo_count = -1
        
        # Tạo mảnh tiếp theo
        self.spawn_next_piece()
        
        # Reset khả năng giữ và bộ đếm reset khóa
        self.can_hold = True
        self.lock_timer = 0.0
        self.is_on_ground = False
        self.lock_reset_count = 0  # Reset bộ đếm cho mảnh mới

    def spawn_next_piece(self):
        """
        Tạo mảnh tiếp theo từ túi.
        
        Kiểm tra xem nó có thể tạo không (nếu không, kết thúc game).
        """
        next_type = self.bag_randomizer.next()
        self.current_piece = Tetromino(next_type)
        self.next_piece_type = self.bag_randomizer.peek()
        self.fall_timer = 0.0

        # Kiểm tra kết thúc game (mảnh không thể tạo)
        if self.check_collision_piece(self.current_piece):
            self.game_over = True
            # Cập nhật điểm cao nếu cần
            if self.score > self.high_score:
                self.high_score = self.score
                self.save_high_score(self.high_score)

    def check_line_clears(self):
        """
        Kiểm tra các hàng hoàn thành và bắt đầu hoạt ảnh xóa.
        
        Một hàng hoàn thành khi tất cả các khối trong hàng đều được lấp đầy.
        """
        lines_to_clear = []

        # Kiểm tra từng hàng
        for y in range(GRID_HEIGHT):
            # Kiểm tra xem tất cả các khối trong hàng có được lấp đầy không
            if all(self.grid[y][x] is not None for x in range(GRID_WIDTH)):
                lines_to_clear.append(y)

        # Nếu tìm thấy hàng, bắt đầu hoạt ảnh
        if lines_to_clear:
            self.lines_being_cleared = lines_to_clear
            self.state = self.STATE_LINE_CLEAR_ANIMATION
            self.line_clear_timer = 0.0

    def complete_line_clear(self):
        """
        Thực sự xóa các hàng đã được xóa và cập nhật điểm.
        
        Được gọi sau khi hoạt ảnh xóa hàng kết thúc.
        """
        if not self.lines_being_cleared:
            return

        num_lines = len(self.lines_being_cleared)

        # Xóa các hàng đã được xóa (bắt đầu từ dưới để tránh vấn đề chỉ số)
        for y in sorted(self.lines_being_cleared, reverse=True):
            del self.grid[y]

        # Thêm các hàng trống mới ở trên cùng
        for _ in range(num_lines):
            self.grid.insert(0, [None for _ in range(GRID_WIDTH)])

        # Cập nhật điểm dựa trên số hàng đã xóa
        score_table = {
            1: SCORE_SINGLE,
            2: SCORE_DOUBLE,
            3: SCORE_TRIPLE,
            4: SCORE_TETRIS,
        }
        base_score = score_table.get(num_lines, 0)
        self.score += base_score * self.level

        # Tăng bộ đếm combo và thêm điểm thưởng combo
        self.combo_count += 1
        if self.combo_count > 0:
            combo_bonus = COMBO_BONUS * self.combo_count * self.level
            self.score += combo_bonus

        # Cập nhật bộ đếm số hàng đã xóa
        self.lines_cleared += num_lines

        # Cập nhật cấp độ (mỗi 10 hàng tăng cấp độ)
        self.level = (self.lines_cleared // 10) + 1

        # Cập nhật và lưu điểm cao ngay lập tức (ngăn mất dữ liệu khi thoát)
        if self.score > self.high_score:
            self.high_score = self.score
            self.save_high_score(self.high_score)

    def reset(self):
        """Reset game về trạng thái ban đầu (khởi động lại)"""
        self.__init__()

    def load_high_score(self):
        """
        Tải điểm cao từ file.
        
        Returns:
            Điểm cao đã lưu, hoặc 0 nếu file không tồn tại
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
        Lưu điểm cao vào file.
        
        Args:
            score: Điểm số cần lưu
        """
        try:
            with open(HIGHSCORE_FILE, 'w') as f:
                f.write(str(score))
        except:
            pass

