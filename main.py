# ========================================
# FICHIER PRINCIPAL DU JEU
# Point d'entrée - Contient la boucle principale et la navigation
# ========================================

# === IMPORTS SYSTÈME ===
import os  # Pour opérations système
import gc  # Garbage collector (nettoie la mémoire)
import time  # Pour gérer les délais
import pygame as pg  # Pygame - bibliothèque de jeu

# === IMPORTS CONFIGURATION ===
from config import WINDOW_WIDTH, WINDOW_HEIGHT, FPS, TITLE  # Paramètres du jeu

# === IMPORTS SCÈNES ===
from scenes.menu_scene import MenuScene  # Écran menu principal
from scenes.dress_scene import DressScene  # Écran habillage (principal)
from scenes.result_scene import ResultScene  # Écran résultat final
from scenes.login_scene import LoginScene  # Écran login
from scenes.register_scene import RegisterScene  # Écran inscription

# === IMPORTS AUTRES ===
from db import DB  # Base de données
from audio_manager import AudioManager  # Gestion des musiques
from repositories import UserRepo  # Repository pour les utilisateurs
from config import MUSIC_TRACKS  # Liste des fichiers musicaux


# ========================================
# CLASSE GAME - ORCHESTRATEUR PRINCIPAL
# Gère la fenêtre, les événements globaux et la navigation entre scènes
# ========================================
class Game:
    def __init__(self):
        pg.init()
        # Initialise le gestionnaire audio (mais ne le lance pas encore)
        self.audio = AudioManager(MUSIC_TRACKS, volume=0.2)
        # Ne pas lancer la musique ici - elle sera lancée seulement au menu

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
        assert self.scene is not None  # Pour le type checker - scene est toujours définie

        # `current_avatar` contient le chemin vers l'image à afficher
        self.current_avatar = None
        self.cached_avatar = None  # Avatar mis en cache pour éviter les rechargements

        # Exporte les utilisateurs en JSON à chaque démarrage
        UserRepo.export_to_json()

    # Méthode unique pour changer de scène
    def set_scene(self, name, *args):
        # Arrête la musique si on va vers connexion/inscription
        if name in ["login", "register"]:
            pg.mixer.music.stop()  # Arrête la musique
        
        # Lance la musique si on va vers menu ou habillage
        if name in ["menu", "dress"]:
            if self.audio and not self.audio.is_playing():  # Vérification audio + check si elle ne joue pas
                self.audio.play()
        
        # Navigue vers la bonne scène
        if name == "login":
            self.scene = LoginScene(self)

        elif name == "register":
            self.scene = RegisterScene(self)

        elif name == "menu":
            # Menu principal après connexion
            self.scene = MenuScene(self)

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
        
    def goto_login(self):
        """Retour à l'écran de connexion/inscription."""
        self.set_scene("login")
        self.cached_avatar = None  # Réinitialise le cache

    def goto_register(self):
        self.set_scene("register")

    def goto_dress(self, mannequin, theme):
        self.set_scene("dress", mannequin, theme)

    def goto_result(self, mannequin, theme, outfit, worn_garments):
        self.set_scene("result", mannequin, theme, outfit, worn_garments)

    def cleanup(self):
        """Nettoyage à la fermeture."""
        try:
            # BASE DE DONNÉES : fermer la connexion à la base de données
            DB.close()

            gc.collect()
            time.sleep(0.5)

            # ✅ MODIFICATION: Les comptes utilisateur sont maintenant conservés
            # La base de données est gardée entre les lancements du jeu
            # Les utilisateurs restent enregistrés d'une partie à l'autre
            # (Décommentez les lignes ci-dessous si vous voulez réinitialiser à chaque fois)
            
            # db_path = os.path.join("data", "game.db")
            # if os.path.exists(db_path):
            #     os.remove(db_path)
            #     print("data/game.db supprimé.")
        except Exception as e:
            print(f"Erreur lors du cleanup : {e}")

    def toggle_fullscreen(self):
        self.is_fullscreen = not self.is_fullscreen
        flags = pg.FULLSCREEN if self.is_fullscreen else 0
        self.screen = pg.display.set_mode((self.w, self.h), flags)

    def _draw_avatar(self):
        """Affiche l'avatar et le pseudo de l'utilisateur en bas à droite."""
        user_id = getattr(self, "current_user_id", None)
        avatar_path = getattr(self, "current_avatar", None)
        if user_id and avatar_path:
            try:
                # Charge et met en cache l'avatar une seule fois
                if self.cached_avatar is None or self.cached_avatar[1] != avatar_path:
                    avatar_img = pg.image.load(avatar_path)
                    avatar_img = avatar_img.convert_alpha() if avatar_img.get_alpha() is not None else avatar_img.convert()
                    avatar_img = pg.transform.smoothscale(avatar_img, (175, 175))
                    self.cached_avatar = (avatar_img, avatar_path)
                else:
                    avatar_img = self.cached_avatar[0]
                
                margin = 16
                aw, ah = avatar_img.get_width(), avatar_img.get_height()
                ax = self.screen.get_width() - margin - aw
                ay = self.screen.get_height() - margin - ah
                self.screen.blit(avatar_img, (ax, ay))

                # Affiche le pseudo centré au-dessus de l'avatar si présent
                username = getattr(self, "current_username", None)
                if username:
                    font = pg.font.SysFont(None, 22)
                    txt = font.render(username, True, (255, 255, 255))
                    pw, ph = txt.get_width(), txt.get_height()
                    px = ax + (aw - pw) // 2
                    py = ay - 6 - ph
                    self.screen.blit(txt, (px, py))
            except Exception:
                pass

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
                    if self.scene:
                        self.scene.handle_event(event)

            if self.scene:
                self.scene.update(dt)
                self.scene.draw(self.screen)
            self._draw_avatar()
            pg.display.flip()

        self.cleanup()
        pg.quit()


if __name__ == "__main__":
    Game().run()
