import pygame as pg


pg.init()
size = 300, 300
screen = pg.display.set_mode(size)
running = True
screen.fill((0, 0, 0))
pg.draw.rect(screen, (0, 0, 255), (0, 0, 50, 50))
pg.display.flip()

while running:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
        if event.type == pg.MOUSEBUTTONDOWN:
            moving = True
            while moving:
                for second_event in pg.event.get():
                    if second_event.type == pg.MOUSEMOTION:
                        screen.fill((0, 0, 0))
                        pg.draw.rect(screen, (0, 0, 255), (second_event.pos[0] - 25, second_event.pos[1] - 25, 50, 50))
                    if second_event.type == pg.MOUSEBUTTONUP or event.type == pg.QUIT:
                        moving = False
                pg.display.flip()

pg.quit()