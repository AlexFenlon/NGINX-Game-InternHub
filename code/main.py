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

        TILE_SIZE = 32

        alex_dialogs = [
            "Hi, I'm Alex! Engineering Intern at F5/NGINX", # im a graduate software developer from MTU
            "Before University, I loved to tinker and mod software", #talk about playing around with tinkering with android devices and modding games
            "I'm on the NGINX Ingress Team.", #talk about what I do, what is unique what is ingress controller, what the team deos
            "I worked with Jim and Shaun on IP listener and Telemetry.", # expand on this talk about specific diffuclt issues (IP listener and telemety)
            "Oh wait! I need to go to the conference room!"
        ]

        spencer_dialogs = [
            "My name Spencer and I'm an Intern at F5/NGINX", # intro, college, internship since when and until when, speak about the various events held in the office
            "I'm on the NGINX Agent Team.", # What agent is, what its like working on the team, shoutout buddy and manager and rest of team
            "I've had the chance to work on some interesting projects." # briefly talk about one of security projects
            "And this is how we navigate through F5 as interns", # all together
        ]

        stephen_dialogs = [
            "Hey, I'm Stephen, yet another engineering intern (theres dozens of us).",
            "Graduating this year from munster Technological University?",
            "I have been passionate about tech from an early age.", # talk about building pc at 13
            "I am on the delivery engineering team",
            "I work under Sergey and my Mentor/Buddy Sean",
            "The rest of the team have been amazing to work with on my journey",
            "Im late! The lads are waiting in the conference room"
        ]

        self.alex = Character((TILE_SIZE * 34, TILE_SIZE * 18), self.overworld_frames['characters']['alex'],
                              self.all_sprites, self.world_rect, alex_dialogs)
        self.spencer = Character((TILE_SIZE * 39, TILE_SIZE * 65), self.overworld_frames['characters']['spencer'],
                                 self.all_sprites, self.world_rect,spencer_dialogs)
        self.stephen = Character((TILE_SIZE * 7, TILE_SIZE * 95), self.overworld_frames['characters']['stephen'],
                                 self.all_sprites, self.world_rect, stephen_dialogs)

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
                # Update the position of the speech bubble to follow the player
                bubble_x = self.current_character.rect.centerx - self.current_character.speech_bubble.get_width() // 2
                bubble_y = self.current_character.rect.top - self.current_character.speech_bubble.get_height() - 10
                bubble_position = (bubble_x + self.all_sprites.offset.x, bubble_y + self.all_sprites.offset.y)

                # Draw the speech bubble
                self.display_surface.blit(self.current_character.speech_bubble, bubble_position)

            pygame.display.update()


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