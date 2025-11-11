import pygame as pg  # pygame importé sous le nom pg
from scenes.base_scene import Scene  # classe de base pour les scènes
from services import Scoring  # utilitaire de scoring


class ResultScene(Scene):  # Écran affichant le résultat après validation d'une tenue
    def __init__(self, game, mannequin, theme, outfit):
        super().__init__(game)  # conserve la référence au jeu
        self.mannequin = mannequin  # mannequin utilisé
        self.theme_code, self.theme_label = theme  # code et libellé du thème
        self.outfit = outfit  # Outfit construit par l'utilisateur
        self.big = pg.font.SysFont(None, 42)  # police grande pour titre
        self.med = pg.font.SysFont(None, 28)  # police moyenne pour textes


        # Calcul du score et de l'argent gagné
        self.score = Scoring.score(self.theme_code, self.outfit.all_items())  # calcule le score total
        self.money = int(self.score / 10) * 5  # conversion simple score -> argent


    def handle_event(self, event):  # Gère les touches clavier sur l'écran résultat
        if event.type == pg.KEYDOWN: 
            if event.key == pg.K_r:  # R pour retourner au menu
                self.game.goto_menu()
            if event.key == pg.K_n:  # N prévu pour relancer (placeholder)
                self.game.goto_menu()  # pour l'instant renvoie aussi au menu


    def draw(self, screen):  # Dessine l'écran résultat
        screen.fill((245,245,250))  # fond clair
        txt = self.big.render(f"Résultat — thème {self.theme_label}", True, (30,30,60))  # titre
        screen.blit(txt, (40,40))
        sc = self.med.render(f"Score: {self.score}", True, (30,30,60))  # texte du score
        mo = self.med.render(f"Argent gagné: {self.money}", True, (30,30,60))  # texte de l'argent gagné
        screen.blit(sc, (40, 120))
        screen.blit(mo, (40, 160))


        hint = self.med.render("R = Retour menu", True, (60,60,80))  # astuce clavier
        screen.blit(hint, (40, 220))