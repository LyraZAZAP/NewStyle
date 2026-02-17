import os
import pygame as pg
from scenes.base_scene import Scene
from ui.widgets import Button
from db import DB

AVATAR_DIR = "assets/avatars"

class RegisterScene(Scene):
    def __init__(self, game):
        super().__init__(game)
        self.title_font = pg.font.SysFont(None, 56)
        self.font = pg.font.SysFont(None, 28)

        # charge le background spécifique à l'inscription (assets/backgrounds/register.png)
        try:
            self.bg = pg.image.load("assets/backgrounds/register.png")
            self.bg = self.bg.convert_alpha() if self.bg.get_alpha() is not None else self.bg.convert()
            self.bg = pg.transform.smoothscale(self.bg, (self.game.w, self.game.h))
        except Exception:
            self.bg = None

        # Champs
        self.login_rect = pg.Rect(340, 210, 340, 45)
        self.pseudo_rect = pg.Rect(340, 270, 340, 45)
        self.password_rect = pg.Rect(340, 330, 340, 45)
        self.active_field = "login"

        self.login = ""
        self.pseudo = ""
        self.password = ""
        self.message = ""

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
            login_val = self.login.strip() or self.pseudo.strip()
            display_name = self.pseudo.strip() or login_val
            password_val = self.password

            # Avatar sélectionné (ou None)
            avatar_path = None
            if self.avatars:
                avatar_path = self.avatars[self.avatar_index]

            # Appel DB : create_user(login, display_name, password, avatar_path)
            ok, msg = DB.create_user(login_val, display_name, password_val, avatar_path)
            self.message = msg

            if ok:
                # Connexion automatique après inscription
                ok2, msg2, user = DB.authenticate(login_val, password_val)
                if ok2 and user:
                    self.game.current_user_id = user.get("id")
                    self.game.current_username = user.get("display_name")
                    self.game.current_avatar = user.get("avatar_path")
                    self.game.goto_menu()
                else:
                    self.message = msg2

        def back():
            self.game.goto_login()

        self.buttons.append(Button((340, 420, 160, 50), "< Avatar", prev_avatar))
        self.buttons.append(Button((520, 420, 160, 50), "Avatar >", next_avatar))
        self.buttons.append(Button((340, 480, 340, 50), "Créer le compte", do_register))
        self.buttons.append(Button((340, 540, 340, 45), "Retour", back))

    def _load_avatars(self):
        if not os.path.isdir(AVATAR_DIR):
            return []
        files = []
        for f in os.listdir(AVATAR_DIR):
            if f.lower().endswith((".png", ".jpg", ".jpeg")):
                files.append(os.path.join(AVATAR_DIR, f))
        files.sort()
        return files

    def _draw_input(self, screen, rect, label, value, active=False, password=False):
        bg = (255, 255, 255)
        border = (100, 150, 255) if active else (30, 30, 60)
        pg.draw.rect(screen, bg, rect, border_radius=8)
        pg.draw.rect(screen, border, rect, 2, border_radius=8)

        shown = ("*" * len(value)) if (password and value) else value
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

        title = self.title_font.render("Inscription", True, (255, 255, 255))
        screen.blit(title, title.get_rect(center=(self.game.w // 2, 120)))

        self._draw_input(screen, self.login_rect, "Identifiant (login)", self.login, self.active_field == "login")
        self._draw_input(screen, self.pseudo_rect, "Pseudo", self.pseudo, self.active_field == "pseudo")
        self._draw_input(screen, self.password_rect, "Mot de passe", self.password, self.active_field == "password", password=True)

        # Aperçu avatar
        if self.avatars:
            path = self.avatars[self.avatar_index]
            img = pg.image.load(path)
            img = img.convert_alpha() if img.get_alpha() is not None else img.convert()
            img = pg.transform.smoothscale(img, (96, 96))
            screen.blit(img, (240, 420))

        for b in self.buttons:
            b.draw(screen)

        if self.message:
            msg = self.font.render(self.message, True, (255, 220, 120))
            screen.blit(msg, (340, 600))

    def update(self, dt):
        pass

    def handle_event(self, event):
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            if self.login_rect.collidepoint(event.pos):
                self.active_field = "login"
            elif self.pseudo_rect.collidepoint(event.pos):
                self.active_field = "pseudo"
            elif self.password_rect.collidepoint(event.pos):
                self.active_field = "password"

        if event.type == pg.KEYDOWN:
            if event.key == pg.K_TAB:
                order = ["login", "pseudo", "password"]
                self.active_field = order[(order.index(self.active_field) + 1) % 3]
                return

            if event.key == pg.K_BACKSPACE:
                if self.active_field == "login":
                    self.login = self.login[:-1]
                elif self.active_field == "pseudo":
                    self.pseudo = self.pseudo[:-1]
                else:
                    self.password = self.password[:-1]
                return

            ch = event.unicode
            if ch and ch.isprintable():
                if self.active_field == "login":
                    if len(self.login) < 24 and ch != " ":
                        self.login += ch
                elif self.active_field == "pseudo":
                    if len(self.pseudo) < 24:
                        self.pseudo += ch
                else:
                    if len(self.password) < 32:
                        self.password += ch

        for b in self.buttons:
            b.handle(event)
