import pygame
import time
import math
from bullet import Bullet
from tank import Tank

class EnemyTank(Tank):
    def __init__(self, x, y, image_t, bullet_image, target_player):
        super().__init__(x, y, image_t, bullet_image)
        self.target_player = target_player
        self.speed = 0  # стандартная скорость врага 1,5
        self.move_delay = 0.4
        self.last_move_time = time.time()
        self.min_distance = 50 

    def update(self, player, bullet_group):
        moved = False
        distance_x = abs(self.rect.centerx - player.rect.centerx)
        distance_y = abs(self.rect.centery - player.rect.centery)

        if distance_x > distance_y:
            if self.rect.centerx < player.rect.centerx and distance_x > self.min_distance:
                self.rect.x += self.speed
                self.direction = 90
                moved = True
            elif self.rect.centerx > player.rect.centerx and distance_x > self.min_distance:
                self.rect.x -= self.speed
                self.direction = 270
                moved = True
        else:
            if self.rect.centery < player.rect.centery and distance_y > self.min_distance:
                self.rect.y += self.speed
                self.direction = 180
                moved = True
            elif self.rect.centery > player.rect.centery and distance_y > self.min_distance:
                self.rect.y -= self.speed
                self.direction = 0
                moved = True

        # Поворот танка
        self.image = pygame.transform.rotate(self.image_t, -self.direction)
        old_center = self.rect.center
        self.rect = self.image.get_rect(center=old_center)

        # --- Проверка "видит ли он игрока прямо перед собой"
        sees_player = False
        if self.direction == 0 and self.rect.centerx == player.rect.centerx and self.rect.centery > player.rect.centery:
            sees_player = True
        elif self.direction == 180 and self.rect.centerx == player.rect.centerx and self.rect.centery < player.rect.centery:
            sees_player = True
        elif self.direction == 90 and self.rect.centery == player.rect.centery and self.rect.centerx < player.rect.centerx:
            sees_player = True
        elif self.direction == 270 and self.rect.centery == player.rect.centery and self.rect.centerx > player.rect.centerx:
            sees_player = True

        # --- Если видит, стреляет
        if sees_player and time.time() - self.last_shot_time >= self.shot_delay:
            self.shoot(bullet_group)
            self.last_shot_time = time.time()