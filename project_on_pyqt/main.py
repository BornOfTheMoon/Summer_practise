import datetime
import random
import sqlite3
import sys

from PyQt5.QtCore import Qt, QBasicTimer, pyqtSignal
from PyQt5.QtGui import QPainter, QColor
from PyQt5.QtWidgets import QMainWindow, QFrame, QDesktopWidget, QApplication, QPushButton, QDialog, QWidget, qApp, \
    QTableWidget, QTableWidgetItem

connection = sqlite3.connect('rate.db')
cursor = connection.cursor()
cursor.execute("""CREATE TABLE IF NOT EXISTS 'results' (
                    'result' int NOT NULL,
                    'month' int NOT NULL,
                    'day' int NOT NULL,
                    'hour' int NOT NULL,
                    'minute' int NOT NULL
                    )""")


FIELDS = ('Результат', 'Месяц', 'День', 'Час', 'Минута')


def terminate():
    sys.exit()






class ResultsTable(QMainWindow):
    def __init__(self, parent):
        super().__init__(parent)
        self.table = QTableWidget()
        self.setGeometry(200, 100, 500, 600)

    def show_results(self, results):
        for result in results:
            print(result)


def add_to_rate(result):
    now = datetime.datetime.now()
    cursor.execute("""INSERT INTO results VALUES(?, ?, ?, ?, ?)""", (result, now.month, now.day, now.hour, now.minute))
    connection.commit()


class Tetris(QMainWindow):
    EXIT_CODE_REBOOT = -123

    def __init__(self):
        super().__init__()
        self.board = Board(self)
        self.statusbar = self.statusBar()
        self.rate = ResultsTable(self)
        self.play_button = QPushButton('Play', self)
        self.rate_button = QPushButton('Rate', self)
        self.exit_button = QPushButton('Exit', self)

        self.menu_init()
        self.show()

    def menu_init(self):
        self.resize(420, 100)
        self.center()
        self.setWindowTitle('Tetris')

        self.play_button.clicked.connect(self.play)
        self.play_button.move(20, 35)
        self.rate_button.clicked.connect(self.show_rate)
        self.rate_button.move(160, 35)
        self.exit_button.clicked.connect(terminate)
        self.exit_button.move(300, 35)

    def play(self):
        self.play_button.hide()
        self.rate_button.hide()
        self.exit_button.hide()
        self.setCentralWidget(self.board)
        self.board.msg_statusbar[str].connect(self.statusbar.showMessage)
        self.board.start()
        self.resize(400, 700)
        self.center()

    def center(self):
        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move(int((screen.width() - size.width()) / 2), int((screen.height() - size.height()) / 2))

    def show_rate(self):
        results = list(cursor.execute("""SELECT result FROM results ORDER BY result DESC""").fetchmany(50))
        self.rate.show_results(results)
        self.rate.show()


class Board(QFrame):
    msg_statusbar = pyqtSignal(str)
    board_width = 10
    board_height = 22
    speed = 300

    def __init__(self, parent):
        super().__init__(parent)
        self.timer = QBasicTimer()
        self.cur_piece = Shape()
        self.is_waiting_after_line = False
        self.cur_x = 0
        self.cur_y = 0
        self.num_lines_removed = 0
        self.board = []

        self.setFocusPolicy(Qt.StrongFocus)
        self.is_started = False
        self.is_paused = False
        self.is_lose = False
        self.clear_board()

    def shape_at(self, x, y):
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
        self.is_waiting_after_line = False
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
                shape = self.shape_at(j, Board.board_height - i - 1)
                if shape != Tetrominoe.no_shape:
                    self.draw_square(painter, rect.left() + j * self.square_width(),
                                     board_top + i * self.square_height(), shape)

        if self.cur_piece.shape() != Tetrominoe.no_shape:
            for i in range(4):
                x = self.cur_x + self.cur_piece.get_x(i)
                y = self.cur_y - self.cur_piece.get_y(i)
                self.draw_square(painter, rect.left() + x * self.square_width(),
                                 board_top + (Board.board_height - y - 1) * self.square_height(), self.cur_piece.shape())

    def keyPressEvent(self, event):

        key = event.key()

        if key == Qt.Key_E:
            qApp.exit(Tetris.EXIT_CODE_REBOOT)

        if not self.is_started or self.cur_piece.shape() == Tetrominoe.no_shape:
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
            if self.is_waiting_after_line:
                self.is_waiting_after_line = False
                self.new_piece()
            else:
                self.one_line_down()

        else:
            super(Board, self).timerEvent(event)

    def clear_board(self):
        for i in range(Board.board_height * Board.board_width):
            self.board.append(Tetrominoe.no_shape)

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
            self.set_shape_at(x, y, self.cur_piece.shape())

        self.remove_full_lines()

        if not self.is_waiting_after_line:
            self.new_piece()

    def remove_full_lines(self):
        num_full_lines = 0
        rows_to_remove = []

        for i in range(Board.board_height):
            n = 0
            for j in range(Board.board_width):
                if not self.shape_at(j, i) == Tetrominoe.no_shape:
                    n = n + 1

            if n == 10:
                rows_to_remove.append(i)

        rows_to_remove.reverse()

        for m in rows_to_remove:
            for k in range(m, Board.board_height):
                for g in range(Board.board_width):
                    self.set_shape_at(g, k, self.shape_at(g, k + 1))

        num_full_lines = num_full_lines + len(rows_to_remove)

        if num_full_lines > 0:
            self.num_lines_removed = self.num_lines_removed + num_full_lines
            self.msg_statusbar.emit(str(self.num_lines_removed))
            self.is_waiting_after_line = True
            self.cur_piece.set_shape(Tetrominoe.no_shape)
            self.update()

    def new_piece(self):
        self.cur_piece.set_random_shape()
        self.cur_x = Board.board_width // 2 + 1
        self.cur_y = Board.board_height - 1 + self.cur_piece.min_y()

        if not self.try_move(self.cur_piece, self.cur_x, self.cur_y):
            self.cur_piece.set_shape(Tetrominoe.no_shape)
            self.timer.stop()
            self.is_started = False
            self.msg_statusbar.emit("Game over")
            add_to_rate(self.num_lines_removed)
            self.is_lose = True

    def try_move(self, new_piece, new_x, new_y):
        for i in range(4):
            x = new_x + new_piece.get_x(i)
            y = new_y - new_piece.get_y(i)

            if x < 0 or x >= Board.board_width or y < 0 or y >= Board.board_height:
                return False

            if self.shape_at(x, y) != Tetrominoe.no_shape:
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
        painter.drawLine(x + self.square_width() - 1,
                         y + self.square_height() - 1, x + self.square_width() - 1, y + 1)


class Tetrominoe(object):
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
        self.coords = [[0,0] for i in range(4)]
        self.piece_shape = Tetrominoe.no_shape
        self.set_shape(Tetrominoe.no_shape)

    def shape(self):
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
        if self.piece_shape == Tetrominoe.square_shape:
            return self

        result = Shape()
        result.piece_shape = self.piece_shape

        for i in range(4):
            result.set_x(i, self.get_y(i))
            result.set_y(i, -self.get_x(i))

        return result


if __name__ == '__main__':
    currentExitCode = Tetris.EXIT_CODE_REBOOT
    while currentExitCode == Tetris.EXIT_CODE_REBOOT:
        app = QApplication(sys.argv)
        tetris = Tetris()
        tetris.show()
        currentExitCode = app.exec_()
        app = None