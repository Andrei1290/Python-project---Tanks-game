import pygame
import time
from bullet import Bullet

class Tank(pygame.sprite.Sprite):
    def __init__(self, x, y, image_t, bullet_image):
        super().__init__()
        original_image = pygame.image.load(image_t).convert_alpha()
        self.image_t = pygame.transform.scale(original_image, (80, 80))  # увеличили танк
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

    def update(self, keys, bullet_group):
        now = pygame.time.get_ticks()

        if now - self.last_move_time >= self.move_delay:
            if keys[pygame.K_w]:
                self.rect.y -= self.step_size
                self.direction = 0
                self.last_move_time = now
            elif keys[pygame.K_s]:
                self.rect.y += self.step_size
                self.direction = 180
                self.last_move_time = now
            elif keys[pygame.K_a]:
                self.rect.x -= self.step_size
                self.direction = 270
                self.last_move_time = now
            elif keys[pygame.K_d]:
                self.rect.x += self.step_size
                self.direction = 90
                self.last_move_time = now

        # Поворот танка
        self.image = pygame.transform.rotate(self.image_t, -self.direction)
        old_center = self.rect.center
        self.rect = self.image.get_rect(center=old_center)

        # Стрельба
        if keys[pygame.K_SPACE] and time.time() - self.last_shot_time >= self.shot_delay:
            self.shoot(bullet_group)
            self.last_shot_time = time.time()

    def shoot(self, bullet_group):
        bullet = Bullet(self.rect.centerx, self.rect.centery, self.direction, self.bullet_image)
        bullet.owner = self
        bullet_group.add(bullet)

    def take_damage(self, bullet_group):
        for bullet in bullet_group:
            if bullet.owner != self and self.rect.colliderect(bullet.rect):
                self.health -= 1
                print(f"Игрок ранен! Осталось жизней: {self.health}")
                bullet.kill()
                if self.health <= 0:
                    print("Игрок уничтожен!")
                    self.kill()
