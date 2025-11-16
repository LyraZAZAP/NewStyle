import os
import pygame as pg
from scenes.base_scene import Scene
from services import Scoring
from config import RESULT_BG_PATH


def _load_background(path, size, fallback_color=(240, 240, 250)):
    """Charge et redimensionne une image de fond, ou retourne une surface unie."""
    if os.path.exists(path):
        img = pg.image.load(path)
        img = img.convert() if img.get_alpha() is None else img.convert_alpha()
        return pg.transform.smoothscale(img, size)
    surf = pg.Surface(size)
    surf.fill(fallback_color)
    return surf


class ResultScene(Scene):
    def __init__(self, game, mannequin, theme, outfit, worn_garments):
        super().__init__(game)
        self.mannequin = mannequin
        self.theme_code, self.theme_label = theme
        self.outfit = outfit
        self.font = pg.font.SysFont(None, 32)
        self.small_font = pg.font.SysFont(None, 24)

        # Zones d'affichage
        self.left_panel = pg.Rect(0, 0, self.game.w // 2, self.game.h)
        self.right_panel = pg.Rect(self.game.w // 2, 0, self.game.w // 2, self.game.h)

        # Charger le fond d'écran
        self.bg = _load_background(RESULT_BG_PATH, (self.game.w, self.game.h))

        # Charger le mannequin de base
        self.mannequin_img = self._safe_load(mannequin.base_sprite_path, size=(360, 520))

        # Trier les vêtements portés par calque et les redimensionner
        self.worn_garments = []
        for garment in sorted(worn_garments, key=lambda g: self._layer_for(g)):
            img = self._safe_load(garment.sprite_path, size=(360, 520))
            self.worn_garments.append(img)

        # Calcul du score et de l'argent gagné
        self.score = Scoring.score(self.theme_code, self.outfit.all_items())
        self.money = int(self.score / 10) * 5

    def _safe_load(self, path, size=(360, 520)):
        if os.path.exists(path):
            img = pg.image.load(path).convert_alpha()
            return pg.transform.smoothscale(img, size)
        surf = pg.Surface(size, pg.SRCALPHA)
        surf.fill((230, 220, 220))
        pg.draw.rect(surf, (120, 120, 140), surf.get_rect(), 2)
        return surf

    def _layer_for(self, garment) -> int:
        # Réutiliser la logique de DressScene
        name = getattr(garment, 'name', '').upper()
        if any(tok in name for tok in ["SHOE", "CHAUSSURE"]):
            return 0
        if any(tok in name for tok in ["BOTTOM", "BAS", "PANTS", "PANTALON", "SKIRT", "JUPE"]):
            return 1
        if any(tok in name for tok in ["TOP", "HAUT", "SHIRT", "DRESS", "ROBE"]):
            return 2
        if any(tok in name for tok in ["HAIR", "CHEVEU", "HEAD"]):
            return 3
        if any(tok in name for tok in ["FACE", "VISAGE"]):
            return 4
        if any(tok in name for tok in ["ACCESSORY", "ACCESSOIRE"]):
            return 5
        return 2

    def handle_event(self, event):  # Gère les touches clavier sur l'écran résultat
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_r:  # R pour retourner au menu
                self.game.goto_menu()
            if event.key == pg.K_n:  # N prévu pour relancer (placeholder)
                self.game.goto_menu()  # pour l'instant renvoie aussi au menu

    def update(self, dt):
        pass

    def draw(self, screen):
        # Dessiner le fond en premier
        screen.blit(self.bg, (0, 0))

        # Panneau gauche: score et infos avec encadrés blancs
        title = self.font.render(f"Résultat — thème {self.theme_label}", True, (20, 20, 50))
        title_rect = title.get_rect(topleft=(20, 20))
        # Encadré blanc semi-transparent derrière le titre
        bg_rect = title_rect.inflate(20, 10)  # ajoute 10px de padding horizontal et 5px vertical
        bg_surf = pg.Surface((bg_rect.width, bg_rect.height), pg.SRCALPHA)
        bg_surf.fill((255, 255, 255, 200))  # blanc avec transparence
        screen.blit(bg_surf, bg_rect.topleft)
        screen.blit(title, title_rect)

        score_text = self.small_font.render(f"Score: {self.score}", True, (50, 50, 80))
        score_rect = score_text.get_rect(topleft=(20, 80))
        bg_rect = score_rect.inflate(20, 10)
        bg_surf = pg.Surface((bg_rect.width, bg_rect.height), pg.SRCALPHA)
        bg_surf.fill((255, 255, 255, 200))
        screen.blit(bg_surf, bg_rect.topleft)
        screen.blit(score_text, score_rect)

        mo = self.small_font.render(f"Argent gagné: {self.money}", True, (30, 30, 60))
        mo_rect = mo.get_rect(topleft=(40, 160))
        bg_rect = mo_rect.inflate(20, 10)
        bg_surf = pg.Surface((bg_rect.width, bg_rect.height), pg.SRCALPHA)
        bg_surf.fill((255, 255, 255, 200))
        screen.blit(bg_surf, bg_rect.topleft)
        screen.blit(mo, mo_rect)

        hint = self.small_font.render("R = Retour menu", True, (60, 60, 80))
        hint_rect = hint.get_rect(topleft=(40, 220))
        bg_rect = hint_rect.inflate(20, 10)
        bg_surf = pg.Surface((bg_rect.width, bg_rect.height), pg.SRCALPHA)
        bg_surf.fill((255, 255, 255, 200))
        screen.blit(bg_surf, bg_rect.topleft)
        screen.blit(hint, hint_rect)

        # Panneau droit: mannequin habillé
        mannequin_x = self.right_panel.centerx - self.mannequin_img.get_width() // 2
        mannequin_y = 80

        # Dessiner le mannequin de base
        screen.blit(self.mannequin_img, (mannequin_x, mannequin_y))

        # Superposer les vêtements portés
        for garment_img in self.worn_garments:
            screen.blit(garment_img, (mannequin_x, mannequin_y))