import math

import pygame
import sys
import os


NAME_TEXT = ["Unicorn adventure"]
INTRO_TEXT = ["Играть", "",
              "Правила", "",
              "Выход"]
RULES_TEXT = ["""Помогите единорогу выбраться из замка.""",
                  """Для этого на каждом уровне нужно пройти""",
                  """через дверь, но она откроется только после """,
                  """того, как единорог встанет на кнопку.""",
                  """Помогайте ему с помощью клавиш "вправо" """,
                  """и "влево" для движения и клавиши "вверх" """,
                  """для прыжка.""",
                  "Удачи! Единорог надеется на Вас!"]
BACK_TEXT = ["Перейти в меню"]
LOSE_TEXT = ["О нет!", "Единорог остался в замке!"]
LOSE_MENU = ["Попробовать ещё", "", "Перейти в меню"]
CONGRATES_TEXT = ["Вы помогли единорогу выбраться!",
                  "Он Вам очень благодарен!"]

COUNT_LEVELS = 2


pygame.init()
size = WIDTH, HEIGHT = 1100, 700
tile_width = tile_height = 110
tile_size = tile_width, tile_height
screen = pygame.display.set_mode(size)
FPS = 60
clock = pygame.time.Clock()


def terminate():
    pygame.quit()
    sys.exit()


def load_image(name, color_key=None):
    fullname = os.path.join('images', name)
    try:
        image = pygame.image.load(fullname).convert()
    except pygame.error as message:
        print('Cannot load image:', name)
        raise SystemExit(message)

    if color_key is not None:
        if color_key == -1:
            color_key = image.get_at((0, 0))
        image.set_colorkey(color_key)
    else:
        image = image.convert_alpha()
    return image


def load_level(filename):
    filename = os.path.join("levels", filename)
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]
    max_width = max(map(len, level_map))
    return list(map(lambda x: x.ljust(max_width, '.'), level_map))


tile_images = {
    'wall': load_image('wall.jpg'),
    'grass': load_image('grass.jpg'),
    'spikes': load_image('spike.jpg', -1)
}
# player_sprite = load_image('unicorn.png', -1)

all_sprites = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
grasses_group = pygame.sprite.Group()
spikes_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()
doors_group = pygame.sprite.Group()
levers_group = pygame.sprite.Group()
spikes_indexes = []
grasses_indexes = []


background = pygame.transform.scale(load_image('background.jpg'), size)
dark_background = background.copy()
pygame.draw.rect(dark_background, (0, 0, 0, 200), (0, 0, WIDTH, HEIGHT))


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        if tile_type == 'grass':
            super().__init__(tiles_group, all_sprites, grasses_group)
        elif tile_type == 'spikes':
            super().__init__(tiles_group, all_sprites, spikes_group)
        else:
            super().__init__(tiles_group, all_sprites)
        self.image = pygame.transform.scale(tile_images[tile_type], tile_size)
        self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y + 20)
        self.pos = pos_x, pos_y
        self.tile_type = tile_type


class Door(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(doors_group, all_sprites)
        self.sprite = load_image('closed_door.jpg', -1)
        self.image = pygame.transform.scale(self.sprite, tile_size)
        self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y + 20)
        self.pos = pos_x, pos_y
        self.state = False

    def update(self):
        self.state = True
        self.sprite = load_image('opened_door.jpg', -1)
        self.image = pygame.transform.scale(self.sprite, tile_size)
        doors_group.draw(screen)
        pygame.display.flip()


class Lever(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(levers_group, all_sprites)
        self.sprite = load_image('inactive_lever.jpg', -1)
        self.image = pygame.transform.scale(self.sprite, tile_size)
        self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y + 20)
        self.pos = pos_x, pos_y
        self.state = False

    def update(self):
        self.sprite = load_image('active_lever.jpg', -1)
        self.image = pygame.transform.scale(self.sprite, tile_size)
        doors_group.draw(screen)
        pygame.display.flip()
        self.state = True


class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(player_group, all_sprites)
        self.sprite = load_image('unicorn_r.png', -1)
        self.image = pygame.transform.scale(self.sprite, tile_size)
        self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y + 20)
        self.pos = pos_x, pos_y
        self.on_ground = True
        self.gravity = 0.05

    def move(self, direction, width, height):
        m_x, m_y = self.pos
        m_x += direction[0]
        m_y += direction[1]
        if not (m_x in range(width) and math.floor(m_y) in range(height)):
            return
        if (not (m_x, math.floor(m_y)) in grasses_indexes) and direction[0] != 0:
            self.pos = m_x, m_y
            x, y = self.rect.x + direction[0] * tile_width, self.rect.y
            self.rect = self.image.get_rect().move(x, y)
        if (m_x, math.floor(m_y + 1)) in spikes_indexes and direction[0] != 0:
            all_sprites.draw(screen)
            player_group.draw(screen)
            self.kill()
            spikes_indexes.clear()
            grasses_indexes.clear()
            lose_screen()
        if (not (m_x, math.floor(m_y - 1)) in grasses_indexes) and direction[1] != 0 and self.on_ground:
            self.pos = m_x, m_y
            x, y = self.rect.x, self.rect.y + direction[1] * tile_height
            self.rect = self.image.get_rect().move(x, y)
        if not (m_x, math.floor(m_y + 1)) in grasses_indexes:
            self.on_ground = False

    def fall(self):
        m_x, m_y = self.pos
        m_y += self.gravity
        if (m_x, math.floor(m_y + 1)) in spikes_indexes:
            self.kill()
            spikes_indexes.clear()
            grasses_indexes.clear()
            lose_screen()
        if (m_x, math.floor(m_y + 1)) in grasses_indexes or m_y > 5:
            m_y = math.floor(m_y)
            self.pos = m_x, m_y
            x, y = self.rect.x, m_y * tile_height + 20
            self.rect = self.image.get_rect().move(x, y)
            self.on_ground = True
        else:
            self.pos = m_x, m_y
            x, y = self.rect.x, self.rect.y + self.gravity * tile_height
            self.rect = self.image.get_rect().move(x, y)


def generate_level(level, width, height):
    new_player, new_lever, new_door = None, None, None
    for y in range(height):
        for x in range(width):
            if level[y][x] == '.':
                Tile('wall', x, y)
            elif level[y][x] == '#':
                Tile('wall', x, y)
                Tile('grass', x, y)
                grasses_indexes.append((x, y))
            elif level[y][x] == '!':
                Tile('wall', x, y)
                Tile('spikes', x, y)
                spikes_indexes.append((x, y))
            elif level[y][x] == '%':
                Tile('wall', x, y)
                new_door = Door(x, y)
            elif level[y][x] == '@':
                Tile('wall', x, y)
                new_player = Player(x, y)
            elif level[y][x] == '?':
                Tile('wall', x, y)
                new_lever = Lever(x, y)
    return new_player, new_lever, new_door


def show_text(text, font_size, text_coord_y, color, text_coord_x=120):
    for line in text:
        font = pygame.font.Font(None, font_size)
        string_rendered = font.render(line, 1, color)
        text_rect = string_rendered.get_rect()
        text_coord_y += 10
        text_rect.top = text_coord_y
        text_rect.x = text_coord_x
        text_coord_y += text_rect.height
        screen.blit(string_rendered, text_rect)


def start_screen():
    screen.fill((0, 0, 0))
    pygame.mouse.set_cursor(*pygame.cursors.arrow)
    screen.blit(background, (0, 0))
    pygame.display.flip()
    show_text(NAME_TEXT, 90, 90, (0, 0, 0))
    show_text(INTRO_TEXT, 70, 300, (190, 190, 170))

    flag = False
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.MOUSEMOTION:
                x, y = event.pos
                if (((x in range(120, 300) and y in range(550, 600)) or (x in range(120, 320) and y in range(430, 480))
                    or (x in range(120, 285) and y in range(310, 360))) and not flag) or x in range(120, 400) and \
                        y in range(610, 650) and flag:
                    pygame.mouse.set_cursor(*pygame.cursors.tri_left)
                else:
                    pygame.mouse.set_cursor(*pygame.cursors.arrow)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                if x in range(120, 300) and y in range(550, 600) and not flag:
                    terminate()
                elif x in range(120, 320) and y in range(430, 480) and not flag:
                    flag = True
                    screen.blit(background, (0, 0))
                    screen.blit(dark_background, (0, 0))
                    show_text(RULES_TEXT, 60, 120, (190, 190, 170))
                    show_text(BACK_TEXT, 50, 600, (150, 150, 130))
                elif x in range(120, 285) and y in range(310, 360) and not flag:
                    play()
                elif x in range(120, 400) and y in range(610, 650) and flag:
                    flag = False
                    screen.blit(background, (0, 0))
                    show_text(NAME_TEXT, 90, 90, (0, 0, 0))
                    show_text(INTRO_TEXT, 70, 300, (190, 190, 170))

        pygame.display.flip()
        clock.tick(FPS)


def lose_screen():
    pygame.mouse.set_cursor(*pygame.cursors.arrow)
    pygame.draw.rect(dark_background, (0, 0, 0, 200), (0, 0, WIDTH, HEIGHT))
    screen.blit(dark_background, (0, 0))
    show_text(LOSE_TEXT, 60, 120, (150, 150, 130))
    show_text(LOSE_MENU, 40, 300, (150, 150, 130))
    pygame.display.flip()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.MOUSEMOTION:
                x, y = event.pos
                if (x in range(120, 375) and y in range(300, 345)) or (x in range(120, 350) and y in range(370, 415)):
                    pygame.mouse.set_cursor(*pygame.cursors.tri_left)
                else:
                    pygame.mouse.set_cursor(*pygame.cursors.arrow)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                if x in range(120, 375) and y in range(300, 345):
                    play()
                elif x in range(120, 350) and y in range(370, 415):
                    start_screen()

        pygame.display.flip()
        clock.tick(FPS)


def congrates_screen():
    pygame.mouse.set_cursor(*pygame.cursors.arrow)
    pygame.draw.rect(dark_background, (0, 0, 0, 200), (0, 0, WIDTH, HEIGHT))
    screen.blit(dark_background, (0, 0))
    show_text(CONGRATES_TEXT, 60, 120, (150, 150, 130))
    show_text(BACK_TEXT, 40, 300, (150, 150, 130))
    pygame.display.flip()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.MOUSEMOTION:
                x, y = event.pos
                if x in range(120, 375) and y in range(300, 330):
                    pygame.mouse.set_cursor(*pygame.cursors.tri_left)
                else:
                    pygame.mouse.set_cursor(*pygame.cursors.arrow)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                if x in range(120, 375) and y in range(300, 330):
                    start_screen()

        pygame.display.flip()
        clock.tick(FPS)


def play(number=1):
    if number > COUNT_LEVELS:
        congrates_screen()
    pygame.mouse.set_cursor(*pygame.cursors.arrow)
    screen.fill((0, 0, 0))
    show_text(BACK_TEXT, 20, -5, (255, 255, 255), 980)
    level = load_level(str(number) + ".txt")
    level_width = len(level[0])
    level_height = len(level)
    player, lever, door = generate_level(level, level_width, level_height)
    all_sprites.draw(screen)
    pygame.display.flip()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                terminate()
            elif event.type == pygame.MOUSEMOTION:
                x, y = event.pos
                if x in range(980, 1020) and y in range(5, 25):
                    pygame.mouse.set_cursor(*pygame.cursors.tri_left)
                else:
                    pygame.mouse.set_cursor(*pygame.cursors.arrow)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                if x in range(980, 1020) and y in range(5, 25):
                    spikes_indexes.clear()
                    grasses_indexes.clear()
                    player.kill()
                    start_screen()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    player.move((-1, 0), level_width, level_height)
                elif event.key == pygame.K_RIGHT:
                    player.move((1, 0), level_width, level_height)
                elif event.key == pygame.K_SPACE:
                    player.move((0, -1), level_width, level_height)

        if not player.on_ground:
            player.fall()

        if player.pos == lever.pos and not lever.state:
            lever.update()
            door.update()

        all_sprites.draw(screen)
        player_group.draw(screen)
        pygame.display.flip()

        clock.tick(FPS)

        if player.pos == door.pos and door.state:
            player.kill()
            spikes_indexes.clear()
            grasses_indexes.clear()
            number += 1
            play(number)


start_screen()
