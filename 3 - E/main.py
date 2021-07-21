import pygame as pg
from math import sin, cos, radians


pg.init()
height = 600
size = height, height
screen = pg.display.set_mode(size)
screen.fill((0, 0, 0))
pg.display.flip()
fps = 120
clock = pg.time.Clock()
k = 2
running = True
drawing = True
while running:
    while drawing and k <= 10:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
                drawing = False
            if event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
                drawing = False
        # screen.fill((0, 0, 0))
        for dot in range(361):
            x1 = int(cos(radians(dot)) * 250) + height // 2
            x2 = int(cos(radians(dot * k)) * 250) + height // 2
            x3 = int(cos(radians(dot * (k - 0.1))) * 250) + height // 2
            y1 = int(sin(radians(dot)) * 250) + height // 2
            y2 = int(sin(radians(dot * k)) * 250) + height // 2
            y3 = int(sin(radians(dot * (k - 0.1))) * 250) + height // 2
            pg.draw.line(screen, (0, 0, 0), (x1, y1), (x3, y3), 1)
            pg.draw.line(screen, (0, 0, 255), (x1, y1), (x2, y2), 1)
            pg.display.flip()
        k += 0.1
    if k > 10:
        k = 2
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
            drawing = False
        if event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
            drawing = True
    clock.tick(fps)

pg.quit()
