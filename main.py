import pygame
import random
from tank import Tank
from enemy import EnemyTank
from wall import Wall
from smoke import Smoke

pygame.init()
screen = pygame.display.set_mode((800, 800))
clock = pygame.time.Clock()

# Музыка и звуки
pygame.mixer.init()
current_music = None
fire_sound = pygame.mixer.Sound("sounds/fire.wav")

def play_music(path):
    global current_music
    if current_music != path:
        pygame.mixer.music.stop()
        pygame.mixer.music.load(path)
        pygame.mixer.music.play(-1)
        current_music = path

# Затемнение экрана
def fade_to_black(duration=1000):
    fade_surface = pygame.Surface((800, 800))
    fade_surface.fill((0, 0, 0))
    start_time = pygame.time.get_ticks()
    while True:
        elapsed = pygame.time.get_ticks() - start_time
        alpha = min(255, int((elapsed / duration) * 255))
        fade_surface.set_alpha(alpha)
        screen.blit(fade_surface, (0, 0))
        pygame.display.flip()
        if alpha >= 255:
            break
        clock.tick(60)

walls = pygame.sprite.Group()

def generate_walls():
    wall_positions = []
    for x in range(0, 800, 80):
        for y in range(0, 800, 80):
            if 300 < x < 500 and 250 < y < 450:
                continue
            if 0 <= x < 800 and 750 <= y < 800:
                continue
            if 0 <= x < 800 and 0 <= y < 50:
                continue
            if 750 <= x < 800 and 0 <= y < 50:
                continue
            if random.random() < 0.15:
                wall = Wall(x, y)
                walls.add(wall)

# Состояние игры
state = "menu"

# Загрузка изображений
menu_bg = pygame.image.load("images/menu.png").convert()
game_bg = pygame.image.load("images/game1.png").convert()
win_image = pygame.image.load("images/win2.png").convert()
lose_image = pygame.image.load("images/lose2.png").convert()

button_raw = pygame.image.load("images/button.png").convert_alpha()
button_raw_hover = pygame.image.load("images/button_hover.png").convert_alpha()
button_image = pygame.transform.scale(button_raw, (350, 100))
button_hover = pygame.transform.scale(button_raw_hover, (350, 100))

raw_logo = pygame.image.load("images/1logo.png").convert_alpha()
logo_image = pygame.transform.scale(raw_logo, (450, 350))
logo_rect = logo_image.get_rect(center=(400, 180))

# Логотип для титров
credits_logo = pygame.image.load("images/1logo.png").convert_alpha()
credits_logo = pygame.transform.scale(credits_logo, (450, 350))
credits_logo_rect = credits_logo.get_rect(center=(400, 800))
credits_logo_target_y = 180

# Кнопки
start_button = button_image.get_rect(center=(400, 400))
credits_button = button_image.get_rect(center=(400, 500))
exit_button = button_image.get_rect(center=(400, 600))
restart_button = button_image.get_rect(center=(400, 550))
menu_button = button_image.get_rect(center=(400, 670))

life_image = pygame.image.load("images/gear1.png").convert_alpha()
life_image = pygame.transform.scale(life_image, (60, 60))

# Начальные объекты
def reset_game():
    global player_tank, player_group, enemy_group, bullet_group, smoke_group, win
    player_tank = Tank(400, 780, "images/tank-player.png", "images/bullet.png", fire_sound)
    enemy_group = pygame.sprite.Group()
    enemy_group.add(EnemyTank(400, 40, "images/tank-enemy.png", "images/bullet.png", player_tank, fire_sound))
    if random.random() < 0.5:
        enemy_group.add(EnemyTank(760, 40, "images/tank-enemy.png", "images/bullet.png", player_tank, fire_sound))
    player_group = pygame.sprite.Group(player_tank)
    bullet_group = pygame.sprite.Group()
    smoke_group = pygame.sprite.Group()
    walls.empty()
    generate_walls()
    win = False

reset_game()

# Данные для титров
credits_text = [
    "",
    "Лидер/Дизайнер/Код",
    "- Андрей Решетник",
    "",
    "Музыка",
    "- Lucas Pope",
    "(Papers, Please)",
    "",
    "Программы и технологии",
    "- Python",
    "- Pygame",
    "- VS Code (Код)",
    "- Krita (Весь дизайн)",
    "- Trello (Распределение задач...)",
    "- Github (Работа над файлами...)",
    "",
    "Отдельная благодарность",
    "- Моей семье",
    "которая поддержала меня ",
    "в трудные моменты",
    "",
    "",
    "Удачи в бою сержант!"
]
credits_y = 800
credits_speed = 50
credits_start_time = 0

# Анимация логотипа
logo_y_offset = 0
logo_direction = 1
logo_timer = 0
logo_delay = 1200
last_logo_move_time = pygame.time.get_ticks()

running = True
while running:
    screen.fill((0, 0, 0))
    keys = pygame.key.get_pressed()
    mouse_pos = pygame.mouse.get_pos()
    mouse_click = False

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_click = True
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            if state in ["playing", "credits"]:
                fade_to_black()
                if state == "credits":
                    credits_y = 800
                    credits_logo_rect.centery = 800  # Сбрасываем позицию логотипа
                state = "menu"

    # ---------- Главное меню ----------
    if state == "menu":
        play_music("sounds/menu_music.mp3")
        screen.blit(pygame.transform.scale(menu_bg, (800, 800)), (0, 0))

        current_time = pygame.time.get_ticks()
        if current_time - last_logo_move_time > logo_delay:
            logo_y_offset += 5 * logo_direction
            logo_direction *= -1
            last_logo_move_time = current_time

        screen.blit(logo_image, (logo_rect.x, logo_rect.y + logo_y_offset))

        # Кнопка "Начать игру"
        if start_button.collidepoint(mouse_pos):
            screen.blit(button_hover, start_button)
            if mouse_click:
                fade_to_black()
                reset_game()
                state = "playing"
        else:
            screen.blit(button_image, start_button)

        font = pygame.font.SysFont(None, 60)
        start_text = font.render("Начать игру", True, (255, 255, 255))
        screen.blit(start_text, start_text.get_rect(center=start_button.center))

        # Кнопка "Титры"
        if credits_button.collidepoint(mouse_pos):
            screen.blit(button_hover, credits_button)
            if mouse_click:
                fade_to_black()
                state = "credits"
                credits_y = 800
                credits_logo_rect.centery = 800  # Сбрасываем логотип
                credits_start_time = pygame.time.get_ticks()
        else:
            screen.blit(button_image, credits_button)

        credits_button_text = font.render("Титры", True, (255, 255, 255))
        screen.blit(credits_button_text, credits_button_text.get_rect(center=credits_button.center))

        # Кнопка "Выйти"
        if exit_button.collidepoint(mouse_pos):
            screen.blit(button_hover, exit_button)
            if mouse_click:
                running = False
        else:
            screen.blit(button_image, exit_button)

        exit_text = font.render("Выйти", True, (255, 255, 255))
        screen.blit(exit_text, exit_text.get_rect(center=exit_button.center))

    # ---------- Игра ----------
    elif state == "playing":
        pygame.mixer.music.stop()
        current_music = None
        screen.blit(pygame.transform.scale(game_bg, (800, 800)), (0, 0))
        # Урон
        player_tank.take_damage(bullet_group)
        for enemy in enemy_group:
            enemy.take_damage(bullet_group)

        # Удаление пуль
        for bullet in bullet_group:
            if bullet.check_collision_with_walls(walls):
                bullet.kill()

        # Смерть
        if not player_tank.alive():
            fade_to_black()
            state = "game_over"
            win = False
        elif not any(enemy.alive() for enemy in enemy_group):
            fade_to_black()
            state = "game_over"
            win = True

        # Обновление
        player_group.update(keys, bullet_group, walls, enemy_group, smoke_group)
        enemy_group.update(player_tank, bullet_group, walls, enemy_group, smoke_group)
        bullet_group.update()
        smoke_group.update()

        # Отрисовка
        player_group.draw(screen)
        enemy_group.draw(screen)
        bullet_group.draw(screen)
        walls.draw(screen)
        smoke_group.draw(screen)
        
        # Жизни игрока
        for i in range(player_tank.health):
            screen.blit(life_image, (10 + i * 65, 10))

    # ---------- Экран победы / поражения ----------
    elif state == "game_over":
        if win:
            play_music("sounds/win_music.mp3")
        else:
            play_music("sounds/lose_music.mp3")

        screen.blit(pygame.transform.scale(win_image if win else lose_image, (800, 800)), (0, 0))

        font = pygame.font.SysFont(None, 60)

        if restart_button.collidepoint(mouse_pos):
            screen.blit(button_hover, restart_button)
            if mouse_click:
                fade_to_black()
                reset_game()
                state = "playing"
        else:
            screen.blit(button_image, restart_button)

        restart_text = font.render("Начать заново", True, (255, 255, 255))
        screen.blit(restart_text, restart_text.get_rect(center=restart_button.center))

        if menu_button.collidepoint(mouse_pos):
            screen.blit(button_hover, menu_button)
            if mouse_click:
                fade_to_black()
                state = "menu"
        else:
            screen.blit(button_image, menu_button)

        menu_text = font.render("Выйти в меню", True, (255, 255, 255))
        screen.blit(menu_text, menu_text.get_rect(center=menu_button.center))

    # ---------- Титры ----------
    elif state == "credits":
        play_music("sounds/win_music.mp3")
        screen.fill((0, 0, 0))

        elapsed_time = (pygame.time.get_ticks() - credits_start_time) / 1000.0
        logo_y = 800 - elapsed_time * credits_speed
        if logo_y < credits_logo_target_y:
            logo_y = credits_logo_target_y
        credits_logo_rect.centery = logo_y
        credits_y = 800 - elapsed_time * credits_speed

        font = pygame.font.SysFont(None, 60)
        for i, line in enumerate(credits_text):
            text_surface = font.render(line, True, (255, 255, 255))
            text_rect = text_surface.get_rect(center=(400, credits_y + i * 80 + 200))
            screen.blit(text_surface, text_rect)

        screen.blit(credits_logo, credits_logo_rect)

        if credits_y + len(credits_text) * 80 < -50:
            fade_to_black()
            state = "menu"
            credits_y = 800
            credits_logo_rect.centery = 800

    pygame.display.flip()
    clock.tick(60)

pygame.quit()