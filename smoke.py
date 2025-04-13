import pygame
import random

class Smoke(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        original_image = pygame.image.load("images/smoke.png").convert_alpha()
        self.image = pygame.transform.scale(original_image, (50, 50))
        self.rect = self.image.get_rect(center=(x, y))
        self.lifetime = 1000  # Время жизни - 1 секунда
        self.start_time = pygame.time.get_ticks()
        # Случайное смещение
        self.rect.x += random.randint(-20, 20)
        self.rect.y += random.randint(-20, 20)

    def update(self):
        # Проверяем, не истекло ли время жизни
        if pygame.time.get_ticks() - self.start_time > self.lifetime:
            self.kill()