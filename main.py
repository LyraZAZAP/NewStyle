# Point d'entrée du jeu — boucle principale et navigation entre scènes

import os
import sys
import gc
import time
import pygame as pg

# PyInstaller --onedir place tous les fichiers --add-data dans _internal/ (sys._MEIPASS).
# On met le CWD sur ce dossier pour que tous les chemins relatifs (assets, musics…) fonctionnent.
# game.db est géré séparément dans config.py — il est stocké dans le dossier du .exe.
if getattr(sys, 'frozen', False):
    os.chdir(sys._MEIPASS)

from config import WINDOW_WIDTH, WINDOW_HEIGHT, FPS, TITLE, MUSIC_TRACKS
from scenes.menu_scene     import MenuScene
from scenes.dress_scene    import DressScene
from scenes.result_scene   import ResultScene
from scenes.login_scene    import LoginScene
from scenes.register_scene import RegisterScene

_SCENES_WITHOUT_AUDIO_HUD = (LoginScene, RegisterScene)
from scenes.story_scene    import StoryScene
from scenes.wheel_scene    import WheelScene
from db                    import DB
from audio_manager         import AudioManager
from repositories          import UserRepo
from ui.widgets            import VolumeWidget


class Game:
    """Orchestrateur principal : fenêtre, boucle de jeu et navigation entre scènes."""

    def __init__(self):
        pg.init()
        self.audio = AudioManager(MUSIC_TRACKS, volume=0.2)

        self.w, self.h    = WINDOW_WIDTH, WINDOW_HEIGHT
        self.screen       = pg.display.set_mode((self.w, self.h))
        pg.display.set_caption(TITLE)
        self.clock        = pg.time.Clock()
        self.running      = True
        self.is_fullscreen = False

        # Infos utilisateur (remplies après connexion)
        self.current_user_id  = None
        self.current_username = None
        self.current_avatar   = None
        self.cached_avatar    = None  # cache pour éviter de recharger l'image à chaque frame

        self.volume_widget = VolumeWidget(self.audio)
        self.volume_widget.place(self.w, self.h)

        self.scene = None
        self.set_scene("login")

        UserRepo.export_to_json()

    # --- Navigation ---

    def set_scene(self, name, *args):
        if name in ("login", "register"):
            pg.mixer.music.stop()
        elif name in ("menu", "dress"):
            if self.audio and not self.audio.is_playing():
                self.audio.play()

        scenes = {
            "login":    lambda: LoginScene(self),
            "register": lambda: RegisterScene(self),
            "menu":     lambda: MenuScene(self),
            "story":    lambda: StoryScene(self, *args),
            "wheel":    lambda: WheelScene(self, *args),
            "dress":    lambda: DressScene(self, *args),
            "result":   lambda: ResultScene(self, *args),
        }
        if name not in scenes:
            raise ValueError(f"Scène inconnue : {name}")
        self.scene = scenes[name]()

    def goto_login(self):
        self.cached_avatar = None
        self.set_scene("login")

    def goto_register(self):         self.set_scene("register")
    def goto_menu(self):             self.set_scene("menu")
    def goto_story(self, m, t):      self.set_scene("story", m, t)
    def goto_wheel(self, m):         self.set_scene("wheel", m)
    def goto_dress(self, m, t):      self.set_scene("dress", m, t)

    def goto_result(self, mannequin, theme, outfit, worn_garments):
        self.set_scene("result", mannequin, theme, outfit, worn_garments)

    # --- Plein écran ---

    def toggle_fullscreen(self):
        self.is_fullscreen = not self.is_fullscreen
        flags = pg.FULLSCREEN if self.is_fullscreen else 0
        self.screen = pg.display.set_mode((self.w, self.h), flags)

    # --- Avatar HUD ---

    def _draw_avatar(self):
        """Affiche l'avatar et le pseudo en bas à droite de l'écran."""
        if not self.current_user_id or not self.current_avatar:
            return
        try:
            if self.cached_avatar is None or self.cached_avatar[1] != self.current_avatar:
                img = pg.image.load(self.current_avatar)
                img = img.convert_alpha() if img.get_alpha() is not None else img.convert()
                img = pg.transform.smoothscale(img, (175, 175))
                self.cached_avatar = (img, self.current_avatar)
            avatar_img = self.cached_avatar[0]

            margin = 16
            ax = self.screen.get_width()  - margin - avatar_img.get_width()
            ay = self.screen.get_height() - margin - avatar_img.get_height()
            self.screen.blit(avatar_img, (ax, ay))

            if self.current_username:
                font = pg.font.SysFont(None, 22)
                txt  = font.render(self.current_username, True, (255, 255, 255))
                self.screen.blit(txt, (ax + (avatar_img.get_width() - txt.get_width()) // 2, ay - 6 - txt.get_height()))
        except Exception:
            pass

    # --- Boucle principale ---

    def _audio_hud_visible(self):
        return self.scene and not isinstance(self.scene, _SCENES_WITHOUT_AUDIO_HUD)

    def _handle_event(self, event):
        if event.type == pg.QUIT:
            self.running = False
            return
        if event.type == pg.KEYDOWN and (
            event.key == pg.K_F11
            or (event.key == pg.K_RETURN and (event.mod & pg.KMOD_ALT))
        ):
            self.toggle_fullscreen()
            return
        if self.scene:
            if self._audio_hud_visible() and self.volume_widget.handle_event(event):
                return
            self.scene.handle_event(event)

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0

            for event in pg.event.get():
                self._handle_event(event)

            if self.scene:
                self.scene.update(dt)
                self.scene.draw(self.screen)
            self._draw_avatar()
            if self._audio_hud_visible():
                self.volume_widget.draw(self.screen)
            pg.display.flip()

        self._cleanup()
        pg.quit()

    def _cleanup(self):
        try:
            DB.close()
            gc.collect()
            time.sleep(0.5)
        except Exception as e:
            print(f"Erreur cleanup : {e}")


if __name__ == "__main__":
    Game().run()
