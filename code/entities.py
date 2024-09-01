import itertools

import pygame
from npc_behaviors import Behavior


class Entity(pygame.sprite.Sprite):
    def __init__(self, pos, frames, groups, world_rect):
        super().__init__(groups)
        self.frame_index = 0
        self.frames = frames
        self.facing_direction = 'down'
        self.direction = pygame.math.Vector2()
        self.speed = 125
        self.animation_speed = 6
        self.image = self.frames[self.get_state()][self.frame_index]
        self.rect = self.image.get_rect(center=pos)
        self.following = []
        self.trail_distance = 100
        self.world_rect = world_rect

    def move(self, dt):
        movement = self.direction * self.speed * dt
        self.rect.center += movement

        # Ensure character stays within world boundaries
        if self.rect.left < self.world_rect.left:
            self.rect.left = self.world_rect.left
        if self.rect.right > self.world_rect.right:
            self.rect.right = self.world_rect.right
        if self.rect.top < self.world_rect.top:
            self.rect.top = self.world_rect.top
        if self.rect.bottom > self.world_rect.bottom:
            self.rect.bottom = self.world_rect.bottom

    def animate(self, dt):
        self.frame_index += self.animation_speed * dt
        self.image = self.frames[self.get_state()][int(self.frame_index % len(self.frames[self.get_state()]))]

    def get_state(self):
        moving = bool(self.direction.length_squared() > 0)
        if moving:
            if self.direction.x != 0:
                self.facing_direction = 'right' if self.direction.x > 0 else 'left'
            if self.direction.y != 0:
                self.facing_direction = 'down' if self.direction.y > 0 else 'up'
        return f"{self.facing_direction}{'' if moving else '_idle'}"

    def update(self, dt):
        if self.following:
            for follower in self.following:
                direction = pygame.math.Vector2(self.rect.center) - pygame.math.Vector2(follower.rect.center)
                distance = direction.length()
                if distance > follower.trail_distance:
                    follower.direction = direction.normalize() if direction.length() > 0 else pygame.math.Vector2()
                    follower.move(dt)
                else:
                    follower.direction = pygame.math.Vector2()

        self.move(dt)
        self.animate(dt)

class Character(Entity):
    def __init__(self, pos, frames, groups, world_rect, dialogs=None, is_npc=False):
        super().__init__(pos, frames, groups, world_rect)
        self.behavior = Behavior()
        self.team = []
        self.is_team_member = False
        self.current_character = None
        self.dialogs = dialogs if dialogs else ["Default dialog."]
        self.current_dialog_index = 0
        self.speech_bubble = None
        self.speech_bubble_start_time = None
        self.stop_moving = False
        self.following_leader = None
        self.target_position = None  # The target position the character should move toward
        self.reached_target = True  # Indicates whether the character has reached the target

        # Add these attributes for NPC-specific movement
        self.is_npc = is_npc
        self.original_y = self.rect.y
        self.movement_direction = 1
        self.movement_interval = 5000  # 5 seconds
        self.movement_distance = 5  # Move 5 pixels up and down
        self.last_movement_time = pygame.time.get_ticks()

    def set_behavior(self, behavior):
        self.behavior = behavior

    def move_to(self, target_position):
        self.target_position = pygame.math.Vector2(target_position)
        self.reached_target = False

    def interact(self):
        # Get the current dialog based on the current index
        return self.dialogs[self.current_dialog_index]

    def next_dialog(self):
        # Cycle to the next dialog
        self.current_dialog_index = (self.current_dialog_index + 1) % len(self.dialogs)

    def input(self):
        if self == self.current_character and self.reached_target:
            keys = pygame.key.get_pressed()
            input_vector = pygame.math.Vector2()

            if keys[pygame.K_w]:
                input_vector.y -= 1
            if keys[pygame.K_s]:
                input_vector.y += 1
            if keys[pygame.K_a]:
                input_vector.x -= 1
            if keys[pygame.K_d]:
                input_vector.x += 1


            # Determine speed and animation speed based on keys pressed
            if keys[pygame.K_LSHIFT] and keys[pygame.K_SPACE]:
                # Super sprint
                self.speed = 1000
                self.animation_speed = 24
            elif keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
                # Normal sprint
                self.speed = 250
                self.animation_speed = 12
            else:
                # Normal walking
                self.speed = 125
                self.animation_speed = 6

            self.direction = input_vector.normalize() if input_vector.length() > 0 else pygame.math.Vector2()

    def update(self, dt):
        if self.behavior:
            self.behavior.update(self, dt)

        if not self.reached_target and self.target_position:
            self.direction = self.target_position - pygame.math.Vector2(self.rect.center)
            if self.direction.length() < 5:
                self.rect.center = self.target_position
                self.direction = pygame.math.Vector2()
                self.reached_target = True
            else:
                self.direction = self.direction.normalize()

        super().update(dt)

        if self.is_npc:
            self.npc_up_down_movement()  # Apply the bobbing movement

        if self.speech_bubble and self.speech_bubble_start_time:
            if pygame.time.get_ticks() - self.speech_bubble_start_time > 5000:
                self.speech_bubble = None
                self.speech_bubble_start_time = None

        if self.following_leader:
            self.follow(self.following_leader, dt)

    def npc_up_down_movement(self):
        current_time = pygame.time.get_ticks()

        if self.movement_direction == 1:  # Moving down
            if current_time - self.last_movement_time >= self.movement_interval:
                self.rect.y += self.movement_distance
                self.movement_direction = -1  # Change direction to up
                self.last_movement_time = current_time  # Reset the timer for the delay before moving up

        elif self.movement_direction == -1:  # Wait before moving up
            if current_time - self.last_movement_time >= 500:  # 500ms delay before moving back up
                self.rect.y -= self.movement_distance
                self.movement_direction = 0  # Set to 0 to indicate waiting for the next cycle
                self.last_movement_time = current_time  # Reset the timer for the next movement cycle

        elif self.movement_direction == 0:  # Wait before starting the next cycle
            if current_time - self.last_movement_time >= self.movement_interval:
                self.movement_direction = 1  # Reset direction for the next cycle


class GifAnimation(pygame.sprite.Sprite):
    def __init__(self, pos, gif_path, size, groups):
        super().__init__(groups)
        self.frames = self.load_gif_frames(gif_path, size)
        self.frame_index = 0
        self.image = self.frames[self.frame_index] if self.frames else pygame.Surface((0, 0))
        self.rect = self.image.get_rect(topleft=pos)
        self.size = size  # Store the desired size

    def load_gif_frames(self, gif_path, size):
        frames = []
        try:
            gif = pygame.image.load(gif_path).convert_alpha()
            gif_width, gif_height = gif.get_size()


            width, height = size
            if width <= 0 or height <= 0:
                raise ValueError("Invalid frame size dimensions.")

            num_frames = gif_height // height
            extra_height = gif_height % height

            for i in range(num_frames):
                try:
                    rect = pygame.Rect(0, i * height, gif_width, height)
                    frame = gif.subsurface(rect).copy()
                    frame = pygame.transform.scale(frame, size)
                    frames.append(frame)
                except pygame.error as e:
                    print(f"Error extracting frame {i}: {e}")
                    break
        except pygame.error as e:
            print(f"Failed to load GIF: {e}")

        return frames

    def update(self, dt):
        if self.frames:
            self.frame_index += 12 * dt
            self.frame_index %= len(self.frames)  # Ensure frame_index wraps around
            self.image = self.frames[int(self.frame_index)]
            self.rect = self.image.get_rect(topleft=self.rect.topleft)  # Update rect position if needed

class PathBehavior:
    def __init__(self, path, speed=300):
        self.path = path
        self.current_target_index = 0
        self.speed = speed

    def update(self, character, dt):
        target_pos = pygame.math.Vector2(self.path[self.current_target_index])
        direction = target_pos - pygame.math.Vector2(character.rect.center)
        distance = direction.length()

        if distance < 5:  # If close enough to the target, move to the next point
            self.current_target_index = (self.current_target_index + 1) % len(self.path)
        else:
            character.direction = direction.normalize()
            character.rect.center += character.direction * self.speed * dt
