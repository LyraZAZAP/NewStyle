# Scène du menu principal

import random
import os
import pygame as pg
from scenes.base_scene import Scene
from ui.widgets import Button
from repositories import MannequinRepo
from models import Mannequin
from config import MENU_BG_PATH, DISC_IMG_PATH, DISC_BTN_PATH, TITLE_IMG_PATH
from ui.music_disc import MusicDiscWidget

# (code_interne, libellé_affiché)
THEMES = [
    ("casual",   "Casual"),
    ("soiree",   "Soirée"),
    ("colorful", "Colorful"),
    ("chic",     "Chic"),
]


def _load_background(path, size, fallback_color=(240, 240, 245)):
    """Charge et redimensionne un fond d'écran, ou surface unie si fichier absent."""
    if os.path.exists(path):
        img = pg.image.load(path)
        img = img.convert() if img.get_alpha() is None else img.convert_alpha()
        return pg.transform.smoothscale(img, size)
    surf = pg.Surface(size)
    surf.fill(fallback_color)
    return surf


class MenuScene(Scene):
    """Écran d'accueil affiché après la connexion."""

    def __init__(self, game):
        super().__init__(game)
        self.title_font = pg.font.SysFont(None, 70)
        self.font_small = pg.font.SysFont(None, 30)

        def start_random():
            theme      = random.choice(THEMES)
            mannequins = MannequinRepo.all()
            default    = Mannequin(0, 'Lina', 'assets/mannequins/mannequin_base.png')
            m          = random.choice(mannequins) if mannequins else default
            self.game.goto_story(m, theme)

        self.buttons = [
            Button((412, 320, 200, 50), "Play",    start_random),
            Button((412, 390, 200, 50), "Quitter", lambda: setattr(self.game, 'running', False)),
        ]

        # Bouton plein écran (coin supérieur droit)
        self.fullscreen_btn = pg.Rect(self.game.w - 120, 10, 110, 40)

        # Fond d'écran
        self.bg = _load_background(MENU_BG_PATH, (self.game.w, self.game.h))

        # Image du titre (assets/titles/)
        self.title_img = None
        try:
            img   = pg.image.load(TITLE_IMG_PATH)
            img   = img.convert_alpha() if img.get_alpha() is not None else img.convert()
            w     = min(600, self.game.w - 40)
            h     = int(w * img.get_height() / img.get_width())
            self.title_img = pg.transform.smoothscale(img, (w, h))
        except Exception as e:
            print(f"Erreur chargement titre : {e}")

        # Disque musical en bas-gauche (partiellement hors écran via margin négatif)
        self.music_disc = MusicDiscWidget(
            self.game, DISC_IMG_PATH, DISC_BTN_PATH,
            size=600, anchor="bottomleft", margin=-175, speed_deg=60,
        )

    def draw(self, screen):
        screen.blit(self.bg, (0, 0))
        self.music_disc.draw(screen)

        # Titre
        if self.title_img is not None:
            screen.blit(self.title_img,
                        self.title_img.get_rect(center=(screen.get_width() // 2, 150)))
        else:
            title    = self.title_font.render("Style Dress", True, (30, 30, 60))
            title_rect = title.get_rect(center=(screen.get_width() // 2, 120))
            bg_surf  = pg.Surface(title_rect.inflate(40, 20).size, pg.SRCALPHA)
            bg_surf.fill((255, 255, 255, 200))
            screen.blit(bg_surf, title_rect.inflate(40, 20).topleft)
            screen.blit(title, title_rect)

        for b in self.buttons:
            b.draw(screen)

        # Bouton plein écran avec effet hover
        color = (100, 150, 255) if self.fullscreen_btn.collidepoint(pg.mouse.get_pos()) else (249, 216, 251)
        pg.draw.rect(screen, color,           self.fullscreen_btn, border_radius=5)
        pg.draw.rect(screen, (255, 255, 255), self.fullscreen_btn, 2, border_radius=5)
        label = "Plein écran" if not self.game.is_fullscreen else "Fenêtré"
        text  = self.font_small.render(label, True, (255, 255, 255))
        screen.blit(text, text.get_rect(center=self.fullscreen_btn.center))

    def handle_event(self, event):
        if self.music_disc.handle_event(event):
            return
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            if self.fullscreen_btn.collidepoint(event.pos):
                self.game.toggle_fullscreen()
                return
        for b in self.buttons:
            b.handle(event)

    def update(self, dt):
        self.music_disc.update(dt)
