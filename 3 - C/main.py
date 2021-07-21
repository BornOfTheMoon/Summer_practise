import pygame as pg


pg.init()
size = 700, 500
screen = pg.display.set_mode(size)
coordinates = []
screen.fill((0, 0, 0))
pg.display.flip()

running = True
while running:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
        if event.type == pg.KEYDOWN and coordinates.__len__():
            if event.key == pg.K_z and (event.mod and pg.KMOD_CTRL):
                coordinates.pop()
                screen.fill((0, 0, 0))
                for coord in coordinates:
                    pg.draw.rect(screen, (255, 255, 255), coord, 2)
                pg.display.flip()
        if event.type == pg.MOUSEBUTTONDOWN:
            x1 = event.pos[0]
            y1 = event.pos[1]
            moving = True
            while moving:
                for second_event in pg.event.get():
                    if second_event.type == pg.MOUSEMOTION:
                        w = second_event.pos[0] - x1
                        h = second_event.pos[1] - y1
                        screen.fill((0, 0, 0))
                        for coord in coordinates:
                            pg.draw.rect(screen, (255, 255, 255), coord, 2)
                        pg.draw.rect(screen, (255, 255, 255), (x1, y1, w, h), 2)
                        pg.display.flip()
                    if second_event.type == pg.MOUSEBUTTONUP:
                        coordinates.append((x1, y1, w, h))
                        moving = False
                    if second_event.type == pg.QUIT:
                        moving = False

pg.quit()
