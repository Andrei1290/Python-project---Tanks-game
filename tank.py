import pygame
import time
from bullet import Bullet
from smoke import Smoke

class Tank(pygame.sprite.Sprite):
    def __init__(self, x, y, image_t, bullet_image, fire_sound=None):
        super().__init__()
        original_image = pygame.image.load(image_t).convert_alpha()
        self.image_t = pygame.transform.scale(original_image, (80, 80))
        self.image = self.image_t
        self.rect = self.image.get_rect(center=(x, y))
        self.direction = 0

        # Движение
        self.step_size = 10
        self.move_delay = 100
        self.last_move_time = 0

        # Стрельба
        self.last_shot_time = 0
        self.shot_delay = 3
        self.bullet_image = bullet_image
        self.health = 3
        self.fire_sound = fire_sound

        # Дым при низком здоровье
        self.smoke_delay = 0.5
        self.last_smoke_time = 0

    def check_collision(self, walls, enemies=None):
        for wall in walls:
            if self.rect.colliderect(wall.rect):
                return True
        if enemies:
            for enemy in enemies:
                if self.rect.colliderect(enemy.rect) and enemy.alive():
                    return True
        return False

    def update(self, keys, bullet_group, walls, enemies=None, smoke_group=None):
        now = pygame.time.get_ticks()

        if now - self.last_move_time >= self.move_delay:
            original_rect = self.rect.copy()

            if keys[pygame.K_w]:
                self.rect.y -= self.step_size
                self.direction = 0
            elif keys[pygame.K_s]:
                self.rect.y += self.step_size
                self.direction = 180
            elif keys[pygame.K_a]:
                self.rect.x -= self.step_size
                self.direction = 270
            elif keys[pygame.K_d]:
                self.rect.x += self.step_size
                self.direction = 90

            if self.check_collision(walls, enemies):
                self.rect = original_rect
            else:
                self.rect.x = max(0, min(self.rect.x, 800 - self.rect.width))
                self.rect.y = max(0, min(self.rect.y, 800 - self.rect.height))
                self.last_move_time = now

        # Поворот танка
        self.image = pygame.transform.rotate(self.image_t, -self.direction)
        old_center = self.rect.center
        self.rect = self.image.get_rect(center=old_center)

        # Стрельба
        if keys[pygame.K_SPACE] and time.time() - self.last_shot_time >= self.shot_delay:
            self.shoot(bullet_group)
            self.last_shot_time = time.time()

        # Спавн дыма при низком здоровье
        if self.health == 1 and smoke_group is not None:
            if time.time() - self.last_smoke_time >= self.smoke_delay:
                smoke = Smoke(self.rect.centerx, self.rect.centery)
                smoke_group.add(smoke)
                self.last_smoke_time = time.time()

    def shoot(self, bullet_group):
        bullet = Bullet(self.rect.centerx, self.rect.centery, self.direction, self.bullet_image)
        bullet.owner = self
        bullet_group.add(bullet)
        if self.fire_sound:
            self.fire_sound.play()

    def take_damage(self, bullet_group):
        for bullet in bullet_group:
            if bullet.owner != self and self.rect.colliderect(bullet.rect):
                self.health -= 1
                print(f"Игрок ранен! Осталось жизней: {self.health}")
                bullet.kill()
                if self.health <= 0:
                    print("Игрок уничтожен!")
                    self.kill()