import pygame as pg
from math import sin, cos, radians


pg.init()
height = 600
size = height, height
screen = pg.display.set_mode(size)
screen.fill((0, 0, 0))
pg.display.flip()
fps = 60
clock = pg.time.Clock()
color = pg.Color(0, 0, 255)
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


        for dot in range(360):
            x1 = int(cos(radians(dot)) * 250) + height // 2
            x2 = int(cos(radians(dot * k)) * 250) + height // 2
            x3 = int(cos(radians(dot * (k - 0.2))) * 250) + height // 2
            y1 = int(sin(radians(dot)) * 250) + height // 2
            y2 = int(sin(radians(dot * k)) * 250) + height // 2
            y3 = int(sin(radians(dot * (k - 0.2))) * 250) + height // 2
            pg.draw.line(screen, (0, 0, 0), (x1, y1), (x3, y3), 1)
            pg.draw.line(screen, color, (x1, y1), (x2, y2), 1)
            pg.display.flip()
        k += 0.2
        hsv = color.hsva
        color.hsva = ((hsv[0] + 10) % 360, hsv[1], hsv[2], hsv[3])

        # for dot in range(360):
        #     screen.fill((0, 0, 0))
        #     for point in range(dot + 1):
        #         x1 = int(cos(radians(point)) * 250) + height // 2
        #         x2 = int(cos(radians(point * k)) * 250) + height // 2
        #         y1 = int(sin(radians(dot)) * 250) + height // 2
        #         y2 = int(sin(radians(dot * k)) * 250) + height // 2
        #         pg.draw.line(screen, color, (x1, y1), (x2, y2), 1)
        #         pg.display.flip()
        #     for point in range(dot + 1, 360):
        #         x1 = int(cos(radians(point)) * 250) + height // 2
        #         x2 = int(cos(radians(point * (k - 0.2))) * 250) + height // 2
        #         y1 = int(sin(radians(dot)) * 250) + height // 2
        #         y2 = int(sin(radians(dot * (k - 0.2))) * 250) + height // 2
        #         hsv = color.hsva
        #         pg.draw.line(screen, (hsv[0] - 20, hsv[1], hsv[2], hsv[3]), (x1, y1), (x2, y2), 1)
        #         pg.display.flip()
        # k += 0.2
        # hsv = color.hsva
        # color.hsva = ((hsv[0] + 10) % 360, hsv[1], hsv[2], hsv[3])

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
