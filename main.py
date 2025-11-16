import os  # pour supprimer le fichier game.db
import pygame as pg  # wrapper pygame
from config import WINDOW_WIDTH, WINDOW_HEIGHT, FPS, TITLE, BACKGROUND_COLOR  # constantes de configuration
from scenes.menu_scene import MenuScene  # écran menu
from scenes.dress_scene import DressScene  # écran d'habillage
from scenes.result_scene import ResultScene  # écran de résultat


class Game:  # Classe principale du jeu : gère la boucle, la fenêtre et la scène active
    def __init__(self):
        pg.init()  # initialise pygame
        self.w, self.h = WINDOW_WIDTH, WINDOW_HEIGHT  # taille de la fenêtre
        self.screen = pg.display.set_mode((self.w, self.h))  # crée la surface principale
        pg.display.set_caption(TITLE)  # titre de la fenêtre
        self.clock = pg.time.Clock()  # horloge pour contrôler la cadence
        self.scene = MenuScene(self)  # scène initiale (menu)
        self.running = True  # drapeau pour la boucle principale


    def goto_menu(self):  # change la scène active vers le menu
        self.scene = MenuScene(self)


    def goto_dress(self, mannequin, theme):  # ouvre l'écran d'habillage
        self.scene = DressScene(self, mannequin, theme)


    def goto_result(self, mannequin, theme, outfit):  # ouvre l'écran de résultat
        self.scene = ResultScene(self, mannequin, theme, outfit)


    def cleanup(self):
        """Supprime le fichier game.db à la fermeture du jeu."""
        try:
            if os.path.exists("game.db"):
                os.remove("game.db")
                print("game.db supprimé.")
        except Exception as e:
            print(f"Erreur lors de la suppression de game.db : {e}")


    def run(self):  # Boucle principale du jeu
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0  # temps écoulé en secondes depuis la frame précédente
            for event in pg.event.get():  # récupère les événements pygame
                if event.type == pg.QUIT:  # fenêtre fermée -> arrêter
                    self.running = False
                else:
                    self.scene.handle_event(event)  # transmettre l'événement à la scène
            self.scene.update(dt)  # mettre à jour la scène
            self.scene.draw(self.screen)  # dessiner la scène
            pg.display.flip()  # actualiser l'affichage
        self.cleanup()  # nettoyer avant de quitter
        pg.quit()  # quitter pygame proprement


if __name__ == "__main__":
    from db import DB  # initialise la base de données au démarrage (crée fichiers si besoin)
    Game().run()  # lance la boucle principale