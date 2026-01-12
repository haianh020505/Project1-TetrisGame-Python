import random
from config import *


class TetrominoType:
    I = 'I'  # Mảnh đường thẳng
    O = 'O'  # Mảnh hình vuông
    T = 'T'  # Mảnh hình chữ T
    S = 'S'  # Mảnh hình chữ S
    Z = 'Z'  # Mảnh hình chữ Z
    J = 'J'  # Mảnh hình chữ J
    L = 'L'  # Mảnh hình chữ L

    @staticmethod
    def all_types():
        """Trả về danh sách tất cả 7 loại mảnh"""
        return [TetrominoType.I, TetrominoType.O, TetrominoType.T,
                TetrominoType.S, TetrominoType.Z, TetrominoType.J,
                TetrominoType.L]

    @staticmethod
    def get_color(piece_type):
        """Trả về màu sắc cho một loại mảnh nhất định"""
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
        Trả về ma trận hình dạng cho một loại mảnh nhất định.
        
        Mỗi hình dạng là một lưới 4x4 trong đó:
        - 0 đại diện cho không gian trống
        - 1 đại diện cho một khối đầy
        
        Điều này giúp dễ dàng xoay và kiểm tra va chạm.
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
    Đại diện cho một mảnh tetromino đơn có thể di chuyển và xoay.
    
    Thuộc tính:
        piece_type: Loại mảnh (I, O, T, S, Z, J, L)
        shape: Lưới 4x4 đại diện cho mảnh
        x, y: Vị trí trên lưới game
        rotation: Trạng thái xoay hiện tại (0, 1, 2, hoặc 3)
    """
    
    def __init__(self, piece_type):
        """
        Tạo một mảnh tetromino mới.
        
        Args:
            piece_type: Một trong các hằng số TetrominoType
        """
        self.piece_type = piece_type
        self.shape = TetrominoType.get_shape(piece_type)
        
        # Vị trí bắt đầu: giữa trên cùng của lưới
        self.x = GRID_WIDTH // 2 - 2
        self.y = 0
        self.rotation = 0

    def get_color(self):
        """Trả về màu sắc của mảnh này"""
        return TetrominoType.get_color(self.piece_type)

    def get_blocks(self):
        """
        Trả về danh sách tọa độ (x, y) cho tất cả các khối đầy trong mảnh.
        
        Hữu ích cho:
        - Vẽ mảnh
        - Kiểm tra va chạm
        - Khóa mảnh vào lưới
        
        Returns:
            Danh sách các tuple (x, y) đại diện cho vị trí khối
        """
        blocks = []
        for i in range(len(self.shape)):
            for j in range(len(self.shape[i])):
                if self.shape[i][j] == 1:
                    # Thêm vị trí mảnh để lấy tọa độ lưới thực tế
                    blocks.append((self.x + j, self.y + i))
        return blocks

    def rotate_clockwise(self):
        """
        Xoay mảnh 90 độ theo chiều kim đồng hồ.
        
        Mảnh O không xoay (nó là hình vuông).
        
        Thuật toán xoay:
        - Lấy chuyển vị của ma trận
        - Đảo ngược mỗi hàng
        """
        # Mảnh O không xoay
        if self.piece_type == TetrominoType.O:
            return

        n = len(self.shape)
        # Tạo hình dạng đã xoay mới
        rotated = [[0 for _ in range(n)] for _ in range(n)]
        
        # Xoay 90 độ theo chiều kim đồng hồ
        for i in range(n):
            for j in range(n):
                rotated[j][n - 1 - i] = self.shape[i][j]
        
        self.shape = rotated
        self.rotation = (self.rotation + 1) % 4

    def rotate_counterclockwise(self):
        """
        Xoay mảnh 90 độ ngược chiều kim đồng hồ.
        
        Tương tự như xoay cùng chiều nhưng theo hướng ngược lại.
        """
        # Mảnh O không xoay
        if self.piece_type == TetrominoType.O:
            return

        n = len(self.shape)
        # Tạo hình dạng đã xoay mới
        rotated = [[0 for _ in range(n)] for _ in range(n)]
        
        # Xoay 90 độ ngược chiều kim đồng hồ
        for i in range(n):
            for j in range(n):
                rotated[n - 1 - j][i] = self.shape[i][j]
        
        self.shape = rotated
        self.rotation = (self.rotation + 3) % 4

    def copy(self):
        """
        Tạo một bản sao của mảnh này.
        
        Được sử dụng để kiểm tra xoay và di chuyển mà không
        ảnh hưởng đến mảnh gốc.
        """
        new_piece = Tetromino(self.piece_type)
        new_piece.shape = [row[:] for row in self.shape]
        new_piece.x = self.x
        new_piece.y = self.y
        new_piece.rotation = self.rotation
        return new_piece


class BagRandomizer:
    """
    Triển khai hệ thống ngẫu nhiên túi 7 mảnh.
    
    Đây là phương pháp ngẫu nhiên Tetris chuẩn:
    - Đặt tất cả 7 mảnh vào một túi
    - Xáo trộn túi
    - Rút mảnh từng cái một
    - Khi trống, đổ đầy và xáo trộn lại
    
    Điều này đảm bảo phân phối công bằng - bạn sẽ không bao giờ phải đợi quá lâu
    mà không thấy một loại mảnh cụ thể.
    """
    
    def __init__(self):
        """Tạo một bộ ngẫu nhiên túi mới với túi đầy đã xáo trộn"""
        self.bag = []
        self.refill_bag()

    def refill_bag(self):
        """Đổ đầy túi với tất cả 7 loại mảnh và xáo trộn"""
        self.bag = TetrominoType.all_types()
        random.shuffle(self.bag)

    def next(self):
        """
        Lấy mảnh tiếp theo từ túi.
        
        Nếu túi trống, nó tự động đổ đầy lại.
        
        Returns:
            Một hằng số TetrominoType
        """
        if len(self.bag) == 0:
            self.refill_bag()
        return self.bag.pop()

    def peek(self):
        """
        Xem mảnh tiếp theo mà không loại bỏ nó khỏi túi.
        
        Được sử dụng để hiển thị xem trước mảnh "KẾ TIẾP".
        
        Returns:
            Một hằng số TetrominoType
        """
        if len(self.bag) == 0:
            self.refill_bag()
        return self.bag[-1]

