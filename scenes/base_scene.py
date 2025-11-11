import pygame as pg  # wrapper pygame importé sous le nom pg


class Scene:  # Classe de base pour toutes les scènes (écran) du jeu
    def __init__(self, game):  # game: instance de l'objet principal du jeu
        self.game = game  # référence vers le jeu pour accéder aux ressources et état


    def handle_event(self, event):  # Doit traiter un événement pygame (clic, touche, etc.)
        pass  # implémenté par les sous-classes si nécessaire


    def update(self, dt):  # Met à jour la logique de la scène (dt = delta time en secondes)
        pass  # implémenté par les sous-classes


    def draw(self, screen):  # Dessine la scène sur la surface `screen`
        pass  # implémenté par les sous-classes