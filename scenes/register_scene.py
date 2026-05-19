# Scène d'inscription

import os
import pygame as pg
from scenes.base_scene import Scene
from ui.widgets import Button
from repositories import UserRepo

AVATAR_DIR = "assets/avatars"


class RegisterScene(Scene):
    """Écran de création de compte : champs texte + sélection d'avatar."""

    def __init__(self, game):
        super().__init__(game)
        self.title_font = pg.font.SysFont(None, 56)
        self.font       = pg.font.SysFont(None, 28)

        try:
            bg = pg.image.load("assets/backgrounds/register.png")
            bg = bg.convert_alpha() if bg.get_alpha() is not None else bg.convert()
            self.bg = pg.transform.smoothscale(bg, (self.game.w, self.game.h))
        except Exception:
            self.bg = None

        self.username_rect     = pg.Rect(340, 210, 340, 45)
        self.display_name_rect = pg.Rect(340, 270, 340, 45)
        self.password_rect     = pg.Rect(340, 330, 340, 45)
        self.active_field      = "username"

        self.username     = ""
        self.display_name = ""
        self.password     = ""
        self.message      = ""

        self.avatars      = self._load_avatars()
        self.avatar_index = 0

        self.buttons = [
            Button((340, 420, 160, 50), "< AVANT",        lambda: self._shift_avatar(-1)),
            Button((520, 420, 160, 50), "SUIVANT >",      lambda: self._shift_avatar(+1)),
            Button((340, 480, 340, 50), "Créer le compte", self._do_register),
            Button((340, 540, 340, 45), "Retour",          self.game.goto_login),
        ]

    # --- Helpers internes ---

    def _shift_avatar(self, direction):
        if self.avatars:
            self.avatar_index = (self.avatar_index + direction) % len(self.avatars)

    def _load_avatars(self):
        if not os.path.isdir(AVATAR_DIR):
            return []
        files = sorted(
            os.path.join(AVATAR_DIR, f)
            for f in os.listdir(AVATAR_DIR)
            if f.lower().endswith((".png", ".jpg", ".jpeg"))
        )
        return files

    def _do_register(self):
        username_val     = self.username.strip()
        display_name_val = self.display_name.strip()
        password_val     = self.password

        if len(username_val) < 3:
            self.message = "Identifiant trop court (min 3)."
            return
        if len(display_name_val) < 3:
            self.message = "Pseudo trop court (min 3)."
            return
        if len(password_val) < 6:
            self.message = "Mot de passe trop court (min 6)."
            return

        avatar_path = self.avatars[self.avatar_index] if self.avatars else "assets/avatars/default.png"
        new_user    = UserRepo.create(username_val, display_name_val, password_val, avatar_path)

        if new_user:
            self.game.current_user_id  = new_user.id
            self.game.current_username = new_user.display_name
            self.game.current_avatar   = new_user.avatar_path
            UserRepo.export_to_json()
            self.game.goto_menu()
        else:
            self.message = "Cet identifiant existe déjà."

    def _draw_input(self, screen, rect, label, value, active=False, password=False):
        border = (100, 150, 255) if active else (30, 30, 60)
        pg.draw.rect(screen, (255, 255, 255), rect, border_radius=8)
        pg.draw.rect(screen, border,          rect, 2, border_radius=8)

        shown = ("*" * len(value)) if (password and value) else value
        if shown:
            color = (30, 30, 60)
        else:
            shown = label
            color = (140, 140, 140)  # placeholder en gris

        screen.blit(self.font.render(shown, True, color), (rect.x + 12, rect.y + 10))

    # --- Scène ---

    def draw(self, screen):
        if self.bg:
            screen.blit(self.bg, (0, 0))
        else:
            screen.fill((40, 40, 60))

        title = self.title_font.render("Inscription", True, (255, 255, 255))
        screen.blit(title, title.get_rect(center=(self.game.w // 2, 120)))

        self._draw_input(screen, self.username_rect,     "Identifiant",      self.username,
                         active=(self.active_field == "username"))
        self._draw_input(screen, self.display_name_rect, "Pseudo affichage", self.display_name,
                         active=(self.active_field == "display_name"))
        self._draw_input(screen, self.password_rect,     "Mot de passe",     self.password,
                         active=(self.active_field == "password"), password=True)

        # Aperçu de l'avatar sélectionné
        if self.avatars:
            img = pg.image.load(self.avatars[self.avatar_index])
            img = img.convert_alpha() if img.get_alpha() is not None else img.convert()
            screen.blit(pg.transform.smoothscale(img, (96, 96)), (240, 420))

        for b in self.buttons:
            b.draw(screen)

        if self.message:
            screen.blit(self.font.render(self.message, True, (255, 220, 120)), (340, 600))

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
        elif self.display_name_rect.collidepoint(pos):
            self.active_field = "display_name"
        elif self.password_rect.collidepoint(pos):
            self.active_field = "password"

    def _handle_keydown(self, event):
        if event.key == pg.K_TAB:
            order = ["username", "display_name", "password"]
            self.active_field = order[(order.index(self.active_field) + 1) % 3]
            return
        if event.key == pg.K_BACKSPACE:
            self._delete_char()
            return
        self._type_char(event.unicode)

    def _delete_char(self):
        if self.active_field == "username":
            self.username = self.username[:-1]
        elif self.active_field == "display_name":
            self.display_name = self.display_name[:-1]
        else:
            self.password = self.password[:-1]

    def _type_char(self, ch):
        if not ch or not ch.isprintable():
            return
        if self.active_field == "username":
            if len(self.username) < 24 and ch != " ":
                self.username += ch
        elif self.active_field == "display_name":
            if len(self.display_name) < 24:
                self.display_name += ch
        elif len(self.password) < 32:
            self.password += ch
