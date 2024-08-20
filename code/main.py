import os
import pygame
from settings import WINDOW_WIDTH, WINDOW_HEIGHT
from entities import Character
from groups import AllSprites
from support import all_character_import

class Game:
    def __init__(self):
        pygame.init()
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("NGINX Game")
        self.clock = pygame.time.Clock()
        self.setup()

    def import_assets(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        base_dir = os.path.dirname(base_dir)

        self.overworld_frames = {
            'characters': all_character_import(base_dir, 'graphics', 'characters')
        }

        self.world_image_path = os.path.join(base_dir, 'data', 'maps', 'world.png')
        try:
            self.world_image = pygame.image.load(self.world_image_path).convert_alpha()
        except pygame.error as e:
            print(f"Failed to load world image: {e}")

    def setup(self):
        self.all_sprites = AllSprites()
        self.import_assets()

        self.world_rect = self.world_image.get_rect()
        self.test_surface = pygame.Surface(self.world_rect.size)
        self.test_surface.blit(self.world_image, (0, 0))

        TILE_SIZE = 32

        self.alex = Character((TILE_SIZE * 2, TILE_SIZE * 2), self.overworld_frames['characters']['player'], self.all_sprites, self.world_rect)
        self.spencer = Character((TILE_SIZE * 4, TILE_SIZE * 2), self.overworld_frames['characters']['fire_boss'], self.all_sprites, self.world_rect)
        self.stephen = Character((TILE_SIZE * 6, TILE_SIZE * 2), self.overworld_frames['characters']['grass_boss'], self.all_sprites, self.world_rect)

        self.current_character = self.alex
        self.alex.current_character = self.alex
        self.camera_target = self.alex

    def switch_character(self, new_character):
        if new_character == self.current_character:
            return

        if self.current_character:
            if hasattr(self.current_character, 'team'):
                if new_character in self.current_character.team or not self.current_character.team:
                    self.current_character = new_character
                    new_character.current_character = new_character
                    if hasattr(new_character, 'rearrange_team'):
                        new_character.rearrange_team()
                    self.camera_target = new_character
                    self.all_sprites.set_camera(new_character.rect, self.world_rect)
                else:
                    print(f"{new_character} is not in the team of the current character.")
            else:
                self.current_character = new_character
                new_character.current_character = new_character
                self.camera_target = new_character
                self.all_sprites.set_camera(new_character.rect, self.world_rect)
        else:
            self.current_character = new_character
            new_character.current_character = new_character
            self.camera_target = new_character
            self.all_sprites.set_camera(new_character.rect, self.world_rect)

    def restart_game(self):
        self.setup()
        print("Game restarted.")

    def run(self):
        keypresses = {}
        while True:
            dt = self.clock.tick(60) / 1000
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if event.type == pygame.KEYDOWN:
                    key = event.key
                    if key in [pygame.K_1, pygame.K_2, pygame.K_3]:
                        if key in keypresses and pygame.time.get_ticks() - keypresses[key] < 500:
                            self.current_character.stop_moving = not self.current_character.stop_moving
                        else:
                            keypresses[key] = pygame.time.get_ticks()
                            if key == pygame.K_1:
                                self.switch_character(self.alex)
                            elif key == pygame.K_2:
                                self.switch_character(self.spencer)
                            elif key == pygame.K_3:
                                self.switch_character(self.stephen)
                    elif key == pygame.K_e:
                        dialogue = self.current_character.interact()
                        if self.current_character.speech_bubble is None:
                            self.current_character.speech_bubble = pygame.Surface((300, 100))
                            self.current_character.speech_bubble.fill((255, 255, 255))
                            font = pygame.font.Font(None, 36)
                            text = font.render(dialogue, True, (0, 0, 0))
                            self.current_character.speech_bubble.blit(text, (10, 10))
                            self.current_character.speech_bubble_start_time = pygame.time.get_ticks()
                    elif key == pygame.K_f:
                        for character in [self.alex, self.spencer, self.stephen]:
                            if pygame.sprite.collide_rect(self.current_character, character):
                                character.start_following(self.current_character)
                    elif key == pygame.K_r:
                        if self.current_character.speech_bubble:
                            self.current_character.speech_bubble = None
                            self.current_character.speech_bubble_start_time = None
                    elif key == pygame.K_c:
                        print("Chat option selected")
                    elif key == pygame.K_ESCAPE:
                        self.restart_game()

            if self.current_character and not self.current_character.stop_moving:
                self.current_character.input()

            self.all_sprites.update(dt)
            if self.camera_target:
                self.all_sprites.set_camera(self.camera_target.rect, self.world_rect)

            self.display_surface.fill((0, 0, 0))
            self.display_surface.blit(self.test_surface, self.all_sprites.offset)
            self.all_sprites.draw(self.display_surface)

            if self.current_character.speech_bubble:
                self.display_surface.blit(self.current_character.speech_bubble,
                                          (self.current_character.rect.x - 150, self.current_character.rect.y - 120))

            pygame.display.update()


if __name__ == '__main__':
    game = Game()
    game.run()
    pygame.display.update()
