import os
import pygame as pg  # pygame importé sous le nom pg
from scenes.base_scene import Scene  # classe de base pour les scènes
from services import Scoring  # utilitaire de scoring


class ResultScene(Scene):  # Écran affichant le résultat après validation d'une tenue
    def __init__(self, game, mannequin, theme, outfit, worn_garments):
        super().__init__(game)  # conserve la référence au jeu
        self.mannequin = mannequin  # mannequin utilisé
        self.theme_code, self.theme_label = theme  # code et libellé du thème
        self.outfit = outfit  # Outfit construit par l'utilisateur
        self.big = pg.font.SysFont(None, 42)  # police grande pour titre
        self.med = pg.font.SysFont(None, 28)  # police moyenne pour textes

        # Zones d'affichage
        self.left_panel = pg.Rect(0, 0, self.game.w // 2, self.game.h)
        self.right_panel = pg.Rect(self.game.w // 2, 0, self.game.w // 2, self.game.h)

        # Charger le mannequin de base
        self.mannequin_img = self._safe_load(mannequin.base_sprite_path, size=(360, 520))

        # Trier les vêtements portés par calque et les redimensionner correctement
        self.worn_garments = []
        for garment in sorted(worn_garments, key=lambda g: self._layer_for(g)):
            # Charger l'image à la taille du mannequin (comme dans DressScene)
            img = self._safe_load(garment.sprite_path, size=(360, 520))
            self.worn_garments.append(img)

        # Calcul du score et de l'argent gagné
        self.score = Scoring.score(self.theme_code, self.outfit.all_items())  # calcule le score total
        self.money = int(self.score / 10) * 5  # conversion simple score -> argent

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


    def draw(self, screen):  # Dessine l'écran résultat
        screen.fill((240, 240, 250))
        
        # Panneau gauche: score et infos
        pg.draw.rect(screen, (255, 255, 255), self.left_panel)
        title = self.big.render(f"Résultat — thème {self.theme_label}", True, (20, 20, 50))
        screen.blit(title, (20, 20))
        
        score_text = self.med.render(f"Score: {self.score}", True, (50, 50, 80))
        mo = self.med.render(f"Argent gagné: {self.money}", True, (30,30,60))
        screen.blit(score_text, (20, 80))
        screen.blit(mo, (40, 160))

        hint = self.med.render("R = Retour menu", True, (60,60,80))
        screen.blit(hint, (40, 220))
        
        # Panneau droit: mannequin habillé
        pg.draw.rect(screen, (235, 240, 250), self.right_panel)
        
        # Position du mannequin (centré dans le panneau droit)
        mannequin_x = self.right_panel.centerx - self.mannequin_img.get_width() // 2
        mannequin_y = 80
        
        # Dessiner le mannequin de base
        screen.blit(self.mannequin_img, (mannequin_x, mannequin_y))
        
        # Superposer les vêtements portés (déjà triés et redimensionnés)
        for garment_img in self.worn_garments:
            screen.blit(garment_img, (mannequin_x, mannequin_y))