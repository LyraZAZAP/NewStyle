import os  # pour supprimer le fichier game.db
import gc  # pour forcer la libération mémoire
import time  # pour ajouter un délai
import sqlite3  # pour fermer les connexions
import pygame as pg  # wrapper pygame
from config import WINDOW_WIDTH, WINDOW_HEIGHT, FPS, TITLE, BACKGROUND_COLOR  # constantes de configuration
from scenes.menu_scene import MenuScene  # écran menu
from scenes.dress_scene import DressScene  # écran d'habillage
from scenes.result_scene import ResultScene  # écran de résultat
from db import DB  # pour fermer la connexion à la base


class Game:  # Classe principale du jeu : gère la boucle, la fenêtre et la scène active
    def __init__(self):
        pg.init()  # initialise pygame
        self.w, self.h = WINDOW_WIDTH, WINDOW_HEIGHT  # taille de la fenêtre
        # utiliser SCALED pour faciliter le plein écran sans changer la logique interne
        self.screen = pg.display.set_mode((self.w, self.h), pg.SCALED)
        pg.display.set_caption(TITLE)  # titre de la fenêtre
        self.clock = pg.time.Clock()  # horloge pour contrôler la cadence
        self.scene = MenuScene(self)  # scène initiale (menu)
        self.running = True  # drapeau pour la boucle principale
        self.is_fullscreen = False  # état courant du plein écran


    def goto_menu(self):  # change la scène active vers le menu
        self.scene = MenuScene(self)


    def goto_dress(self, mannequin, theme):  # ouvre l'écran d'habillage
        self.scene = DressScene(self, mannequin, theme)


    def goto_result(self, mannequin, theme, outfit, worn_garments):  # ouvre l'écran de résultat
        self.scene = ResultScene(self, mannequin, theme, outfit, worn_garments)


    def cleanup(self):
        """Supprime le fichier game.db du dossier data à la fermeture du jeu."""
        try:
            # Fermer la connexion à la base de données
            DB.close()
            
            # Forcer la libération mémoire pour relâcher les verrous fichier
            gc.collect()
            time.sleep(0.5)  # Attendre que les verrous se relâchent
            
            db_path = os.path.join("data", "game.db")
            if os.path.exists(db_path):
                os.remove(db_path)
                print("data/game.db supprimé.")
        except Exception as e:
            print(f"Erreur lors de la suppression de data/game.db : {e}")


    def toggle_fullscreen(self):
        """Bascule fenêtre <-> plein écran sans changer la résolution logique."""
        self.is_fullscreen = not self.is_fullscreen
        flags = pg.SCALED | (pg.FULLSCREEN if self.is_fullscreen else 0)
        self.screen = pg.display.set_mode((self.w, self.h), flags)


    def run(self):  # Boucle principale du jeu
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0  # temps écoulé en secondes depuis la frame précédente
            for event in pg.event.get():  # récupère les événements pygame
                if event.type == pg.QUIT:  # fenêtre fermée -> arrêter
                    self.running = False
                # toggle plein écran: F11 ou Alt+Entrée
                elif event.type == pg.KEYDOWN and (event.key == pg.K_F11 or (event.key == pg.K_RETURN and (event.mod & pg.KMOD_ALT))):
                    self.toggle_fullscreen()
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