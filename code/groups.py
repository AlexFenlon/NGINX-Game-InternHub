import pygame
from settings import WINDOW_WIDTH, WINDOW_HEIGHT

class AllSprites(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.offset = pygame.math.Vector2()

    def draw(self, surface):
        for sprite in self.sprites():
            # Blit each sprite with the camera offset
            surface.blit(sprite.image, sprite.rect.topleft + self.offset)

    def set_camera(self, player_rect, world_rect):
        # Calculate the camera position
        camera_x = -player_rect.centerx + WINDOW_WIDTH // 2
        camera_y = -player_rect.centery + WINDOW_HEIGHT // 2

        # Ensure the camera does not go out of the world boundaries
        camera_x = max(camera_x, -(world_rect.width - WINDOW_WIDTH))
        camera_x = min(camera_x, 0)
        camera_y = max(camera_y, -(world_rect.height - WINDOW_HEIGHT))
        camera_y = min(camera_y, 0)

        self.offset = pygame.math.Vector2(camera_x, camera_y)
