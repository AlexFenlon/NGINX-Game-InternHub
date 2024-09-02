import os
import time

import pygame
from settings import WINDOW_WIDTH, WINDOW_HEIGHT
from entities import Character, GifAnimation
from groups import AllSprites
from support import all_character_import
from npc_behaviors import PathBehavior, WanderBehavior

base_dir = os.path.dirname(os.path.abspath(__file__))
base_dir = os.path.dirname(base_dir)
TILE_SIZE = 32

class Game:
    def __init__(self):
        pygame.init()
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("NGINX Game")
        self.clock = pygame.time.Clock()
        self.setup()

    def import_assets(self):
        self.overworld_frames = {
            'characters': all_character_import(base_dir, 'graphics', 'characters')
        }

        self.world_image_path = os.path.join(base_dir, 'graphics', 'map', 'world.png')
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

        gif1_path = os.path.join(base_dir, 'graphics', 'gifs', 'f5logo.gif')
        gif1_size = (52, 32)  # Set your desired size
        gif1_pos = (TILE_SIZE * 40.2, TILE_SIZE * 30.5)
        self.gif1_animation = GifAnimation(gif1_pos, gif1_path, gif1_size, self.all_sprites)

        gif2_path = os.path.join(base_dir, 'graphics', 'gifs', 'scroll.gif')
        gif2_size = (52, 32)  # Set your desired size
        gif2_pos = (TILE_SIZE * 46.2, TILE_SIZE * 30.5)
        self.gif2_animation = GifAnimation(gif2_pos, gif2_path, gif2_size, self.all_sprites)

        gif3_path = os.path.join(base_dir, 'graphics', 'gifs', 'nginxlogo.gif')
        gif3_size = (52, 32)  # Set your desired size
        gif3_pos = (TILE_SIZE * 40.2, TILE_SIZE * 40.5)
        self.gif3_animation = GifAnimation(gif3_pos, gif3_path, gif3_size, self.all_sprites)

        gif4_path = os.path.join(base_dir, 'graphics', 'gifs', 'ogbluescreen.gif')
        gif4_size = (52, 32)  # Set your desired size
        gif4_pos = (TILE_SIZE * 46.2, TILE_SIZE * 40.5)
        self.gif4_animation = GifAnimation(gif4_pos, gif4_path, gif4_size, self.all_sprites)


        alex_dialogs = [
            "Hi, I'm Alex! An Engineering Intern at F5/NGINX!",
            "Since a young age, I loved to tinker and mod software!",
            "I'm on the NGINX Ingress Controller Team.",
            "My biggest additions is on IP listener and Telemetry.",
            "Oh wait! I need to go to the conference room!"
        ]

        spencer_dialogs = [
            "My name Spencer and I'm an Intern at F5/NGINX",
            "I'm on the NGINX Agent Team.",
            "I've had the chance to work on some interesting projects.",
            "And this is how we navigate through F5 as interns!"
        ]

        stephen_dialogs = [
            "Hey, I'm Stephen, another engineering intern at f5/NGINX.",
            "Graduating this year from Munster Technological University?",
            "I started at f5 in february of this year.",
            "My experience at NGINX/F5 has been like no other",
            "Im on the delivery eng. team, under Sergey nad my buddy Sean!",
            "Ive worked on some interesting/challenging projects",
            "I'm late! The lads are waiting in the conference room"
        ]

        self.alex = Character((TILE_SIZE * 34, TILE_SIZE * 18), self.overworld_frames['characters']['alex'],
                              self.all_sprites, self.world_rect, alex_dialogs)
        self.spencer = Character((TILE_SIZE * 39, TILE_SIZE * 65), self.overworld_frames['characters']['spencer'],
                                 self.all_sprites, self.world_rect, spencer_dialogs)
        self.stephen = Character((TILE_SIZE * 7, TILE_SIZE * 95), self.overworld_frames['characters']['stephen'],
                                 self.all_sprites, self.world_rect, stephen_dialogs)

        # Define the path for each NPC
        npc_paths = {
            'moving_character': [
                (TILE_SIZE * 18, TILE_SIZE * 8),  # Starting position slightly higher
                (TILE_SIZE * 35, TILE_SIZE * 10),  # Move further right
                (TILE_SIZE * 35, TILE_SIZE * 100),  # Move much further down
                (TILE_SIZE * 18, TILE_SIZE * 100),  # Move left
                (TILE_SIZE * 18, TILE_SIZE * 8),  # Move up back to the starting position
            ]
        }

        # Add NPCs with PathBehavior
        self.npc1 = Character((TILE_SIZE * 11, TILE_SIZE * 36), self.overworld_frames['characters']['blond'],
                              self.all_sprites, self.world_rect, ["I'm NPC1!"], is_npc=True)
        self.npc2 = Character((TILE_SIZE * 11, TILE_SIZE * 16), self.overworld_frames['characters']['hat_girl'],
                              self.all_sprites, self.world_rect, ["I'm NPC2!"], is_npc=True)
        self.npc3 = Character((TILE_SIZE * 47, TILE_SIZE * 26), self.overworld_frames['characters']['purple_girl'],
                              self.all_sprites, self.world_rect, ["I'm NPC3!"], is_npc=True)
        self.npc4 = Character((TILE_SIZE * 11, TILE_SIZE * 56), self.overworld_frames['characters']['straw'],
                              self.all_sprites, self.world_rect, ["I'm NPC3!"], is_npc=True)
        self.npc5 = Character((TILE_SIZE * 41, TILE_SIZE * 46), self.overworld_frames['characters']['grass_boss'],
                              self.all_sprites, self.world_rect, ["I'm NPC3!"], is_npc=True)

        # Example for a new character with WanderBehavior
        self.moving_character = Character(
            (TILE_SIZE * 18, TILE_SIZE * 8),  # Starting position near the top-left of the central cubicle
            self.overworld_frames['characters']['npc1'],
            self.all_sprites,
            self.world_rect,
            is_npc=True  # Ensure it's marked as an NPC
        )
        path_behavior = PathBehavior(npc_paths['moving_character'])
        self.moving_character.set_behavior(path_behavior)

        self.current_character = self.alex
        self.alex.current_character = self.alex
        self.camera_target = self.alex

    def switch_character(self, new_character):
        if new_character == self.current_character:
            return

        if self.current_character:
            # Define the target location where the current character should move
            target_positions = {
                self.alex: (TILE_SIZE * 31, TILE_SIZE * 109),
                self.spencer: (TILE_SIZE * 29, TILE_SIZE * 110),
                self.stephen: (TILE_SIZE * 27, TILE_SIZE * 111)
            }

            target_position = target_positions.get(self.current_character, None)
            if target_position:
                self.current_character.move_to(target_position)
                self.facing_direction = 'down'

        # Switch the current character
        self.current_character = new_character
        self.camera_target = new_character
        self.all_sprites.set_camera(new_character.rect, self.world_rect)

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
                            # Define the size of the speech bubble
                            bubble_width, bubble_height = 300, 100
                            self.current_character.speech_bubble = pygame.Surface((bubble_width, bubble_height),
                                                                                  pygame.SRCALPHA)

                            lime = (0, 255, 0)
                            white = (255, 255, 255)
                            draw_rounded_rect(self.current_character.speech_bubble, white,
                                              self.current_character.speech_bubble.get_rect(), 10, border_color=lime,
                                              border_width=5)

                            font = pygame.font.Font(None, 36)
                            max_text_width = bubble_width - 20  # Adjust according to your bubble size and padding

                            # Wrap the text to fit within the bubble
                            lines = wrap_text(dialogue, font, max_text_width)

                            # Render each line separately
                            y_offset = 10
                            for line in lines:
                                text = font.render(line, True, (0, 0, 0))
                                self.current_character.speech_bubble.blit(text, (10, y_offset))
                                y_offset += font.get_height()
                    elif key == pygame.K_RETURN:  # Handle Enter key for dialog cycling
                        if self.current_character.speech_bubble:
                            # Go to the next dialog
                            self.current_character.next_dialog()
                            dialogue = self.current_character.interact()

                            # Update the speech bubble with the new dialog
                            bubble_width, bubble_height = 300, 100
                            self.current_character.speech_bubble = pygame.Surface((bubble_width, bubble_height),
                                                                                  pygame.SRCALPHA)

                            lime = (0, 255, 0)
                            white = (255, 255, 255)
                            draw_rounded_rect(self.current_character.speech_bubble, white,
                                              self.current_character.speech_bubble.get_rect(), 10, border_color=lime,
                                              border_width=5)

                            font = pygame.font.Font(None, 36)
                            max_text_width = bubble_width - 20  # Adjust according to your bubble size and padding

                            # Wrap the text to fit within the bubble
                            lines = wrap_text(dialogue, font, max_text_width)

                            # Render each line separately
                            y_offset = 10
                            for line in lines:
                                text = font.render(line, True, (0, 0, 0))
                                self.current_character.speech_bubble.blit(text, (10, y_offset))
                                y_offset += font.get_height()
                    elif key == pygame.K_f:
                        for character in [self.alex, self.spencer, self.stephen]:
                            print_character_location(character)
                    elif key == pygame.K_r:
                        if self.current_character.speech_bubble:
                            self.current_character.speech_bubble = None
                            self.current_character.speech_bubble_start_time = None
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
                # Update the position of the speech bubble to follow the player
                bubble_x = self.current_character.rect.centerx - self.current_character.speech_bubble.get_width() // 2
                bubble_y = self.current_character.rect.top - self.current_character.speech_bubble.get_height() - 10
                bubble_position = (bubble_x + self.all_sprites.offset.x, bubble_y + self.all_sprites.offset.y)

                # Draw the speech bubble
                self.display_surface.blit(self.current_character.speech_bubble, bubble_position)

            pygame.display.update()

def pixel_to_tile(pixel_pos, tile_size):
    return pixel_pos // tile_size

def print_character_location(character):
    # Get the pixel position of the character's center
    x_pixel, y_pixel = character.rect.center
    # Convert pixel position to tile coordinates
    x_tile = pixel_to_tile(x_pixel, TILE_SIZE)
    y_tile = pixel_to_tile(y_pixel, TILE_SIZE)
    # Print the location in TILE_SIZE * X format
    print(f"Character's Location: TILE_SIZE * {x_tile}, TILE_SIZE * {y_tile}")

def wrap_text(text, font, max_width):
    """Wrap text into multiple lines that fit within max_width."""
    words = text.split(' ')
    lines = []
    current_line = ""

    for word in words:
        # Check if adding the next word exceeds the max width
        test_line = current_line + word + " "
        if font.size(test_line)[0] <= max_width:
            current_line = test_line
        else:
            # If it exceeds, save the current line and start a new one
            lines.append(current_line.strip())
            current_line = word + " "

    # Add the last line
    if current_line:
        lines.append(current_line.strip())

    return lines

def draw_rounded_rect(surface, color, rect, radius, border_color=None, border_width=0):
    """Draws a rounded rectangle with optional border."""
    rect = pygame.Rect(rect)
    shape_surf = pygame.Surface(rect.size, pygame.SRCALPHA)

    # Draw the filled rounded rectangle
    pygame.draw.rect(shape_surf, color, shape_surf.get_rect(), border_radius=radius)

    if border_color and border_width > 0:
        pygame.draw.rect(shape_surf, border_color, shape_surf.get_rect(), border_radius=radius, width=border_width)

    surface.blit(shape_surf, rect.topleft)

if __name__ == '__main__':
    game = Game()
    game.run()
    pygame.display.update()