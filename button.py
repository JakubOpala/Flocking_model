import pygame

class Button:
    def __init__(self, x, y, width, height, text, action):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.action = action
        self.clicked = False

    def draw(self, screen):
        pygame.draw.rect(screen, (200, 200, 200), self.rect)
        pygame.draw.rect(screen, (0, 0, 0), self.rect, 2)

        font = pygame.font.Font(None, 36)
        text_surface = font.render(self.text, True, (0, 0, 0))
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def check_click(self, event):
        click = False

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.clicked = True

        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.clicked and self.rect.collidepoint(event.pos):
                click = True
            self.clicked = False
        
        return click