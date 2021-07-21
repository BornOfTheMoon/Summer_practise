import pygame as pg
from random import randint


class Board:
    def __init__(self):
        self.count_cells = 10
        self.cell_size = 60
        self.board = [[0] * self.count_cells for _ in range(self.count_cells)]
        self.count_mines = randint(1, 20)
        self.mines = []
        for i in range(self.count_mines):
            x = randint(0, 9)
            y = randint(0, 9)
            self.mines.append((x, y))
        for i in range(self.count_cells):
            for j in range(self.count_cells):
                if (i, j) in self.mines:
                    self.board[i][j] = -1
                    for h in range(i - 1, i + 2):
                        for w in range(j - 1, j + 2):
                            if (h >= 0) and (h < self.count_cells) and (w >= 0) and (w < self.count_cells) and (self.board[h][w] != -1):
                                self.board[h][w] += 1

    def render(self, screen):
        screen.fill((0, 0, 0))
        for i in range(self.count_cells):
            for j in range(self.count_cells):
                if self.board[i][j] == -1:
                    pg.draw.rect(screen, (255, 0, 0),
                                 (i * self.cell_size + 20, j * self.cell_size + 20, self.cell_size, self.cell_size), 0)
                pg.draw.rect(screen, (255, 255, 255),
                             (i * self.cell_size + 20, j * self.cell_size + 20, self.cell_size, self.cell_size), 1)
        pg.display.flip()


if __name__ == '__main__':
    pg.init()
    board_size = 640, 640
    screen = pg.display.set_mode(board_size)
    board = Board()
    board.render(screen)
    running = True
    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
            if event.type == pg.MOUSEBUTTONDOWN:
                i = (event.pos[0] - 20) // 60
                j = (event.pos[1] - 20) // 60
                if board.board[i][j] != -1:
                    font = pg.font.Font(None, 50)
                    text = font.render(str(board.board[i][j]), 1, (255, 255, 255))
                    text_x = i * 60 + 41
                    text_y = j * 60 + 34
                    screen.blit(text, (text_x, text_y))
                    pg.display.flip()
    pg.quit()

