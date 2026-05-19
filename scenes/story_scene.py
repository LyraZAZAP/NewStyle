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
        self.dialogue_index = 0

        self.dialogues = [
            "Tu viens d'entrer en école de styliste, après le bac (de JUSTESSE).",
            "Une seule règle : sois stylé.",
            "En marchant vers ton école, tu vois beaucoup d'élèves, tous habillés de façon très originale.",
            "Tu remarques : emo… scène… goth… classic… lolita… etc.",
        ]

        self.background   = _load_image("assets/backgrounds/school.png",
                                        (self.game.w, self.game.h), fallback_color=(180, 200, 240))
        self.bar_image    = _load_image("assets/bar/bar_text_purple.png")
        self.bar_rect     = self.bar_image.get_rect(midbottom=(self.game.w // 2, self.game.h - 5))

        char_size         = (int(self.game.h * 0.84),) * 2
        self.juliette_image = _load_image("assets/characteres/juliette_mouth_closed.png", size=char_size)
        self.juliette_rect  = self.juliette_image.get_rect(midbottom=(self.game.w // 2, self.game.h - 40))

        self.title_font  = pg.font.SysFont(None, 42)
        self.text_font   = pg.font.SysFont(None, 32)
        self.prompt_font = pg.font.SysFont(None, 24)

        self.juliette_visible = False
        self.shake_timer      = 0.0
        self.shake_duration   = 0.4  # secondes
        self.shake_intensity  = 8    # pixels

    def handle_event(self, event):
        advance = (
            (event.type == pg.MOUSEBUTTONDOWN and event.button == 1) or
            (event.type == pg.KEYDOWN and event.key in (pg.K_RETURN, pg.K_SPACE))
        )
        if not advance:
            return
        if self.juliette_visible and self.shake_timer <= 0.0:
            self.game.goto_dress(self.mannequin, self.theme)
        else:
            self._next_dialogue()

    def update(self, dt):
        if self.shake_timer > 0.0:
            self.shake_timer = max(0.0, self.shake_timer - dt)

    def draw(self, screen):
        screen.blit(self.background, (0, 0))

        # Effet de tremblement quand Juliette apparaît
        shake_x, shake_y = 0, 0
        if self.juliette_visible and self.shake_timer > 0.0:
            amplitude = int(self.shake_intensity * (self.shake_timer / self.shake_duration))
            shake_x   = random.randint(-amplitude, amplitude)
            shake_y   = random.randint(-amplitude, amplitude)

        if self.juliette_visible:
            screen.blit(self.juliette_image, self.juliette_rect.move(shake_x, shake_y))

        bar_rect = self.bar_rect.move(shake_x, shake_y)
        screen.blit(self.bar_image, bar_rect)

        title = self.title_font.render("toi", True, (255, 255, 255))
        screen.blit(title, (bar_rect.left + 30, bar_rect.top + 18))

        text = self.text_font.render(self.dialogues[self.dialogue_index], True, (245, 245, 245))
        screen.blit(text, (bar_rect.left + 40, bar_rect.top + 80))

        prompt      = self.prompt_font.render("Cliquez ou appuyez sur Entrée pour continuer", True, (200, 200, 220))
        prompt_rect = prompt.get_rect()
        prompt_rect.bottomright = (bar_rect.right - 20, bar_rect.bottom - 15)
        screen.blit(prompt, prompt_rect)

    def _next_dialogue(self):
        if self.juliette_visible:
            return
        if self.dialogue_index < len(self.dialogues) - 1:
            self.dialogue_index += 1
        else:
            self.juliette_visible = True
            self.shake_timer      = self.shake_duration
