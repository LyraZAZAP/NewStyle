# Scène de connexion

import pygame as pg
from scenes.base_scene import Scene
from ui.widgets import Button
from repositories import UserRepo


class LoginScene(Scene):
    """Écran de connexion : champs username/password et boutons."""

    def __init__(self, game):
        super().__init__(game)
        self.title_font = pg.font.SysFont(None, 56)
        self.font       = pg.font.SysFont(None, 28)

        try:
            bg = pg.image.load("assets/backgrounds/login.png")
            bg = bg.convert_alpha() if bg.get_alpha() is not None else bg.convert()
            self.bg = pg.transform.smoothscale(bg, (self.game.w, self.game.h))
        except Exception:
            self.bg = None

        self.username_rect = pg.Rect(340, 220, 340, 45)
        self.password_rect = pg.Rect(340, 290, 340, 45)
        self.active_field  = "username"

        self.username = ""
        self.password = ""
        self.message  = ""

        self.buttons = [
            Button((340, 360, 160, 50), "Connexion",  self._attempt_login),
            Button((520, 360, 160, 50), "Inscription", self.game.goto_register),
            Button((340, 430, 340, 45), "Retour menu", self.game.goto_menu),
        ]

    def _attempt_login(self):
        user = UserRepo.authenticate(self.username, self.password)
        if user:
            self.game.current_user_id  = user.id
            self.game.current_username = user.display_name
            self.game.current_avatar   = user.avatar_path
            self.game.goto_menu()
        else:
            self.message = "Identifiants incorrects."

    def _draw_input(self, screen, rect, label, value, active=False, password=False):
        border = (100, 150, 255) if active else (30, 30, 60)
        pg.draw.rect(screen, (255, 255, 255), rect, border_radius=800)
        pg.draw.rect(screen, border,          rect, 2, border_radius=800)

        shown = ("*" * len(value)) if (password and value) else value
        if shown:
            color = (30, 30, 60)
        else:
            shown = label
            color = (140, 140, 140)  # placeholder en gris

        screen.blit(self.font.render(shown, True, color), (rect.x + 12, rect.y + 10))

    def draw(self, screen):
        if self.bg:
            screen.blit(self.bg, (0, 0))
        else:
            screen.fill((40, 40, 60))

        title = self.title_font.render("Connexion", True, (255, 255, 255))
        screen.blit(title, title.get_rect(center=(self.game.w // 2, 140)))

        self._draw_input(screen, self.username_rect, "Pseudo",       self.username,
                         active=(self.active_field == "username"))
        self._draw_input(screen, self.password_rect, "Mot de passe", self.password,
                         active=(self.active_field == "password"), password=True)

        for b in self.buttons:
            b.draw(screen)

        if self.message:
            screen.blit(self.font.render(self.message, True, (255, 220, 120)), (340, 500))

        help_txt = self.font.render("TAB pour changer de champ, ENTRÉE pour se connecter", True, (30, 30, 60))
        screen.blit(help_txt, (250, 610))

    def update(self, dt):
        pass  # écran statique, aucune logique à mettre à jour

    def handle_event(self, event):
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            self._handle_click(event.pos)
        elif event.type == pg.KEYDOWN:
            self._handle_keydown(event)
        for b in self.buttons:
            b.handle(event)

    def _handle_click(self, pos):
        if self.username_rect.collidepoint(pos):
            self.active_field = "username"
        elif self.password_rect.collidepoint(pos):
            self.active_field = "password"

    def _handle_keydown(self, event):
        if event.key == pg.K_TAB:
            self.active_field = "password" if self.active_field == "username" else "username"
            return
        if event.key == pg.K_RETURN:
            self._attempt_login()
            return
        if event.key == pg.K_BACKSPACE:
            self._delete_char()
            return
        self._type_char(event.unicode)

    def _delete_char(self):
        if self.active_field == "username":
            self.username = self.username[:-1]
        else:
            self.password = self.password[:-1]

    def _type_char(self, ch):
        if not ch or not ch.isprintable():
            return
        if self.active_field == "username":
            if len(self.username) < 24 and ch != " ":
                self.username += ch
        elif len(self.password) < 32:
            self.password += ch
