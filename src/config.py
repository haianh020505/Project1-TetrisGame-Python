"""
Hằng số và Cấu hình cho Game Tetris

File này chứa tất cả các giá trị hằng số được sử dụng trong game:
- Kích thước lưới
- Màu sắc cho từng mảnh tetromino
- Cài đặt thời gian game
- Quy tắc tính điểm
"""
import pygame

# Kích thước lưới (theo đơn vị khối)
GRID_WIDTH = 10   # Chiều rộng 10 khối
GRID_HEIGHT = 20  # Chiều cao 20 khối
BLOCK_SIZE = 30   # Mỗi khối có kích thước 30x30 pixels

# Kích thước màn hình (theo đơn vị pixels)
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 650

# Vị trí của lưới game trên màn hình
GRID_OFFSET_X = 50
GRID_OFFSET_Y = 50

# Vị trí của bảng UI (điểm số, mảnh tiếp theo, v.v.)
UI_OFFSET_X = GRID_OFFSET_X + (GRID_WIDTH * BLOCK_SIZE) + 50
UI_OFFSET_Y = 50

# Thời gian trong game (theo đơn vị giây)
INITIAL_FALL_SPEED = 1.0      # Số giây trước khi mảnh rơi xuống một hàng
FAST_DROP_SPEED = 0.05        # Tốc độ khi giữ phím mũi tên xuống
LOCK_DELAY = 0.5              # Thời gian mảnh ở đáy trước khi khóa
LINE_CLEAR_ANIMATION = 0.2    # Thời lượng hoạt ảnh xóa hàng

# Thời gian đầu vào (hệ thống DAS/ARR cho điều khiển phản hồi nhanh)
DAS_DELAY = 0.15              # Delayed Auto Shift: độ trễ ban đầu trước khi lặp lại tự động (giây)
ARR_DELAY = 0.033             # Auto Repeat Rate: độ trễ giữa các di chuyển lặp lại (giây, ~30 lần/giây)

# Hệ thống tính điểm (điểm được trao khi xóa hàng)
SCORE_SINGLE = 100    # Xóa 1 hàng
SCORE_DOUBLE = 300    # Xóa 2 hàng
SCORE_TRIPLE = 500    # Xóa 3 hàng
SCORE_TETRIS = 800    # Xóa 4 hàng (Tetris!)
SCORE_SOFT_DROP = 1   # Điểm mỗi hàng cho rơi chậm
SCORE_HARD_DROP = 2   # Điểm mỗi hàng cho rơi nhanh

# Màu sắc (định dạng RGB)
# Màu nền và UI
COLOR_BACKGROUND = (25, 25, 30)      # Nền xám đậm
COLOR_GRID = (50, 50, 65)            # Đường lưới
COLOR_TEXT = (230, 230, 230)         # Chữ màu trắng
COLOR_GHOST_ALPHA = 77               # Độ trong suốt cho mảnh ma (0-255)

# Màu sắc Tetromino (mỗi loại mảnh có màu riêng)
COLOR_I = (0, 230, 230)    # Cyan - Mảnh I (đường thẳng)
COLOR_O = (230, 230, 0)    # Vàng - Mảnh O (hình vuông)
COLOR_T = (180, 0, 230)    # Tím - Mảnh T
COLOR_S = (0, 230, 0)      # Xanh lá - Mảnh S
COLOR_Z = (230, 0, 0)      # Đỏ - Mảnh Z
COLOR_J = (0, 0, 230)      # Xanh dương - Mảnh J
COLOR_L = (230, 128, 0)    # Cam - Mảnh L
COLOR_WHITE = (255, 255, 255)  # Trắng cho viền

# File lưu điểm cao
HIGHSCORE_FILE = "highscore.txt"

# Bảng tốc độ trọng lực (đường cong theo hướng dẫn Tetris chuẩn)
# Ánh xạ cấp độ -> tốc độ rơi tính bằng giây
GRAVITY_SPEED_TABLE = {
    1: 1.0,
    2: 0.79,
    3: 0.61,
    4: 0.47,
    5: 0.36,
    6: 0.28,
    7: 0.21,
}

# Tính điểm combo
COMBO_BONUS = 50  # Điểm thưởng cơ bản cho mỗi cấp combo

def get_gravity_speed(level):
    """
    Lấy tốc độ rơi cho một cấp độ nhất định.
    
    Sử dụng đường cong trọng lực Tetris chuẩn, trong đó tốc độ tăng
    theo cấp số nhân với cấp độ. Giới hạn ở 0.1s cho cấp 8 trở lên.
    
    Args:
        level: Cấp độ game hiện tại
        
    Returns:
        Tốc độ rơi tính bằng giây (thời gian giữa các lần rơi tự động)
    """
    if level in GRAVITY_SPEED_TABLE:
        return GRAVITY_SPEED_TABLE[level]
    elif level >= 8:
        return 0.1  # Giới hạn ở rất nhanh cho cấp 8 trở lên
    else:
        # Không nên xảy ra, nhưng fallback về tốc độ cấp 1
        return 1.0

