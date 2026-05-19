import pygame as pg


class Scene:
    """Classe abstraite dont héritent toutes les scènes du jeu.

    Chaque scène représente un écran : login, menu, habillage, résultat, etc.
    La boucle principale dans Game appelle handle_event → update → draw à chaque frame.
    """

    def __init__(self, game):
        self.game = game

    def handle_event(self, event):
        """Traite un événement pygame (clic, touche, scroll…)."""
        pass

    def update(self, dt):
        """Met à jour la logique de la scène. dt = secondes depuis la dernière frame."""
        pass

    def draw(self, screen):
        """Dessine tous les éléments visuels de la scène."""
        pass
