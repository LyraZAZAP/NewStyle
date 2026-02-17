# ========================================
# WIDGETS D'INTERFACE UTILISATEUR
# Composants réutilisables (boutons, etc.)
# ========================================

# === IMPORTS ===
import pygame as pg  # Pygame importé sous le nom pg (bibliothèque de jeu)


# === CLASSE BOUTON ===
class Button:  # Widget simple de bouton cliquable
    def __init__(self, rect, text, on_click):
        """Initialise un bouton avec sa position, son texte et sa fonction de clic."""
        self.rect = pg.Rect(rect)  # Crée un rectangle pygame (x, y, width, height)
        self.text = text  # Texte affiché sur le bouton
        self.on_click = on_click  # Fonction appelée quand on clique sur le bouton
        self.font = pg.font.SysFont(None, 28)  # Police pour le texte (taille 28)

    def draw(self, surf):
        """Dessine le bouton sur la surface (écran) fournie."""
        # Dessine le fond du bouton (rectangle gris clair)
        pg.draw.rect(surf, (220, 220, 230), self.rect, border_radius=20)
        # Dessine la bordure du bouton (couleur violet foncé, épaisseur 5)
        pg.draw.rect(surf, (179, 0, 248), self.rect, 5, border_radius=20)
        # Rend le texte avec la police
        label = self.font.render(self.text, True, (179, 0, 248))
        # Centre le texte dans le rectangle du bouton
        surf.blit(label, label.get_rect(center=self.rect.center))

    def handle(self, event):
        """Gère les événements pygame pour ce bouton (clics)."""
        # Vérifie si on a cliqué avec le bouton gauche de la souris
        if event.type == pg.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos):
            # Appelle la fonction associée au clic
            self.on_click()