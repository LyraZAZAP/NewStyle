# ========================================
# SCÈNE D'INSCRIPTION (REGISTER)
# Permet au nouvel utilisateur de créer un compte
# ========================================

# === IMPORTS ===
import os  # Pour parcourir les dossiers d'avatars
import pygame as pg  # Pygame pour l'affichage et les événements
from scenes.base_scene import Scene  # Classe de base pour les scènes
from ui.widgets import Button  # Widget bouton réutilisable
from db import DB  # Base de données - création utilisateur

# === CONFIGURATION ===
AVATAR_DIR = "assets/avatars"  # Dossier contenant les avatars disponibles


class RegisterScene(Scene):
    """Écran d'inscription avec champs username/display_name/password et sélection d'avatar."""
    
    def __init__(self, game):
        super().__init__(game)
        self.title_font = pg.font.SysFont(None, 56) # Police pour le titre de la scène
        self.font = pg.font.SysFont(None, 28) # Police pour les champs et messages

        # charge le background spécifique à l'inscription (assets/backgrounds/register.png)
        try:
            self.bg = pg.image.load("assets/backgrounds/register.png")
            self.bg = self.bg.convert_alpha() if self.bg.get_alpha() is not None else self.bg.convert()
            self.bg = pg.transform.smoothscale(self.bg, (self.game.w, self.game.h))
        except Exception:
            self.bg = None

        # Champs
        self.username_rect = pg.Rect(340, 210, 340, 45) # Rectangle pour le champ username
        self.display_name_rect = pg.Rect(340, 270, 340, 45) 
        self.password_rect = pg.Rect(340, 330, 340, 45)
        self.active_field = "username"

        self.username = "" # Identifiant de connexion (sans espaces, min 3 caractères)
        self.display_name = "" # Pseudo affiché dans le jeu (peut contenir des espaces, min 3 caractères)
        self.password = "" # Mot de passe (min 6 caractères) - ne sera pas affiché en clair dans le champ, mais stocké hashé dans la DB
        self.message = "" # Message d'erreur ou de succès à afficher à l'utilisateur après une tentative d'inscription

        # Avatars
        self.avatars = self._load_avatars() 
        self.avatar_index = 0 

        # Boutons
        self.buttons = []

        def prev_avatar():
            if self.avatars:
                self.avatar_index = (self.avatar_index - 1) % len(self.avatars)

        def next_avatar():
            if self.avatars:
                self.avatar_index = (self.avatar_index + 1) % len(self.avatars)

        def do_register():
            # Prépare les valeurs
            username_val = self.username.strip() 
            display_name_val = self.display_name.strip()
            password_val = self.password.strip()

            # Avatar sélectionné (ou None)
            avatar_path = None
            if self.avatars:
                avatar_path = self.avatars[self.avatar_index]

            # BASE DE DONNÉES : créer un nouvel utilisateur dans la table users
            # Appel DB : create_user(username, display_name, password, avatar_path)
            ok, msg = DB.create_user(username_val, display_name_val, password_val, avatar_path)
            self.message = msg

            if ok:
                # Connexion automatique après inscription
                # BASE DE DONNÉES : authentifier automatiquement l'utilisateur qu'on vient de créer
                ok2, msg2, user = DB.authenticate(username_val, password_val)
                if ok2 and user:
                    self.game.current_user_id = user.get("id")
                    self.game.current_username = user.get("display_name")
                    self.game.current_avatar = user.get("avatar_path")
                    self.game.goto_menu()
                else:
                    self.message = msg2

        def back():
            self.game.goto_login()

        self.buttons.append(Button((340, 420, 160, 50), "< AVANT", prev_avatar)) 
        self.buttons.append(Button((520, 420, 160, 50), "SUIVANT >", next_avatar))
        self.buttons.append(Button((340, 480, 340, 50), "Créer le compte", do_register))
        self.buttons.append(Button((340, 540, 340, 45), "Retour", back))

    def _load_avatars(self):
        if not os.path.isdir(AVATAR_DIR): # Si le dossier n'existe pas, retourne une liste vide
            return [] #le retour en liste vide 
        files = []
        for f in os.listdir(AVATAR_DIR): # Parcourt les fichiers du dossier
            if f.lower().endswith((".png", ".jpg", ".jpeg")): 
                files.append(os.path.join(AVATAR_DIR, f))
        files.sort()
        return files

    def _draw_input(self, screen, rect, label, value, active=False, password=False):
        bg = (255, 255, 255)
        border = (100, 150, 255) if active else (30, 30, 60)
        pg.draw.rect(screen, bg, rect, border_radius=8)
        pg.draw.rect(screen, border, rect, 2, border_radius=8)

        shown = ("*" * len(value)) if (password and value) else value # montre des étoiles pour le mot de passe, sinon le texte normal
        if not shown:
            shown = label
            color = (140, 140, 140)
        else:
            color = (30, 30, 60)

        text = self.font.render(shown, True, color)
        screen.blit(text, (rect.x + 12, rect.y + 10))

    def draw(self, screen):
        # affiche le background si disponible sinon fond uni
        if self.bg:
            screen.blit(self.bg, (0, 0))
        else:
            screen.fill((40, 40, 60))

        title = self.title_font.render("Inscription", True, (255, 255, 255)) #création du titre de la scène d'inscription 
        screen.blit(title, title.get_rect(center=(self.game.w // 2, 120))) # Positionne le titre en haut de l'écran, centré à l'horizontale

        self._draw_input(screen, self.username_rect, "Identifiant", self.username, self.active_field == "username")
        self._draw_input(screen, self.display_name_rect, "Pseudo affichage", self.display_name, self.active_field == "display_name")
        self._draw_input(screen, self.password_rect, "Mot de passe", self.password, self.active_field == "password", password=True)

        # Aperçu avatar
        if self.avatars:
            path = self.avatars[self.avatar_index] # Chemin de l'avatar sélectionné
            img = pg.image.load(path) # Charge l'image de l'avatar sélectionné
            img = img.convert_alpha() if img.get_alpha() is not None else img.convert() # Redimensionne l'avatar pour l'affichage (96x96 pixels)
            img = pg.transform.smoothscale(img, (96, 96)) # Redimensionne l'avatar pour l'affichage (96x96 pixels)
            screen.blit(img, (240, 420)) # Affiche l'avatar à gauche des boutons de navigation

        for b in self.buttons:
            b.draw(screen)

        if self.message:
            msg = self.font.render(self.message, True, (255, 220, 120)) # Affiche le message d'erreur ou de succès en bas de l'écran
            screen.blit(msg, (340, 600)) # Positionne le message sous les boutons

    def update(self, dt):
        pass

    def handle_event(self, event):
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1: # Clic gauche dans un champ de texte pour le sélectionner 
            if self.username_rect.collidepoint(event.pos): # Si clic dans le champ username, active ce champ
                self.active_field = "username" 
            elif self.display_name_rect.collidepoint(event.pos): # Si clic dans le champ display_name, active ce champ
                self.active_field = "display_name"
            elif self.password_rect.collidepoint(event.pos): # Si clic dans le champ password, active ce champ
                self.active_field = "password"

        if event.type == pg.KEYDOWN:
            if event.key == pg.K_TAB:
                order = ["username", "display_name", "password"]
                self.active_field = order[(order.index(self.active_field) + 1) % 3]
                return

            if event.key == pg.K_BACKSPACE:
                if self.active_field == "username":
                    self.username = self.username[:-1]
                elif self.active_field == "display_name":
                    self.display_name = self.display_name[:-1]
                else:
                    self.password = self.password[:-1]
                return

            ch = event.unicode
            if ch and ch.isprintable():
                if self.active_field == "username":
                    if len(self.username) < 24 and ch != " ":
                        self.username += ch
                elif self.active_field == "display_name":
                    if len(self.display_name) < 24:
                        self.display_name += ch
                else:
                    if len(self.password) < 32:
                        self.password += ch

        for b in self.buttons:
            b.handle(event)
