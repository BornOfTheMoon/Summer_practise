import pygame as pg


class Board:
    def __init__(self, size, count_cells):
        self.count_cells = count_cells
        self.board_size = size, size
        self.cell_size = int(size / count_cells)
        self.board = [[0] * self.count_cells for i in range(self.count_cells)]
        for i in range(self.count_cells):
            for j in range(self.count_cells):
                if (i % 2 == 0 and j % 2 != 0) or (i % 2 != 0 and j % 2 == 0):
                    self.board[i][j] = 1

    def render(self):
        pg.init()
        screen = pg.display.set_mode(self.board_size)
        screen.fill((0, 0, 0))
        for i in range(self.count_cells):
            for j in range(self.count_cells):
                if self.board[i][j] == 1:
                    pg.draw.rect(screen, (255, 255, 255),
                                 (i * self.cell_size, j * self.cell_size, self.cell_size, self.cell_size), 0)
        pg.display.flip()


if __name__ == '__main__':
    size, count_cells = map(int, input().split())
    board = Board(size, count_cells)
    board.render()
    while pg.event.wait().type != pg.QUIT:
        pass
    pg.quit()
