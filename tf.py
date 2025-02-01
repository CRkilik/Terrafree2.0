import pygame
import random
import noise
import sys

# Инициализация PyGame
pygame.init()

# Настройки экрана
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("TerraFree 2.0")

# Цвета
SKY_BLUE = (135, 206, 235)
WHITE = (255, 255, 255)
RED = (255, 0, 0)

# Размеры блоков и игрока
BLOCK_SIZE = 50
PLAYER_WIDTH, PLAYER_HEIGHT = 25, 50

# Загрузка текстур
textures = {
    "grass": pygame.image.load("assets/texture/grass.png"),
    "dirt": pygame.image.load("assets/texture/dirt.png"),
    "stone": pygame.image.load("assets/texture/stone.png"),
    "player": pygame.image.load("assets/texture/player.png"),
    "pjump": pygame.image.load("assets/texture/pjump.png"),
    "pright": pygame.image.load("assets/texture/pright.png"),
    "pleft": pygame.image.load("assets/texture/pleft.png"),
    "block": pygame.image.load("assets/texture/block.png")
}

# Масштабирование текстур
for key in textures:
    textures[key] = pygame.transform.scale(textures[key], (BLOCK_SIZE, BLOCK_SIZE))

textures["player"] = pygame.transform.scale(textures["player"], (PLAYER_WIDTH, PLAYER_HEIGHT))
textures["pjump"] = pygame.transform.scale(textures["pjump"], (PLAYER_WIDTH, PLAYER_HEIGHT))
textures["pright"] = pygame.transform.scale(textures["pright"], (PLAYER_WIDTH, PLAYER_HEIGHT))
textures["pleft"] = pygame.transform.scale(textures["pleft"], (PLAYER_WIDTH, PLAYER_HEIGHT))

# Генерация мира с использованием шума Перлина
def generate_world_chunk(start_x, width, height):
    world_chunk = []
    scale = 70
    octaves = 3
    persistence = 0.15
    lacunarity = 2.0
    seed = random.randint(0, 1000)

    for x in range(start_x, start_x + width):
        column = []
        y_offset = int(noise.pnoise1(x / scale, octaves=octaves, persistence=persistence, lacunarity=lacunarity, base=seed) * 5)
        
        if random.random() < 0.2:  # 20% шанс на поляну
            y_offset = 0

        top_ground = height // 2 + y_offset
        random_variation = random.randint(-1, 1)
        top_ground += random_variation

        for y in range(height):
            if y < top_ground:
                column.append(None)
            elif y == top_ground:
                column.append("grass")
            elif y < top_ground + 3:
                column.append("dirt")
            else:
                column.append("stone")
        world_chunk.append(column)
    return world_chunk

# Функция для поиска безопасной позиции спавна
def find_spawn_position(world):
    spawn_x = len(world) // 2
    for y in range(len(world[0])):
        if world[spawn_x][y] == "grass":
            return spawn_x * BLOCK_SIZE, (y - 1) * BLOCK_SIZE
    return spawn_x * BLOCK_SIZE, len(world[0]) * BLOCK_SIZE // 2

# Класс игрока
class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = PLAYER_WIDTH
        self.height = PLAYER_HEIGHT
        self.velocity_x = 0
        self.velocity_y = 0
        self.on_ground = False
        self.texture = textures["player"]
        self.direction = "right"
        self.name = "Player"

    def update(self, keys, world):
        if keys[pygame.K_a]:
            self.velocity_x = -5
            self.direction = "left"
            self.texture = textures["pleft"]
        elif keys[pygame.K_d]:
            self.velocity_x = 5
            self.direction = "right"
            self.texture = textures["pright"]
        else:
            self.velocity_x = 0
            self.texture = textures["player"]

        if keys[pygame.K_SPACE] and self.on_ground:
            self.velocity_y = -15
            self.texture = textures["pjump"]
            self.on_ground = False

        self.velocity_y += 1
        if self.velocity_y > 10:
            self.velocity_y = 10

        self.check_collisions(world)

    def check_collisions(self, world):
        future_y = self.y + self.velocity_y
        if self.velocity_y > 0:
            bottom_block_y = (future_y + self.height) // BLOCK_SIZE
            bottom_block_x = self.x // BLOCK_SIZE
            if bottom_block_y < len(world[0]) and world[bottom_block_x][bottom_block_y] is not None:
                self.velocity_y = 0
                self.on_ground = True
                self.y = bottom_block_y * BLOCK_SIZE - self.height
            else:
                self.on_ground = False

        elif self.velocity_y < 0:
            top_block_y = future_y // BLOCK_SIZE
            top_block_x = self.x // BLOCK_SIZE
            if top_block_y >= 0 and world[top_block_x][top_block_y] is not None:
                self.velocity_y = 0
                self.y = (top_block_y + 1) * BLOCK_SIZE

        self.y += self.velocity_y

        future_x = self.x + self.velocity_x
        if self.velocity_x > 0:
            right_block_x = (future_x + self.width) // BLOCK_SIZE
            right_block_y_top = self.y // BLOCK_SIZE
            right_block_y_bottom = (self.y + self.height - 1) // BLOCK_SIZE
            if (right_block_x < len(world) and 
                (world[right_block_x][right_block_y_top] is not None or 
                 world[right_block_x][right_block_y_bottom] is not None)):
                self.velocity_x = 0
                self.x = right_block_x * BLOCK_SIZE - self.width
        elif self.velocity_x < 0:
            left_block_x = future_x // BLOCK_SIZE
            left_block_y_top = self.y // BLOCK_SIZE
            left_block_y_bottom = (self.y + self.height - 1) // BLOCK_SIZE
            if (left_block_x >= 0 and 
                (world[left_block_x][left_block_y_top] is not None or 
                 world[left_block_x][left_block_y_bottom] is not None)):
                self.velocity_x = 0
                self.x = (left_block_x + 1) * BLOCK_SIZE

        self.x += self.velocity_x

    def draw(self, screen, camera_x, camera_y):
        screen.blit(self.texture, (self.x - camera_x, self.y - camera_y))

# Основной игровой цикл
def main():
    clock = pygame.time.Clock()
    world_width, world_height = 200, 100
    world = generate_world_chunk(0, world_width, world_height)

    spawn_x, spawn_y = find_spawn_position(world)
    player = Player(spawn_x, spawn_y)

    camera_x, camera_y = player.x - SCREEN_WIDTH // 2, player.y - SCREEN_HEIGHT // 2

    running = True
    chat_open = False
    chat_input = ""
    chat_messages = []
    font = pygame.font.Font(None, 36)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_t:
                    if not chat_open:  # Открываем чат только если он закрыт
                        chat_open = True
                        chat_input = ""  # Очищаем строку ввода только при открытии

                if chat_open:
                    if event.key == pygame.K_RETURN:
                        if chat_input.strip():  # Проверяем, что сообщение не пустое
                            message = f"{player.name}> {chat_input}"
                            chat_messages.append((message, pygame.time.get_ticks()))
                            if chat_input.startswith("/set_name "):
                                new_name = chat_input.split(" ", 1)[1]
                                player.name = new_name
                            elif chat_input.startswith("/tp "):
                                try:
                                    _, x, y = chat_input.split(" ")
                                    player.x = int(x)
                                    player.y = int(y)
                                except ValueError:
                                    pass
                        chat_input = ""
                        chat_open = False  # Закрываем чат
                    elif event.key == pygame.K_BACKSPACE:
                        chat_input = chat_input[:-1]
                    else:
                        chat_input += event.unicode

            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                world_x = (mouse_x + camera_x) // BLOCK_SIZE
                world_y = (mouse_y + camera_y) // BLOCK_SIZE

                if event.button == 1:
                    if 0 <= world_x < len(world) and 0 <= world_y < len(world[0]):
                        world[world_x][world_y] = None
                elif event.button == 3:
                    if 0 <= world_x < len(world) and 0 <= world_y < len(world[0]):
                        world[world_x][world_y] = "block"

        keys = pygame.key.get_pressed()
        player.update(keys, world)

        if player.x // BLOCK_SIZE < len(world) // 4:
            new_chunk = generate_world_chunk(len(world), world_width // 2, world_height)
            world = new_chunk + world
            player.x += len(new_chunk) * BLOCK_SIZE
        elif player.x // BLOCK_SIZE > len(world) * 3 // 4:
            new_chunk = generate_world_chunk(len(world), world_width // 2, world_height)
            world.extend(new_chunk)

        camera_x = player.x - SCREEN_WIDTH // 2
        camera_y = player.y - SCREEN_HEIGHT // 2

        screen.fill(SKY_BLUE)

        for x in range(len(world)):
            for y in range(len(world[x])):
                if world[x][y] is not None:
                    texture = textures[world[x][y]]
                    screen.blit(texture, (x * BLOCK_SIZE - camera_x, y * BLOCK_SIZE - camera_y))

        player.draw(screen, camera_x, camera_y)

        # Отрисовка чата
        current_time = pygame.time.get_ticks()
        for message, timestamp in chat_messages[:]:
            if current_time - timestamp > 10000:
                chat_messages.remove((message, timestamp))
            else:
                text_surface = font.render(message, True, WHITE)
                screen.blit(text_surface, (10, SCREEN_HEIGHT - 100 - (chat_messages.index((message, timestamp)) * 30)))

        if chat_open:
            input_surface = font.render(f"> {chat_input}", True, WHITE)
            screen.blit(input_surface, (10, SCREEN_HEIGHT - 80))  # Поднимаем чат выше

        # Надпись ALPHA-2.0 в правом верхнем углу
        alpha_text = font.render("ALPHA-2.0", True, RED)
        screen.blit(alpha_text, (SCREEN_WIDTH - alpha_text.get_width() - 10, 10))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
