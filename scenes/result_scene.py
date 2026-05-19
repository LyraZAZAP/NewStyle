# Scène de résultat : score et aperçu de la tenue finale

import os
import pygame as pg
from scenes.base_scene import Scene
from services import Scoring
from config import RESULT_BG_PATH


def _load_background(path, size, fallback_color=(240, 240, 250)):
    """Charge et redimensionne un fond d'écran, ou surface unie si fichier absent."""
    if os.path.exists(path):
        img = pg.image.load(path)
        img = img.convert() if img.get_alpha() is None else img.convert_alpha()
        return pg.transform.smoothscale(img, size)
    surf = pg.Surface(size)
    surf.fill(fallback_color)
    return surf


class ResultScene(Scene):
    """Affiche le score, l'argent gagné et le mannequin habillé."""

    def __init__(self, game, mannequin, theme, outfit, worn_garments):
        super().__init__(game)
        self.mannequin              = mannequin
        self.theme_code, self.theme_label = theme
        self.outfit                 = outfit
        self.font       = pg.font.SysFont(None, 32)
        self.small_font = pg.font.SysFont(None, 24)

        self.left_panel  = pg.Rect(0,              0, self.game.w // 2, self.game.h)
        self.right_panel = pg.Rect(self.game.w // 2, 0, self.game.w // 2, self.game.h)

        self.bg           = _load_background(RESULT_BG_PATH, (self.game.w, self.game.h))
        self.mannequin_img = self._safe_load(mannequin.base_sprite_path, size=(360, 520))

        # Tri par calque pour un affichage cohérent avec DressScene
        self.worn_garments = [
            self._safe_load(g.sprite_path, size=(360, 520))
            for g in sorted(worn_garments, key=self._layer_for)
        ]

        self.score = Scoring.score(self.theme_code, self.outfit.all_items())
        self.money = int(self.score / 10) * 5

    def _safe_load(self, path, size=(360, 520)):
        """Charge et redimensionne une image, ou placeholder gris si absente."""
        if os.path.exists(path):
            return pg.transform.smoothscale(pg.image.load(path).convert_alpha(), size)
        surf = pg.Surface(size, pg.SRCALPHA)
        surf.fill((230, 220, 220))
        pg.draw.rect(surf, (120, 120, 140), surf.get_rect(), 2)
        return surf

    def _layer_for(self, garment) -> int:
        """Ordre de superposition identique à DressScene (0=fond → 5=avant)."""
        name = getattr(garment, 'name', '').upper()
        if any(t in name for t in ["SHOE", "CHAUSSURE"]):                         return 0
        if any(t in name for t in ["BOTTOM", "BAS", "PANTS", "SKIRT", "JUPE"]):  return 1
        if any(t in name for t in ["TOP", "HAUT", "SHIRT", "DRESS", "ROBE"]):    return 2
        if any(t in name for t in ["HAIR", "CHEVEU", "HEAD"]):                    return 3
        if any(t in name for t in ["FACE", "VISAGE"]):                            return 4
        if any(t in name for t in ["ACCESSORY", "ACCESSOIRE"]):                   return 5
        return 2

    def handle_event(self, event):
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_r:
                self.game.goto_menu()
            elif event.key == pg.K_e:
                self.game.goto_story(self.mannequin, (self.theme_code, self.theme_label), phase=1)

    def update(self, dt):
        pass  # écran statique, aucune logique à mettre à jour

    def draw(self, screen):
        screen.blit(self.bg, (0, 0))
        self._draw_info_panel(screen)
        self._draw_mannequin(screen)

    def _draw_info_panel(self, screen):
        """Panneau gauche : titre, score, argent, raccourci retour."""
        items = [
            (self.font,       f"Résultat — thème {self.theme_label}", (255,255,255), (20, 20)),
            (self.small_font, f"Score: {self.score}",                 (50, 50, 80),  (20, 80)),
            (self.small_font, f"Argent gagné: {self.money}",          (30, 30, 60),  (40, 160)),
            (self.small_font, "R = Retour au menu",                    (60, 60, 80),  (40, 220)),
            (self.small_font, "E = Continuer l'histoire",              (60, 60, 80),  (40, 260)),
        ]
        for font, text, color, pos in items:
            surf    = font.render(text, True, color)
            rect    = surf.get_rect(topleft=pos)
            bg_surf = pg.Surface(rect.inflate(20, 10).size, pg.SRCALPHA)
            bg_surf.fill((255, 255, 255, 200))
            screen.blit(bg_surf, rect.inflate(20, 10).topleft)
            screen.blit(surf, rect)

    def _draw_mannequin(self, screen):
        """Panneau droit : mannequin de base + vêtements portés superposés."""
        x = self.right_panel.centerx - self.mannequin_img.get_width() // 2
        y = 80
        screen.blit(self.mannequin_img, (x, y))
        for garment_img in self.worn_garments:
            screen.blit(garment_img, (x, y))
