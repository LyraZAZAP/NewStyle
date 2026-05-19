# Scène visual novel d'introduction

import os
import random
import pygame as pg
from scenes.base_scene import Scene


def _load_image(path, size=None, fallback_color=(220, 220, 240)):
    """Charge une image (et la redimensionne si size est donné), ou surface de repli si absente."""
    if os.path.exists(path):
        image = pg.image.load(path)
        image = image.convert_alpha() if image.get_alpha() is not None else image.convert()
        if size is not None:
            image = pg.transform.smoothscale(image, size)
        return image
    surf = pg.Surface(size if size is not None else (100, 100), pg.SRCALPHA)
    surf.fill(fallback_color)
    return surf


class StoryScene(Scene):
    """Scène simple : fond, personnage et barre de texte narrative."""

    def __init__(self, game, mannequin, theme):
        super().__init__(game)
        self.mannequin      = mannequin
        self.theme          = theme
        self.player_dialogues = [  # dialogues du joueur (narrateur)
            "Tu viens d'entrer en école de styliste, après le bac de JUSTESSE ",
            "Une seule règle, soit stylé",
            "En marchant vers ton école, tu vois beaucoup d'élèves, tous habillés de façon très originaux. Tu remarques, emo.. scene.. goth.. classic.. lolita.. etc etc",
            "DUMBASS T'A COGNÉ QUELQU'UN",
        ]
        
        self.dialogue_index = 0  # index dans player_dialogues
        self.juliette_dialogue_index = 0  # index dans juliette_dialogues
        
        self.juliette_dialogues = [  # dialogues de Juliette : (texte, clé image)
            ("OPA! Mais vro regarde", "confused_talking"),
            ("AHHHH t'es nouvelle nn???", "mouth_closed"),
            ("Va falloir une outfit là psq tu ressemble à un ", "smile"),
        ]

        self.background   = _load_image("assets/backgrounds/school.png", (self.game.w, self.game.h), fallback_color=(180, 200, 240))
        raw_bar = _load_image("assets/bar/bar_text_purple.png")  # charger la barre sans redimensionnement
        nat_w, nat_h = raw_bar.get_size()  # récupérer les dimensions naturelles
        bar_w = self.game.w - 20  # largeur cible : presque tout l'écran
        bar_h = int(nat_h * bar_w / nat_w)  # hauteur calculée pour conserver le ratio
        self.bar_image = pg.transform.smoothscale(raw_bar, (bar_w, bar_h))  # redimensionner en conservant les proportions
        
        self.bar_rect     = self.bar_image.get_rect(midbottom=(self.game.w // 2, self.game.h - 5))

        self.text_area_rect = pg.Rect(self.bar_rect.left + 40, self.bar_rect.top + 90, self.bar_rect.width - 80, self.bar_rect.height - 100)  # zone de texte dans la barre, décalée vers le bas
        char_size = (int(self.game.h * 0.84), int(self.game.h * 0.84))
        self.juliette_images = {  # toutes les expressions de Juliette
            "mouth_closed":     _load_image("assets/characteres/juliette_mouth_closed.png",     size=char_size),
            "smile":            _load_image("assets/characteres/juliette_smile.png",            size=char_size),
            "confused_talking": _load_image("assets/characteres/juliette_confused_talking.png", size=char_size),
        }
        self.juliette_image = self.juliette_images["mouth_closed"]  # image affichée actuellement
        self.juliette_rect = self.juliette_image.get_rect(midbottom=(self.game.w // 2, self.game.h - 40))

        self.title_font = pg.font.SysFont("Comic Sans MS", 42)  # police pour le titre
        self.text_font = pg.font.SysFont("Comic Sans MS", 32)  # police pour le dialogue
        self.prompt_font = pg.font.SysFont("Comic Sans MS", 24)  # police pour le prompt
        

        self.juliette_visible = False
        self.shake_timer      = 0.0
        self.shake_duration   = 0.4  # secondes
        self.shake_intensity  = 8    # pixels

    def handle_event(self, event):
        """Avance le dialogue ou quitte la scène après le dernier dialogue de Juliette."""
        advance = False
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            advance = True
        elif event.type == pg.KEYDOWN and event.key in (pg.K_RETURN, pg.K_SPACE):
            advance = True

        if advance and self.shake_timer <= 0.0:
            self._next_dialogue()
        
    def update(self, dt):
        if self.shake_timer > 0.0:
            self.shake_timer = max(0.0, self.shake_timer - dt)

    def draw(self, screen):
        screen.blit(self.background, (0, 0))

        shake_x, shake_y = 0, 0
        if self.juliette_visible and self.shake_timer > 0.0:
            amplitude = int(self.shake_intensity * (self.shake_timer / self.shake_duration))
            shake_x   = random.randint(-amplitude, amplitude)
            shake_y   = random.randint(-amplitude, amplitude)

        if self.juliette_visible:
            screen.blit(self.juliette_image, self.juliette_rect.move(shake_x, shake_y))

        bar_rect = self.bar_rect.move(shake_x, shake_y)
        screen.blit(self.bar_image, bar_rect)

        speaker_name = "juliette" if self.juliette_visible else "toi"
        title = self.title_font.render(speaker_name, True, (255, 255, 255))
        screen.blit(title, (bar_rect.left + 30, bar_rect.top + 18))

        if self.juliette_visible:
            message = self.juliette_dialogues[self.juliette_dialogue_index][0]
        else:
            message = self.player_dialogues[self.dialogue_index]
        wrapped = self._wrap_text(message, self.text_font, self.bar_rect.width - 80)
        line_y = bar_rect.top + 90
        for line in wrapped:
            text = self.text_font.render(line, True, (245, 245, 245))
            screen.blit(text, (bar_rect.left + 40, line_y))
            line_y += self.text_font.get_linesize()

        prompt = self.prompt_font.render("Cliquez ou appuyez sur Entrée pour continuer", True, (200, 200, 220))
        prompt_rect = prompt.get_rect()
        prompt_rect.bottomright = (bar_rect.right - 20, bar_rect.bottom - 15)
        screen.blit(prompt, prompt_rect)

    def _wrap_text(self, text, font, max_width):
        """Découpe un texte long en plusieurs lignes pour qu'il tienne dans max_width pixels."""
        words = text.split()  # séparer le texte en mots individuels
        lines, current = [], []  # lines = lignes finies, current = mots de la ligne en cours
        for word in words:  # parcourir chaque mot
            test = ' '.join(current + [word])  # tester si le mot courant rentre sur la ligne
            if font.size(test)[0] <= max_width:  # si la ligne reste dans la largeur autorisée
                current.append(word)  # ajouter le mot à la ligne en cours
            else:
                if current:  # si la ligne en cours n'est pas vide
                    lines.append(' '.join(current))  # valider la ligne et la sauvegarder
                current = [word]  # recommencer une nouvelle ligne avec le mot débordant
        if current:  # ajouter la dernière ligne si elle n'est pas vide
            lines.append(' '.join(current))
        return lines  # retourner la liste de toutes les lignes

    def _next_dialogue(self):
        """Avance les dialogues du joueur, puis ceux de Juliette, puis change de scène."""
        if self.juliette_visible:
            # Avancer dans les dialogues de Juliette
            if self.juliette_dialogue_index < len(self.juliette_dialogues) - 1:
                self.juliette_dialogue_index += 1
                img_key = self.juliette_dialogues[self.juliette_dialogue_index][1]
                self.juliette_image = self.juliette_images[img_key]
            else:
                self.game.goto_dress(self.mannequin, self.theme)
        else:
            if self.dialogue_index < len(self.player_dialogues) - 1:
                self.dialogue_index += 1
            else:
                # Tous les dialogues du joueur sont lus : Juliette apparaît
                self.juliette_visible = True
                self.shake_timer = self.shake_duration
                img_key = self.juliette_dialogues[0][1]
                self.juliette_image = self.juliette_images[img_key]