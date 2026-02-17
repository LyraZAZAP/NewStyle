# ========================================
# CLASSE DE BASE POUR TOUTES LES SCÈNES
# Les scènes sont les différents écrans du jeu
# ========================================

# === IMPORTS ===
import pygame as pg  # Pygame importé sous le nom pg (bibliothèque de jeu)


# === CLASSE DE BASE ===
class Scene:  # Classe abstraite (modèle) pour toutes les scènes du jeu
    def __init__(self, game):
        """Initialise une scène avec une référence au jeu."""
        self.game = game  # Stocke la référence vers l'objet jeu principal

    def handle_event(self, event):
        """Traite un événement pygame (clic souris, touche clavier, etc.)."""
        pass  # Chaque scène concrète implémente sa propre logique

    def update(self, dt):
        """Met à jour la logique de la scène chaque frame."""
        # dt = delta time (temps écoulé depuis la dernière frame en secondes)
        pass  # Chaque scène concrète implémente sa propre logique

    def draw(self, screen):
        """Dessine tutti les éléments visuels de la scène."""
        # screen = surface pygame où dessiner (l'écran du jeu)
        pass  # Chaque scène concrète implémente sa propre logique