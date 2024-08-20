import pygame

class Sprite(pygame.sprite.Sprite):
    def __init__(self, position, image, group):
        super().__init__(group)
        self.image = image
