import os
import gc
import time
import pygame as pg

from config import WINDOW_WIDTH, WINDOW_HEIGHT, FPS, TITLE
from scenes.menu_scene import MenuScene
from scenes.dress_scene import DressScene
from scenes.result_scene import ResultScene
from scenes.login_scene import LoginScene
from db import DB


class Game:
    def __init__(self):
        pg.init()
        self.w, self.h = WINDOW_WIDTH, WINDOW_HEIGHT
        self.screen = pg.display.set_mode((self.w, self.h))
        pg.display.set_caption(TITLE)
        self.clock = pg.time.Clock()
        self.running = True
        self.is_fullscreen = False

        # Infos utilisateur (remplies après connexion)
        self.current_user_id = None
        self.current_username = None

        # --- SCENE MANAGER ---
        # Scène de départ : LOGIN
        self.scene = None
        self.set_scene("login")

    # Méthode unique pour changer de scène
    def set_scene(self, name, *args):
        if name == "login":
            self.scene = LoginScene(self)

        elif name == "menu":
            # Infos utilisateur (remplies après connexion)
            self.current_user_id = None
            self.current_username = None

            # Scène initiale : connexion
            self.scene = LoginScene(self)


        elif name == "dress":
            mannequin, theme = args
            self.scene = DressScene(self, mannequin, theme)

        elif name == "result":
            mannequin, theme, outfit, worn_garments = args
            self.scene = ResultScene(self, mannequin, theme, outfit, worn_garments)

        else:
            raise ValueError(f"Scène inconnue: {name}")

    # Optionnel : tu peux garder tes anciens goto_*, mais ils deviennent juste des alias
    def goto_menu(self):
        self.set_scene("menu")

    def goto_dress(self, mannequin, theme):
        self.set_scene("dress", mannequin, theme)

    def goto_result(self, mannequin, theme, outfit, worn_garments):
        self.set_scene("result", mannequin, theme, outfit, worn_garments)

    def cleanup(self):
        """Nettoyage à la fermeture."""
        try:
            DB.close()

            gc.collect()
            time.sleep(0.5)

            # ⚠️ IMPORTANT :
            # Si tu veux garder les comptes utilisateur, NE SUPPRIME PAS la DB.
            # Commente/supprime ce bloc quand tu voudras conserver les users.
            db_path = os.path.join("data", "game.db")
            if os.path.exists(db_path):
                os.remove(db_path)
                print("data/game.db supprimé.")
        except Exception as e:
            print(f"Erreur lors du cleanup : {e}")

    def toggle_fullscreen(self):
        self.is_fullscreen = not self.is_fullscreen
        flags = pg.FULLSCREEN if self.is_fullscreen else 0
        self.screen = pg.display.set_mode((self.w, self.h), flags)

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.running = False
                elif event.type == pg.KEYDOWN and (
                    event.key == pg.K_F11
                    or (event.key == pg.K_RETURN and (event.mod & pg.KMOD_ALT))
                ):
                    self.toggle_fullscreen()
                else:
                    self.scene.handle_event(event)

            self.scene.update(dt)
            self.scene.draw(self.screen)
            pg.display.flip()

        self.cleanup()
        pg.quit()


if __name__ == "__main__":
    Game().run()
