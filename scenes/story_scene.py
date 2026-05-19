import os
import random
import pygame as pg
from scenes.base_scene import Scene

BAR_SCALE = 0.28 

def _load_image(path, size=None, fallback_color=(220, 220, 240)):
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

    def __init__(self, game, mannequin, theme):
        super().__init__(game)
        self.mannequin = mannequin
        self.theme = theme
        self.dialogue_index = 0

        self.dialogues = [
            "Tu viens d'entrer en école de styliste, après le bac (de JUSTESSE)",
            "Une seule règle : sois stylé",
            "En marchant vers l'école, tu vois des élèves habillés de façon très originale.",
            "YO DUMBASS T'AS BOUSCULÉ QUELQU'UN",
        ]

        self.background = _load_image(
            "assets/backgrounds/school.png",
            (game.w, game.h),
            fallback_color=(180, 200, 240),
        )

        bar_h = int(game.h * BAR_SCALE)
        self.bar_image = _load_image("assets/bar/bar_text_purple.png", (game.w, bar_h)) 
        self.bar_rect = self.bar_image.get_rect(midbottom=(game.w // 2, game.h - 5))

        char_size = int(game.h * 0.84) 
        self.juliette_image = _load_image(
            "assets/characteres/juliette_mouth_closed.png", (char_size, char_size)
        )
        self.juliette_rect = self.juliette_image.get_rect(
            midbottom=(game.w // 2, game.h - 40)
        )

        self.title_font = pg.font.SysFont(None, 42)
        self.text_font = pg.font.SysFont(None, 32)
        self.prompt_font = pg.font.SysFont(None, 24)

        self.juliette_visible = False
        self.shake_timer = 0.0
        self.shake_duration = 0.4
        self.shake_intensity = 8

    def handle_event(self, event):
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            if self.juliette_visible and self.shake_timer <= 0.0:
                self.game.goto_dress(self.mannequin, self.theme)
            else:
                self._next_dialogue()
        elif event.type == pg.KEYDOWN and event.key in (pg.K_RETURN, pg.K_SPACE):
            if self.juliette_visible and self.shake_timer <= 0.0:
                self.game.goto_dress(self.mannequin, self.theme)
            else:
                self._next_dialogue()

    def update(self, dt):
        if self.shake_timer > 0.0:
            self.shake_timer = max(0.0, self.shake_timer - dt)

    def draw(self, screen):
        screen.blit(self.background, (0, 0))

        shake_x, shake_y = 0, 0
        if self.juliette_visible and self.shake_timer > 0.0:
            amplitude = int(self.shake_intensity * (self.shake_timer / self.shake_duration))
            shake_x = random.randint(-amplitude, amplitude)
            shake_y = random.randint(-amplitude, amplitude)

        if self.juliette_visible:
            screen.blit(self.juliette_image, self.juliette_rect.move(shake_x, shake_y))

        bar_rect = self.bar_rect.move(shake_x, shake_y)
        screen.blit(self.bar_image, bar_rect)

        pad = 30
        y = bar_rect.top + 14

        title = self.title_font.render("toi", True, (255, 255, 255))
        screen.blit(title, (bar_rect.left + pad, y))
        y += self.title_font.get_height() + 8

        max_w = bar_rect.width - pad * 2
        for line in self._wrap(self.dialogues[self.dialogue_index], self.text_font, max_w):
            screen.blit(self.text_font.render(line, True, (245, 245, 245)), (bar_rect.left + pad, y))
            y += self.text_font.get_linesize()

        prompt = self.prompt_font.render("Cliquez ou appuyez sur Entrée pour continuer", True, (200, 200, 220))
        screen.blit(prompt, prompt.get_rect(bottomright=(bar_rect.right - 20, bar_rect.bottom - 10)))

    def _wrap(self, text, font, max_width):
        words = text.split()
        lines, current = [], ""
        for word in words:
            test = current + (" " if current else "") + word
            if font.size(test)[0] <= max_width:
                current = test
            else:
                if current:
                    lines.append(current)
                current = word
        if current:
            lines.append(current)
        return lines

    def _next_dialogue(self):
        if self.juliette_visible:
            return
        if self.dialogue_index < len(self.dialogues) - 1:
            self.dialogue_index += 1
        else:
            self.juliette_visible = True
            self.shake_timer = self.shake_duration