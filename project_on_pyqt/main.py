import sys
import datetime
import random
import sqlite3

from PyQt5.QtCore import Qt, QBasicTimer, pyqtSignal
from PyQt5.QtGui import QPainter, QColor
from PyQt5.QtWidgets import QMainWindow, QFrame, QDesktopWidget, QApplication, QPushButton, QWidget, qApp, \
    QTableWidget, QTableWidgetItem, QVBoxLayout, QInputDialog

connection = sqlite3.connect('rating.db')
cursor = connection.cursor()
cursor.execute("""CREATE TABLE IF NOT EXISTS 'results' (
                    'result' int NOT NULL,
                    'name' text NOT NULL,
                    'month' int NOT NULL,
                    'day' int NOT NULL,
                    'hour' int NOT NULL,
                    'minute' int NOT NULL
                    )""")

FIELDS = ('Результат', 'Имя', 'Месяц', 'День', 'Час', 'Минута')


def terminate():
    sys.exit()


class TableWidget(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.table = ResultsTable(self)
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout()
        self.table.setMinimumSize(800, 600)
        main_layout.addWidget(self.table)
        self.setLayout(main_layout)


class ResultsTable(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.table = QTableWidget()
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.addWidget(self.table)
        self.setLayout(layout)
        results = list(cursor.execute("""SELECT * FROM results ORDER BY result DESC""").fetchmany(100))
        if len(results) > 0:
            self.table.setColumnCount(len(results[0]))
        self.table.setHorizontalHeaderLabels(FIELDS)
        self.table.setRowCount(0)
        for i, row in enumerate(results):
            self.table.setRowCount(self.table.rowCount() + 1)
            for j, element in enumerate(row):
                item = QTableWidgetItem(str(element))
                self.table.setItem(i, j, item)

        self.table.resizeColumnsToContents()


class Tetris(QMainWindow):
    EXIT_CODE_REBOOT = -123456789

    def __init__(self):
        super().__init__()
        self.board = Board(self)
        self.statusbar = self.statusBar()
        self.rating = ResultsTable(self)
        self.play_button = QPushButton('Play', self)
        self.rating_button = QPushButton('Rating', self)
        self.exit_button = QPushButton('Exit', self)
        self.table = TableWidget(self)

        self.setup_ui()
        self.show()

    def setup_ui(self):
        self.resize(420, 100)
        self.center()
        self.setWindowTitle('Tetris')

        self.play_button.clicked.connect(self.play)
        self.play_button.move(20, 35)
        self.rating_button.clicked.connect(self.table.show)
        self.rating_button.move(160, 35)
        self.exit_button.clicked.connect(terminate)
        self.exit_button.move(300, 35)

    def center(self):
        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move(int((screen.width() - size.width()) / 2), int((screen.height() - size.height()) / 2))

    def play(self):
        self.play_button.hide()
        self.rating_button.hide()
        self.exit_button.hide()
        self.setCentralWidget(self.board)
        self.board.msg_statusbar[str].connect(self.statusbar.showMessage)
        self.resize(400, 700)
        self.center()
        self.board.start()


class Board(QFrame):
    msg_statusbar = pyqtSignal(str)
    board_width = 10
    board_height = 22
    speed = 300

    def __init__(self, parent):
        super().__init__(parent)
        self.timer = QBasicTimer()
        self.cur_piece = Shape()
        self.is_need_new_piece = False
        self.cur_x = 0
        self.cur_y = 0
        self.num_lines_removed = 0
        self.board = []

        self.setFocusPolicy(Qt.StrongFocus)
        self.is_started = False
        self.is_paused = False
        self.clear_board()

    def get_shape_at(self, x, y):
        return self.board[(y * Board.board_width) + x]

    def set_shape_at(self, x, y, shape):
        self.board[(y * Board.board_width) + x] = shape

    def square_width(self):
        return self.contentsRect().width() // Board.board_width

    def square_height(self):
        return self.contentsRect().height() // Board.board_height

    def start(self):
        if self.is_paused:
            return

        self.is_started = True
        self.is_need_new_piece = False
        self.num_lines_removed = 0
        self.clear_board()

        self.msg_statusbar.emit(str(self.num_lines_removed))

        self.new_piece()
        self.timer.start(Board.speed, self)

    def pause(self):
        if not self.is_started:
            return

        self.is_paused = not self.is_paused

        if self.is_paused:
            self.timer.stop()
            self.msg_statusbar.emit("paused")
        else:
            self.timer.start(Board.speed, self)
            self.msg_statusbar.emit(str(self.num_lines_removed))

        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        rect = self.contentsRect()
        board_top = rect.bottom() - Board.board_height * self.square_height()

        for i in range(Board.board_height):
            for j in range(Board.board_width):
                shape = self.get_shape_at(j, Board.board_height - i - 1)
                if shape != Figure.no_shape:
                    self.draw_square(painter, rect.left() + j * self.square_width(),
                                     board_top + i * self.square_height(), shape)

        if self.cur_piece.get_shape() != Figure.no_shape:
            for i in range(4):
                x = self.cur_x + self.cur_piece.get_x(i)
                y = self.cur_y - self.cur_piece.get_y(i)
                self.draw_square(painter, rect.left() + x * self.square_width(), board_top +
                                 (Board.board_height - y - 1) * self.square_height(), self.cur_piece.get_shape())

    def keyPressEvent(self, event):
        key = event.key()

        if key == Qt.Key_E:
            qApp.exit(Tetris.EXIT_CODE_REBOOT)

        if not self.is_started or self.cur_piece.get_shape() == Figure.no_shape:
            super(Board, self).keyPressEvent(event)
            return

        if key == Qt.Key_P:
            self.pause()
            return

        if self.is_paused:
            return

        elif key == Qt.Key_Left:
            self.try_move(self.cur_piece, self.cur_x - 1, self.cur_y)

        elif key == Qt.Key_Right:
            self.try_move(self.cur_piece, self.cur_x + 1, self.cur_y)

        elif key == Qt.Key_Up:
            self.try_move(self.cur_piece.rotate(), self.cur_x, self.cur_y)

        elif key == Qt.Key_Down:
            self.one_line_down()

        elif key == Qt.Key_Space:
            self.drop_down()

        else:
            super(Board, self).keyPressEvent(event)

    def timerEvent(self, event):
        if event.timerId() == self.timer.timerId():
            if self.is_need_new_piece:
                self.is_need_new_piece = False
                self.new_piece()
            else:
                self.one_line_down()

        else:
            super(Board, self).timerEvent(event)

    def clear_board(self):
        for i in range(Board.board_height * Board.board_width):
            self.board.append(Figure.no_shape)

    def drop_down(self):
        new_y = self.cur_y

        while new_y > 0:
            if not self.try_move(self.cur_piece, self.cur_x, new_y - 1):
                break
            new_y -= 1

        self.piece_dropped()

    def one_line_down(self):
        if not self.try_move(self.cur_piece, self.cur_x, self.cur_y - 1):
            self.piece_dropped()

    def piece_dropped(self):
        for i in range(4):
            x = self.cur_x + self.cur_piece.get_x(i)
            y = self.cur_y - self.cur_piece.get_y(i)
            self.set_shape_at(x, y, self.cur_piece.get_shape())

        self.remove_full_lines()

        if not self.is_need_new_piece:
            self.new_piece()

    def remove_full_lines(self):
        num_full_lines = 0
        rows_to_remove = []

        for i in range(Board.board_height):
            n = 0
            for j in range(Board.board_width):
                if not self.get_shape_at(j, i) == Figure.no_shape:
                    n = n + 1

            if n == 10:
                rows_to_remove.append(i)

        rows_to_remove.reverse()

        for m in rows_to_remove:
            for k in range(m, Board.board_height):
                for g in range(Board.board_width):
                    self.set_shape_at(g, k, self.get_shape_at(g, k + 1))

        num_full_lines += len(rows_to_remove)

        if num_full_lines > 0:
            self.num_lines_removed = self.num_lines_removed + num_full_lines
            self.msg_statusbar.emit(str(self.num_lines_removed))
            self.is_need_new_piece = True
            self.cur_piece.set_shape(Figure.no_shape)
            self.update()

    def new_piece(self):
        self.cur_piece.set_random_shape()
        self.cur_x = Board.board_width // 2 + 1
        self.cur_y = Board.board_height - 1 + self.cur_piece.min_y()

        if not self.try_move(self.cur_piece, self.cur_x, self.cur_y):
            self.cur_piece.set_shape(Figure.no_shape)
            self.timer.stop()
            self.is_started = False
            self.msg_statusbar.emit("Game over")
            self.add_to_rating(self.num_lines_removed)
            qApp.exit(Tetris.EXIT_CODE_REBOOT)

    def try_move(self, new_piece, new_x, new_y):
        for i in range(4):
            x = new_x + new_piece.get_x(i)
            y = new_y - new_piece.get_y(i)

            if x < 0 or x >= Board.board_width or y < 0 or y >= Board.board_height:
                return False

            if self.get_shape_at(x, y) != Figure.no_shape:
                return False

        self.cur_piece = new_piece
        self.cur_x = new_x
        self.cur_y = new_y
        self.update()
        return True

    def draw_square(self, painter, x, y, shape):
        color_table = [0x000000, 0xCC6666, 0x66CC66, 0x6666CC, 0xCCCC66, 0xCC66CC, 0x66CCCC, 0xDAAA00]

        color = QColor(color_table[shape])
        painter.fillRect(x + 1, y + 1, self.square_width() - 2,
                         self.square_height() - 2, color)

        painter.setPen(color.lighter())
        painter.drawLine(x, y + self.square_height() - 1, x, y)
        painter.drawLine(x, y, x + self.square_width() - 1, y)

        painter.setPen(color.darker())
        painter.drawLine(x + 1, y + self.square_height() - 1,
                         x + self.square_width() - 1, y + self.square_height() - 1)
        painter.drawLine(x + self.square_width() - 1, y + self.square_height() - 1,
                         x + self.square_width() - 1, y + 1)

    def add_to_rating(self, result):
        name, ok_pressed = QInputDialog.getText(self, 'name', 'Введите имя для рейтинга')
        if ok_pressed and name != "":
            now = datetime.datetime.now()
            cursor.execute("""INSERT INTO results VALUES(?, ?, ?, ?, ?, ?)""", (result, name, now.month, now.day,
                                                                                now.hour, now.minute))
            connection.commit()


class Figure(object):
    no_shape = 0
    z_shape = 1
    s_shape = 2
    line_shape = 3
    t_shape = 4
    square_shape = 5
    l_shape = 6
    mirrored_l_shape = 7


class Shape(object):
    coords_table = (
        ((0, 0),     (0, 0),     (0, 0),     (0, 0)),
        ((0, -1),    (0, 0),     (-1, 0),    (-1, 1)),
        ((0, -1),    (0, 0),     (1, 0),     (1, 1)),
        ((0, -1),    (0, 0),     (0, 1),     (0, 2)),
        ((-1, 0),    (0, 0),     (1, 0),     (0, 1)),
        ((0, 0),     (1, 0),     (0, 1),     (1, 1)),
        ((-1, -1),   (0, -1),    (0, 0),     (0, 1)),
        ((1, -1),    (0, -1),    (0, 0),     (0, 1))
    )

    def __init__(self):
        self.coords = [[0, 0] for _ in range(4)]
        self.piece_shape = Figure.no_shape
        self.set_shape(Figure.no_shape)

    def get_shape(self):
        return self.piece_shape

    def set_shape(self, shape):
        table = Shape.coords_table[shape]

        for i in range(4):
            for j in range(2):
                self.coords[i][j] = table[i][j]

        self.piece_shape = shape

    def set_random_shape(self):
        self.set_shape(random.randint(1, 7))

    def get_x(self, index):
        return self.coords[index][0]

    def get_y(self, index):
        return self.coords[index][1]

    def set_x(self, index, x):
        self.coords[index][0] = x

    def set_y(self, index, y):
        self.coords[index][1] = y

    def min_y(self):
        m = self.coords[0][1]

        for i in range(4):
            m = min(m, self.coords[i][1])

        return m

    def rotate(self):
        if self.piece_shape == Figure.square_shape:
            return self

        result = Shape()
        result.piece_shape = self.piece_shape

        for i in range(4):
            result.set_x(i, self.get_y(i))
            result.set_y(i, -self.get_x(i))

        return result


if __name__ == '__main__':
    current_exit_code = Tetris.EXIT_CODE_REBOOT
    while current_exit_code == Tetris.EXIT_CODE_REBOOT:
        app = QApplication(sys.argv)
        tetris = Tetris()
        tetris.show()
        current_exit_code = app.exec_()
        app = None
