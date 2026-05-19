import pygame as pg


class Button:
    """Bouton cliquable avec texte centré."""

    def __init__(self, rect, text, on_click):
        self.rect     = pg.Rect(rect)
        self.text     = text
        self.on_click = on_click
        self.font     = pg.font.SysFont(None, 28)

    def draw(self, surf):
        pg.draw.rect(surf, (220, 220, 230), self.rect, border_radius=20)
        pg.draw.rect(surf, (10, 104, 255),  self.rect, 5, border_radius=20)
        label = self.font.render(self.text, True, (10, 104, 255))
        surf.blit(label, label.get_rect(center=self.rect.center))

    def handle(self, event):
        if event.type == pg.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos):
            self.on_click()
