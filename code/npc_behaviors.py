import pygame
import random


class Behavior:
    def update(self, entity, dt):
        pass


class PathBehavior(Behavior):
    def __init__(self, path, speed=100):
        self.path = path
        self.current_index = 0
        self.speed = speed
        self.target_position = self.path[self.current_index]

    def update(self, character, dt):
        if not self.path:
            return

        # Move towards the target position
        x_diff = self.target_position[0] - character.rect.centerx
        y_diff = self.target_position[1] - character.rect.centery
        distance = max(abs(x_diff), abs(y_diff))

        if distance < 1:  # Close enough to the target
            # Move to the next waypoint
            self.current_index = (self.current_index + 1) % len(self.path)
            self.target_position = self.path[self.current_index]
        else:
            # Move towards the target position
            x_velocity = (x_diff / distance) * self.speed * dt
            y_velocity = (y_diff / distance) * self.speed * dt
            character.rect.x += x_velocity
            character.rect.y += y_velocity

class WanderBehavior(Behavior):
    def __init__(self, direction_change_interval=3.0, wander_area=None, speed=100):
        self.direction_change_interval = direction_change_interval
        self.wander_area = wander_area
        self.speed = speed
        self.time_since_change = 0
        self.current_direction = pygame.Vector2(random.choice([1, -1]), random.choice([1, -1])).normalize()

    def update(self, character, dt):
        self.time_since_change += dt
        if self.time_since_change >= self.direction_change_interval:
            self.time_since_change = 0
            self.current_direction = pygame.Vector2(random.choice([1, -1]), random.choice([1, -1])).normalize()

        character.rect.x += self.current_direction.x * self.speed * dt
        character.rect.y += self.current_direction.y * self.speed * dt

        if self.wander_area:
            if character.rect.left < self.wander_area.left:
                character.rect.left = self.wander_area.left
                self.current_direction.x *= -1
            if character.rect.right > self.wander_area.right:
                character.rect.right = self.wander_area.right
                self.current_direction.x *= -1
            if character.rect.top < self.wander_area.top:
                character.rect.top = self.wander_area.top
                self.current_direction.y *= -1
            if character.rect.bottom > self.wander_area.bottom:
                character.rect.bottom = self.wander_area.bottom
                self.current_direction.y *= -1
