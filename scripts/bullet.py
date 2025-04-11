import pygame

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction, image_path):
        super().__init__()
        original_image = pygame.image.load(image_path).convert_alpha()
        self.image_orig = pygame.transform.scale(original_image, (64, 64))  # увеличили пулю
        self.image = pygame.transform.rotate(self.image_orig, -direction)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 7
        self.direction = direction
        self.owner = None

    def update(self):
        if self.direction == 0:
            self.rect.y -= self.speed
        elif self.direction == 90:
            self.rect.x += self.speed
        elif self.direction == 180:
            self.rect.y += self.speed
        elif self.direction == 270:
            self.rect.x -= self.speed

        if not pygame.display.get_surface().get_rect().colliderect(self.rect):
            self.kill()
