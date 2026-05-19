# Scène roue de la fortune — sélection du thème en mode Arcade

import math
import random
import pygame as pg
from scenes.base_scene import Scene

_FONT = "Comic Sans MS"

THEMES_WHEEL = [
    ("casual",   "Casual",   (255, 160,  80)),
    ("soiree",   "Soirée",   (150,  80, 210)),
    ("colorful", "Colorful", ( 60, 190, 110)),
    ("chic",     "Chic",     (215,  70, 120)),
]


class WheelScene(Scene):
    """Roue de la fortune qui sélectionne un thème aléatoire avant la scène dressing."""

    def __init__(self, game, mannequin):
        super().__init__(game)
        self.mannequin = mannequin

        self.n         = len(THEMES_WHEEL)
        self.seg_angle = 2 * math.pi / self.n
        self.angle     = 0.0
        self.spinning  = False
        self.selected_theme = None  # (code, label) une fois arrêtée
        self.selected_idx   = None

        # Animation de rotation
        self.target_angle      = 0.0
        self.spin_start_angle  = 0.0
        self.spin_duration     = 4.0
        self.spin_elapsed      = 0.0

        self.center = (game.w // 2, game.h // 2 + 20)
        self.radius = 200

        self.title_font  = pg.font.SysFont(_FONT, 40, bold=True)
        self.sub_font    = pg.font.SysFont(_FONT, 24)
        self.label_font  = pg.font.SysFont(_FONT, 26, bold=True)
        self.result_font = pg.font.SysFont(_FONT, 36, bold=True)
        self.btn_font    = pg.font.SysFont(_FONT, 28)

        btn_w, btn_h = 200, 50
        cx   = game.w // 2
        by   = game.h - 15 - btn_h
        self.spin_rect = pg.Rect(cx - btn_w // 2, by, btn_w, btn_h)
        self.play_rect = pg.Rect(cx + 10,          by, btn_w, btn_h)
        self.back_rect = pg.Rect(cx - btn_w - 10,  by, btn_w, btn_h)

    # ------------------------------------------------------------------

    def handle_event(self, event):
        if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
            self.game.goto_menu()
            return
        if event.type != pg.MOUSEBUTTONDOWN or event.button != 1:
            return
        pos = event.pos
        if self.spinning:
            return
        if self.selected_theme is None:
            if self.spin_rect.collidepoint(pos):
                self._start_spin()
        else:
            if self.play_rect.collidepoint(pos):
                self.game.goto_dress(self.mannequin, self.selected_theme)
            elif self.back_rect.collidepoint(pos):
                self._start_spin()

    def _start_spin(self):
        self.selected_theme = None
        winner_idx = random.randint(0, self.n - 1)
        self.selected_idx = winner_idx

        # Angle cible : centre du segment gagnant sous le pointeur (haut = -π/2)
        target = -(winner_idx + 0.5) * self.seg_angle
        while target <= self.angle + math.pi:
            target += 2 * math.pi
        target += 2 * math.pi * random.randint(5, 9)

        self.target_angle     = target
        self.spin_start_angle = self.angle
        self.spin_duration    = 4.0 + random.uniform(0.0, 1.5)
        self.spin_elapsed     = 0.0
        self.spinning         = True

    def update(self, dt):
        if not self.spinning:
            return
        self.spin_elapsed += dt
        t = min(self.spin_elapsed / self.spin_duration, 1.0)
        ease = 1 - (1 - t) ** 4          # easeOutQuart : décélération naturelle
        self.angle = self.spin_start_angle + (self.target_angle - self.spin_start_angle) * ease
        if t >= 1.0:
            self.spinning = False
            self.angle = self.target_angle
            self.selected_theme = (
                THEMES_WHEEL[self.selected_idx][0],
                THEMES_WHEEL[self.selected_idx][1],
            )

    # ------------------------------------------------------------------

    def draw(self, screen):
        screen.fill((25, 15, 45))

        title = self.title_font.render("Mode Arcade", True, (255, 220, 80))
        screen.blit(title, title.get_rect(centerx=self.game.w // 2, top=12))

        if self.selected_theme is None and not self.spinning:
            sub = self.sub_font.render(
                "Tournez la roue pour découvrir votre thème !", True, (180, 170, 220)
            )
            screen.blit(sub, sub.get_rect(centerx=self.game.w // 2, top=60))

        self._draw_wheel(screen)
        self._draw_pointer(screen)

        mouse = pg.mouse.get_pos()

        if not self.spinning:
            if self.selected_theme is None:
                self._draw_btn(screen, self.spin_rect, "Tourner !", mouse)
            else:
                color = THEMES_WHEEL[self.selected_idx][2]
                res = self.result_font.render(
                    f"Thème : {self.selected_theme[1]}", True, color
                )
                # Ombre
                res_sh = self.result_font.render(
                    f"Thème : {self.selected_theme[1]}", True, (0, 0, 0)
                )
                rx = self.game.w // 2
                ry = self.back_rect.top - 14
                screen.blit(res_sh, res_sh.get_rect(centerx=rx + 2, bottom=ry + 2))
                screen.blit(res,    res.get_rect(centerx=rx, bottom=ry))
                self._draw_btn(screen, self.back_rect, "Retourner", mouse, secondary=True)
                self._draw_btn(screen, self.play_rect,  "Jouer !",  mouse)
        else:
            dots = self.btn_font.render("...", True, (180, 180, 220))
            screen.blit(dots, dots.get_rect(center=self.spin_rect.center))

    def _draw_wheel(self, screen):
        cx, cy = self.center
        r = self.radius
        for i, (code, label, color) in enumerate(THEMES_WHEEL):
            start = self.angle + i * self.seg_angle - math.pi / 2
            end   = start + self.seg_angle

            draw_color = color
            if not self.spinning and self.selected_idx == i:
                draw_color = tuple(min(255, c + 65) for c in color)

            self._fill_sector(screen, draw_color, cx, cy, r, start, end)
            # Séparateur
            pg.draw.line(screen, (255, 255, 255),
                         (cx, cy),
                         (int(cx + r * math.cos(start)), int(cy + r * math.sin(start))), 2)

            # Libellé centré sur l'arc
            mid_a = (start + end) / 2
            lx = cx + r * 0.62 * math.cos(mid_a)
            ly = cy + r * 0.62 * math.sin(mid_a)
            sh  = self.label_font.render(label, True, (0, 0, 0))
            txt = self.label_font.render(label, True, (255, 255, 255))
            screen.blit(sh,  sh.get_rect(center=(lx + 2, ly + 2)))
            screen.blit(txt, txt.get_rect(center=(lx, ly)))

        pg.draw.circle(screen, (255, 255, 255), (cx, cy), r, 3)
        pg.draw.circle(screen, (255, 220, 80),  (cx, cy), 20)
        pg.draw.circle(screen, (180, 140,  0),  (cx, cy), 20, 3)

    def _draw_pointer(self, screen):
        cx, cy = self.center
        tip_y = cy - self.radius - 8
        pts = [(cx, tip_y), (cx - 14, tip_y - 28), (cx + 14, tip_y - 28)]
        pg.draw.polygon(screen, (255, 220, 50), pts)
        pg.draw.polygon(screen, (180, 130,  0), pts, 2)

    @staticmethod
    def _fill_sector(surface, color, cx, cy, r, start, end, steps=40):
        pts = [(cx, cy)]
        for i in range(steps + 1):
            a = start + (end - start) * i / steps
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
        pg.draw.polygon(surface, color, pts)

    def _draw_btn(self, screen, rect, text, mouse, secondary=False):
        hovered = rect.collidepoint(mouse)
        if secondary:
            bg = (60, 40, 100) if hovered else (45, 25, 80)
            border = (150, 120, 210)
        else:
            bg = (130, 65, 200) if hovered else (100, 45, 165)
            border = (210, 160, 255)
        pg.draw.rect(screen, bg,     rect, border_radius=12)
        pg.draw.rect(screen, border, rect, 2, border_radius=12)
        txt = self.btn_font.render(text, True, (255, 255, 255))
        screen.blit(txt, txt.get_rect(center=rect.center))
