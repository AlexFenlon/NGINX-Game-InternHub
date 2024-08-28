import pygame
from settings import ANIMATION_SPEED, TILE_SIZE


class Entity(pygame.sprite.Sprite):
    def __init__(self, pos, frames, groups, world_rect):
        super().__init__(groups)
        self.frame_index = 0
        self.frames = frames
        self.facing_direction = 'down'
        self.direction = pygame.math.Vector2()
        self.speed = 250
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
        self.frame_index += ANIMATION_SPEED * dt
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
    def __init__(self, pos, frames, groups, world_rect):
        super().__init__(pos, frames, groups, world_rect)
        self.team = []
        self.is_team_member = False
        self.current_character = None
        self.dialogs = [
            "Hello! I am a character. Press 'E' to interact.",
            "This is the second line of dialog.",
            "This is the third line of dialog."
        ]
        self.current_dialog_index = 0
        self.speech_bubble = None
        self.speech_bubble_start_time = None
        self.stop_moving = False
        self.following_leader = None  # Track the leader this character is following

    def interact(self):
        # Get the current dialog based on the current index
        return self.dialogs[self.current_dialog_index]

    def next_dialog(self):
        # Cycle to the next dialog
        self.current_dialog_index = (self.current_dialog_index + 1) % len(self.dialogs)

    def input(self):
        if self == self.current_character:
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

            self.direction = input_vector.normalize() if input_vector.length() > 0 else pygame.math.Vector2()

    def interact(self):
        # Allow the current character to make others follow them
        for character in self.current_character.team:
            if pygame.sprite.collide_rect(self.current_character, character):
                character.start_following(self.current_character)
                return f"{character} is now following {self.current_character}"

        return self.dialogs[self.current_dialog_index]

    def update(self, dt):
        super().update(dt)

        if self.speech_bubble and self.speech_bubble_start_time:
            if pygame.time.get_ticks() - self.speech_bubble_start_time > 5000:
                self.speech_bubble = None
                self.speech_bubble_start_time = None

        # If following a leader, adjust the movement
        if self.following_leader:
            self.follow(self.following_leader, dt)

    def follow(self, leader, dt):
        # Calculate the direction towards the leader
        direction = pygame.math.Vector2(leader.rect.center) - pygame.math.Vector2(self.rect.center)
        distance = direction.length()

        if distance > leader.trail_distance:
            # Move towards the leader if far enough away, but don't get too close
            self.direction = direction.normalize()
            self.rect.center += self.direction * self.speed * dt

        # Sync the animation frame with the leader for consistent appearance
        self.frame_index = leader.frame_index
        self.image = self.frames[leader.get_state()][int(self.frame_index % len(self.frames[leader.get_state()]))]

    def start_following(self, leader):
        self.following_leader = leader
        print(f"{self} is now following {leader}.")

    def stop_following(self):
        self.following_leader = None
        print(f"{self} stopped following their leader.")