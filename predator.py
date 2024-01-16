import numpy as np
import pygame 
import sys
import math
import random

class Predator:
    def __init__(self, world_size):
        self.x  = world_size[0] / 2
        self.y  = world_size[1] / 2
        self.vx = 0
        self.vy = 0
        self.direction = np.array([1,0])
        self.world_size = world_size
        self.size = 1
        self.image = pygame.image.load('smakosz.png')

    def distance(self, bird):
        dx = abs(self.x - bird.x)
        dy = abs(self.y - bird.y)

        # periodic boundary conditions
        dx = min(dx, self.world_size[0] - dx)
        dy = min(dy, self.world_size[1] - dy)

        wrapped_distance = np.sqrt(dx**2 + dy**2)
        return wrapped_distance

    def dir(self):
        if self.vx**2 + self.vy**2 == 0:
            return self.direction
        return np.array([self.vx, self.vy]) / np.linalg.norm(np.array([self.vx, self.vy]))

    def move(self, keys):
        self.vx = 0
        self.vy = 0
        # Adjust the velocity based on arrow keys
        if keys[pygame.K_UP]:
            self.vy -= 5
        if keys[pygame.K_DOWN]:
            self.vy += 5
        if keys[pygame.K_LEFT]:
            self.vx -= 5
        if keys[pygame.K_RIGHT]:
            self.vx += 5

        # Update the direction
        self.direction = self.dir()

        # Update the position based on the velocity
        self.x += self.vx
        self.y += self.vy

        # Wrap around the world if needed
        self.x %= self.world_size[0]
        self.y %= self.world_size[1]
        
    def draw(self, screen):

        direction_angle = math.atan2(self.direction[1], self.direction[0])

        # Rotate the image
        rotated_image = pygame.transform.rotate(pygame.transform.scale(self.image, (40+self.size, 50+self.size)), -direction_angle)

        rect = rotated_image.get_rect(center=(self.x, self.y))

        # Blit the rotated image onto the screen
        screen.blit(rotated_image, rect.topleft)

    def eat(self, birds):

        birds_output = []

        for i, bird in enumerate(birds):
            if self.distance(bird) < self.size+15:
                self.size += 2
            else:
                birds_output.append(bird)
        
        return birds_output