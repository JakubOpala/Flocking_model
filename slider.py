import pygame
import sys

class Slider:
    def __init__(self, x, y, length, min_value, max_value, default_value, label):
        self.rect = pygame.Rect(x, y, length, 10)
        self.handle_rect = pygame.Rect(x + default_value / max_value * length - 5, y - 5, 20, 20)
        self.min_value = min_value
        self.max_value = max_value
        self.value = default_value
        self.label = label

    def update_value(self):
        self.value = (self.handle_rect.x - self.rect.x) / self.rect.width * (self.max_value - self.min_value)

    def draw(self, screen):
        pygame.draw.rect(screen, (200, 200, 200), self.rect)
        pygame.draw.rect(screen, (0, 0, 0), self.rect, 2)
        pygame.draw.rect(screen, (150, 150, 150), self.handle_rect)
        pygame.draw.rect(screen, (0, 0, 0), self.handle_rect, 2)

        font = pygame.font.Font(None, 24)
        text_surface = font.render(f"{self.label}: {self.value:.2f}", True, (0, 0, 0))
        screen.blit(text_surface, (self.rect.x, self.rect.y - 30))