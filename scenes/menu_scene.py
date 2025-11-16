import random  # utilitaire pour choisir aléatoirement
import os
import pygame as pg  # pygame importé sous le nom pg
from scenes.base_scene import Scene  # classe de base pour les scènes
from ui.widgets import Button  # widget bouton réutilisable
from repositories import MannequinRepo  # repo pour récupérer les mannequins
from models import Mannequin
from config import MENU_BG_PATH

THEMES = [  # liste des thèmes disponibles (code, label)
    ("casual", "Casual"),
    ("soiree", "Soirée"),
    ("colorful", "Colorful"),
    ("chic", "Chic"),
]


def _load_background(path, size, fallback_color=(240, 240, 245)):
    if os.path.exists(path):
        img = pg.image.load(path)
        img = img.convert() if img.get_alpha() is None else img.convert_alpha()
        return pg.transform.smoothscale(img, size)
    surf = pg.Surface(size)
    surf.fill(fallback_color)
    return surf


class MenuScene(Scene):  # Écran d'accueil / menu principal
    def __init__(self, game):
        super().__init__(game)  # conserve la référence au jeu
        self.title_font = pg.font.SysFont(None, 56)  # police pour le titre
        self.buttons = []  # liste des boutons du menu

        def start_random():  # callback appelé au clic pour démarrer une partie aléatoire
            theme = random.choice(THEMES)  # choisit un thème au hasard
            mannequins = MannequinRepo.all()  # récupère la liste des mannequins disponibles
            # Sécurité : si la BDD n'est pas peuplée, utiliser un mannequin par défaut
            default_mannequin = Mannequin(0, 'Lina', 'assets/mannequins/mannequin_base.png')
            m = random.choice(mannequins) if mannequins else default_mannequin
            self.game.goto_dress(m, theme)

        self.buttons.append(Button((412, 320, 200, 50), "Nouvelle partie", start_random))

        # Bouton toggle fullscreen (coin supérieur droit)
        self.fullscreen_btn = pg.Rect(self.game.w - 120, 10, 110, 40)
        self.font_small = pg.font.SysFont(None, 24)

        # Charger le fond d'écran
        self.bg = _load_background(MENU_BG_PATH, (self.game.w, self.game.h))

    def draw(self, screen):  # Dessine l'écran du menu
        screen.blit(self.bg, (0, 0))  # Dessiner le fond en premier
        title = self.title_font.render("Regardez mon beau jeu", True, (179,0,248))  # rend le titre
        title_rect = title.get_rect(center=(screen.get_width() // 2, 120))
        # Encadré blanc semi-transparent derrière le titre
        bg_rect = title_rect.inflate(40, 20)
        bg_surf = pg.Surface((bg_rect.width, bg_rect.height), pg.SRCALPHA)
        bg_surf.fill((255, 255, 255, 200))
        screen.blit(bg_surf, bg_rect.topleft)
        screen.blit(title, title_rect)

        for b in self.buttons:  # dessine tous les boutons
            b.draw(screen)

        # Dessiner le bouton fullscreen
        color = (100, 150, 255) if self.fullscreen_btn.collidepoint(pg.mouse.get_pos()) else (70, 120, 200)
        pg.draw.rect(screen, color, self.fullscreen_btn, border_radius=5)
        pg.draw.rect(screen, (179,0,248), self.fullscreen_btn, 5, border_radius=5)

        label = "Plein écran" if not self.game.is_fullscreen else "Fenêtré"
        text = self.font_small.render(label, True, (255, 255, 255))
        text_rect = text.get_rect(center=self.fullscreen_btn.center)
        screen.blit(text, text_rect)

    def handle_event(self, event):  # Transmet les événements aux widgets (boutons)
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            # Clic sur bouton fullscreen
            if self.fullscreen_btn.collidepoint(event.pos):
                self.game.toggle_fullscreen()
                return
        for b in self.buttons:
            b.handle(event)