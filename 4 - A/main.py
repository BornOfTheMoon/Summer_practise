import pygame
import random


pygame.init()
display = pygame.display.set_mode((400, 400))
horizontal_borders = pygame.sprite.Group()
vertical_borders = pygame.sprite.Group()
balls = pygame.sprite.Group()


class Ball(pygame.sprite.Sprite):
    def __init__(self, radius, pos):
        super().__init__()
        self.radius = radius
        self.image = pygame.Surface((2 * radius, 2 * radius),
                                    pygame.SRCALPHA, 32)
        pygame.draw.circle(self.image, pygame.Color('red'),
                           (radius, radius), radius)
        x, y = pos[0] - radius, pos[1] - radius
        self.rect = pygame.Rect(x, y, 2 * radius - 5, 2 * radius - 5)
        self.vx = random.randint(-5, 5)
        self.vy = random.randint(-5, 5)

    def update(self):
        self.rect = self.rect.move(self.vx, self.vy)
        if pygame.sprite.spritecollideany(self, horizontal_borders):
            self.vy = -self.vy
            
        if pygame.sprite.spritecollideany(self, vertical_borders):
            self.vx = -self.vx

        if pygame.sprite.spritecollideany(self, balls):
            self.vx = -self.vx
            self.vy = -self.vy


class Border(pygame.sprite.Sprite):
    def __init__(self, x1, y1, x2, y2):
        super().__init__()
        if x1 == x2:
            self.add(vertical_borders)
            self.image = pygame.Surface((1, y2 - y1))
            self.rect = pygame.Rect(x1, y1, 1, y2 - y1)
        else:
            self.add(horizontal_borders)
            self.image = pygame.Surface((x2 - x1, 1))
            self.rect = pygame.Rect(x1, y1, x2 - x1, 1)


left_b = Border(0, 0, 0, 400)
right_b = Border(400, 0, 400, 400)
top_b = Border(0, 0, 400, 0)
bottom_b = Border(0, 400, 400, 400)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONUP:
            point = event.pos
            balls.add(Ball(20, point))

    fps = pygame.time.Clock().tick(30)
    for i, ball in enumerate(balls):
        balls.remove(ball)
        ball.update()
        balls.add(ball)
    display.fill((0, 0, 0))
    for ball in balls:
        display.blit(ball.image, ball.rect)
    pygame.display.flip()

pygame.quit()
