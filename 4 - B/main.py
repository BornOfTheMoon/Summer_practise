import pygame


pygame.init()
tile_width = tile_height = 50
tile_size = tile_width, tile_height


def get_size(filename):
    filename = filename
    with open(filename, 'r') as level:
        level_map = [line.strip() for line in level]

    width = max(map(len, level_map))
    height = len(level_map)
    return width * tile_width, height * tile_height


size = get_size("map.txt")
display = pygame.display.set_mode(size)


def get_index(x, y, level_width):
    return y * level_width + x


def load_level(filename):
    with open(filename, 'r') as level:
        level_map = [line.strip() for line in level]

    max_width = max(map(len, level_map))

    return list(map(lambda x: x.ljust(max_width, '.'), level_map))


def load_image(name, color_key=None):
    try:
        image = pygame.image.load(name).convert()
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


tile_images = {
    'box': load_image('box.png'),
    'grass': load_image('grass.png')
}
player_sprite = load_image('unicorn.png', -1)

all_sprites = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
boxes_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        if tile_type == 'box':
            super().__init__(tiles_group, all_sprites, boxes_group)
        else:
            super().__init__(tiles_group, all_sprites)
        self.image = pygame.transform.scale(tile_images[tile_type], tile_size)
        self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y)
        self.pos = pos_x, pos_y
        self.tile_type = tile_type


class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(player_group, all_sprites)
        self.image = pygame.transform.scale(player_sprite, tile_size)
        self.rect = self.image.get_rect().move(
            tile_width * pos_x + 15, tile_height * pos_y + 5)
        self.vision = 1, 0
        self.pos = pos_x, pos_y

    def move(self, velocity):
        v_x, v_y = velocity
        if v_x != 0 or v_y != 0:
            self.vision = velocity
            m_x, m_y = self.pos
            m_x += v_x
            m_y += v_y
            if m_x < 0 or m_x > size[0] / tile_width - 1 or m_y < 0 or m_y > size[1] / tile_height - 1:
                return
            if not tiles_group.sprites()[get_index(m_x, m_y, level_x + 1)] in boxes_group:
                self.pos = m_x, m_y
                x, y = self.rect.x + v_x * tile_width, self.rect.y + v_y * tile_height
                self.rect = self.image.get_rect().move(x, y)

    def attack(self):
        vision_x, vision_y = self.vision
        m_x, m_y = self.pos
        attack_x, attack_y = vision_x + m_x, vision_y + m_y
        if attack_x >= 0 and attack_x < size[0] / tile_width and attack_y >= 0 and attack_y < size[1] / tile_height:
            attacked_tile = tiles_group.sprites()[get_index(attack_x, attack_y, level_x + 1)]
            if attacked_tile in boxes_group:
                boxes_group.remove(attacked_tile)
                attacked_tile.image = pygame.transform.scale(tile_images['grass'], (tile_width, tile_height))
                player.move(self.vision)


def generate_level(level):
    new_player, x, y = None, None, None
    for y in range(len(level)):
        for x in range(len(level)):
            if level[y][x] == '.':
                Tile('grass', x, y)
            elif level[y][x] == '#':
                Tile('box', x, y)
            elif level[y][x] == '@':
                Tile('grass', x, y)
                new_player = Player(x, y)
    return new_player, x, y


player, level_x, level_y = generate_level(load_level('map.txt'))
running = True
velocity = 0, 0

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_UP:
                velocity = 0, -1
            elif event.key == pygame.K_DOWN:
                velocity = 0, 1
            elif event.key == pygame.K_RIGHT:
                velocity = 1, 0
            elif event.key == pygame.K_LEFT:
                velocity = -1, 0
            elif event.key == pygame.K_SPACE:
                player.attack()

    player.move(velocity)
    velocity = 0, 0
    tiles_group.draw(display)
    player_group.draw(display)
    pygame.display.flip()

pygame.quit()
