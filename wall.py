import pygame

class Wall(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.normal_image = pygame.image.load("images/normal_house.png").convert_alpha() # Нормальный дом
        self.damaged_image = pygame.image.load("images/damaged_house.png").convert_alpha() # Сломаный дом - при вытсреле по нему
        self.normal_image = pygame.transform.scale(self.normal_image, (80, 80))
        self.damaged_image = pygame.transform.scale(self.damaged_image, (80, 80))
        self.image = self.normal_image
        self.rect = self.image.get_rect(topleft=(x, y))
        # Состояние дома: 0 - нормальная, 1 - поврежденная
        self.state = 0

    def hit(self):
        """Обработка попадания пули"""
        if self.state == 0:
            # Если дом нормальный, меняем на поврежденный
            self.image = self.damaged_image
            self.state = 1
        elif self.state == 1:
            # Если дом поврежден, уничтожаем его
            self.kill()