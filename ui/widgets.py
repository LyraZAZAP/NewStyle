import pygame as pg  # wrapper pygame importé sous le nom pg


class Button:  # Widget simple de bouton
    def __init__(self, rect, text, on_click):  # rect: tuple/rect, text: label, on_click: callable
        self.rect = pg.Rect(rect)  # stocke le rectangle du bouton (x,y,w,h)
        self.text = text  # texte affiché sur le bouton
        self.on_click = on_click  # fonction appelée au clic
        self.font = pg.font.SysFont(None, 28)  # police par défaut, taille 28


    def draw(self, surf):  # Dessine le bouton sur la surface `surf`
        pg.draw.rect(surf, (220,220,230), self.rect, border_radius = 10)  # fond clair arrondi
        pg.draw.rect(surf, (208,161,255), self.rect, 2, border_radius = 20)  # contour plus foncé
        label = self.font.render(self.text, True, (208,161,255))  # rend le texte en couleur sombre
        surf.blit(label, label.get_rect(center=self.rect.center))  # centre le label dans le rect


    def handle(self, event):  # Gère les événements pygame pour le bouton
        if event.type == pg.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos):  # clic dans le rect ?
            self.on_click()  # appelle le callback associé