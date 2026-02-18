# ========================================
# SCÈNE DE CONNEXION (LOGIN)
# Permet à l'utilisateur de se connecter à son compte
# ========================================

# === IMPORTS ===
import pygame as pg  # Pygame pour l'affichage et les événements
from scenes.base_scene import Scene  # Classe de base pour les scènes
from ui.widgets import Button  # Widget bouton réutilisable
from db import DB  # Base de données - authentification


class LoginScene(Scene):
    """Écran de login avec champs username/password et boutons."""
    
    def __init__(self, game):
        super().__init__(game)
        self.title_font = pg.font.SysFont(None, 56)
        self.font = pg.font.SysFont(None, 28)
        # charge le background spécifique au login (assets/backgrounds/login.png)
        try:
            self.bg = pg.image.load("assets/backgrounds/login.png")
            # gérer transparence si besoin
            self.bg = self.bg.convert_alpha() if self.bg.get_alpha() is not None else self.bg.convert() # Redimensionne le background pour qu'il remplisse tout l'écran (game.w x game.h)
            self.bg = pg.transform.smoothscale(self.bg, (self.game.w, self.game.h)) # Redimensionne le background pour qu'il remplisse tout l'écran (game.w x game.h)
        except Exception:
            self.bg = None

        # Champs input (rectangles cliquables)
        self.username_rect = pg.Rect(340, 220, 340, 45) # Rectangle pour le champ username
        self.password_rect = pg.Rect(340, 290, 340, 45) # Rectangle pour le champ password
        self.active_field = "username"  # ou "password"

        self.username = ""
        self.password = ""
        self.message = ""

        # Boutons (même style que ton MenuScene)
        self.buttons = []

        def do_login():
            # BASE DE DONNÉES : vérifier les identifiants de l'utilisateur
            ok, msg, user = DB.authenticate(self.username, self.password)
            self.message = msg
            if ok and user:
                self.game.current_user_id = user.get("id")
                self.game.current_username = user.get("display_name")
                self.game.current_avatar = user.get("avatar_path")
                self.game.goto_menu()

        def do_register():
            # Rediriger vers la scène d'inscription séparée
            self.game.goto_register()

        def go_back():
            self.game.goto_menu()

        self.buttons.append(Button((340, 360, 160, 50), "Connexion", do_login)) 
        self.buttons.append(Button((520, 360, 160, 50), "Inscription", do_register))
        self.buttons.append(Button((340, 430, 340, 45), "Retour menu", go_back))

    # --- Utils affichage ---
    def _draw_input(self, screen, rect, label, value, active=False, password=False):
        # fond
        bg = (255, 255, 255) 
        border = (100, 150, 255) if active else (30, 30, 60) # bordure bleue si actif, sinon sombre
        pg.draw.rect(screen, bg, rect, border_radius=800) # fond blanc avec coins arrondis
        pg.draw.rect(screen, border, rect, 2, border_radius=800) # bordure avec coins arrondis

        # texte
        shown = ("*" * len(value)) if (password and value) else value
        if not shown:
            shown = label
            color = (140, 140, 140) # placeholder en gris clair
        else:
            color = (30, 30, 60) # texte saisi en sombre

        text = self.font.render(shown, True, color)
        screen.blit(text, (rect.x + 12, rect.y + 10))

    def draw(self, screen):
        # affiche le background si disponible sinon fond uni
        if self.bg:
            screen.blit(self.bg, (0, 0))
        else:
            screen.fill((40, 40, 60))

        # Titre
        title = self.title_font.render("Connexion", True, (255, 255, 255))
        screen.blit(title, title.get_rect(center=(self.game.w // 2, 140))) # Positionne le titre en haut de l'écran, centré à l'horizontale

        # Champs
        self._draw_input(
            screen, self.username_rect, "Pseudo", self.username, # Affiche "Pseudo" comme placeholder si le champ est vide, sinon affiche le texte saisi
            active=(self.active_field == "username"), password=False # Affiche le champ username, avec une bordure bleue si c'est le champ actif
        )
        self._draw_input(
            screen, self.password_rect, "Mot de passe", self.password,
            active=(self.active_field == "password"), password=True
        )

        # Boutons
        for b in self.buttons:
            b.draw(screen)

        # Message
        if self.message:
            msg = self.font.render(self.message, True, (255, 220, 120))
            screen.blit(msg, (340, 500))

        # Aide rapide
        help_txt = self.font.render("TAB pour changer de champ, ENTRÉE pour se connecter", True, (30, 30, 60))
        screen.blit(help_txt, (250, 610)) # Positionne l'aide rapide en bas de l'écran, aligné à gauche

    def update(self, dt):
        pass

    def handle_event(self, event):
        # Clique : activer champ
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            if self.username_rect.collidepoint(event.pos):
                self.active_field = "username"
            elif self.password_rect.collidepoint(event.pos):
                self.active_field = "password"

        # Clavier : écrire
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_TAB:
                self.active_field = "password" if self.active_field == "username" else "username"
                return

            if event.key == pg.K_RETURN:
                # Enter => tentative de connexion
                # BASE DE DONNÉES : authentifier l'utilisateur avec le username et le mot de passe
                ok, msg, user = DB.authenticate(self.username, self.password)
                self.message = msg
                if ok and user:
                    self.game.current_user_id = user.get("id")
                    self.game.current_username = user.get("display_name")
                    self.game.current_avatar = user.get("avatar_path")
                    self.game.goto_menu()
                    
                return

            if event.key == pg.K_BACKSPACE: # Supprimer le dernier caractère du champ actif
                if self.active_field == "username":
                    self.username = self.username[:-1]
                else:
                    self.password = self.password[:-1]
                return

            # Ajout de caractère (limite + éviter caractères chelous)
            ch = event.unicode
            if ch and ch.isprintable():
                if self.active_field == "username":
                    if len(self.username) < 24 and ch != " ":
                        self.username += ch
                else:
                    if len(self.password) < 32:
                        self.password += ch

        # Transmettre aux boutons
        for b in self.buttons:
            b.handle(event)
