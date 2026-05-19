import pygame as pg


class Button:
    """Bouton cliquable avec texte centré."""

    def __init__(self, rect, text, on_click):
        self.rect     = pg.Rect(rect)
        self.text     = text
        self.on_click = on_click
        self.font     = pg.font.SysFont(None, 28)

    def draw(self, surf):
        pg.draw.rect(surf, (220, 220, 230), self.rect, border_radius=20)
        pg.draw.rect(surf, (10, 104, 255),  self.rect, 5, border_radius=20)
        label = self.font.render(self.text, True, (10, 104, 255))
        surf.blit(label, label.get_rect(center=self.rect.center))

    def handle(self, event):
        if event.type == pg.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos):
            self.on_click()


class VolumeWidget:
    """Curseur de volume + flèches de navigation musicale — bas-droit de l'écran.

    Layout : [◀] [♪] [===slider===] [▶]
    """

    W, H    = 188, 28
    ARROW_W = 22
    ICON_W  = 22
    GAP     = 4
    MARGIN  = 16

    def __init__(self, audio):
        self.audio     = audio
        self._dragging = False
        self._font     = pg.font.SysFont(None, 20)
        self.rect      = pg.Rect(0, 0, self.W, self.H)
        self.prev_rect = pg.Rect(0, 0, self.ARROW_W, self.H)
        self.icon_rect = pg.Rect(0, 0, self.ICON_W,  self.H)
        self.bar_rect  = pg.Rect(0, 0, 0, 10)

    def place(self, screen_w, screen_h):
        x = screen_w - self.MARGIN - self.W
        y = screen_h - self.MARGIN - self.H

        self.rect      = pg.Rect(x, y, self.W, self.H)
        self.prev_rect = pg.Rect(x, y, self.ARROW_W, self.H)

        icon_x = x + self.ARROW_W + self.GAP
        self.icon_rect = pg.Rect(icon_x, y, self.ICON_W, self.H)

        bar_x = icon_x + self.ICON_W + self.GAP
        bar_w = self.W - self.ARROW_W - self.GAP - self.ICON_W - self.GAP
        self.bar_rect  = pg.Rect(bar_x, y + (self.H - 10) // 2, bar_w, 10)

    # --- Calculs volume ↔ position ---

    def _volume_x(self):
        return int(self.bar_rect.left + self.audio.volume * self.bar_rect.width)

    def _x_to_volume(self, x):
        return max(0.0, min(1.0, (x - self.bar_rect.left) / max(1, self.bar_rect.width)))

    def _set_volume(self, x):
        self.audio.volume = self._x_to_volume(x)
        pg.mixer.music.set_volume(self.audio.volume)

    # --- Événements ---

    def handle_event(self, event):
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            return self._handle_mouse_down(event.pos)
        if event.type == pg.MOUSEBUTTONUP and event.button == 1 and self._dragging:
            self._dragging = False
            return True
        if event.type == pg.MOUSEMOTION and self._dragging:
            self._set_volume(event.pos[0])
            return True
        return False

    def _handle_mouse_down(self, pos):
        if self.prev_rect.collidepoint(pos):
            self.audio.prev_track()
            return True
        hx, hy = self._volume_x(), self.bar_rect.centery
        on_handle = abs(pos[0] - hx) <= 8 and abs(pos[1] - hy) <= 8
        if self.bar_rect.collidepoint(pos) or on_handle:
            self._dragging = True
            self._set_volume(pos[0])
            return True
        return False

    # --- Dessin ---

    def _draw_arrow(self, screen, rect, symbol):
        hovered = rect.collidepoint(pg.mouse.get_pos())
        fg = (255, 255, 255) if hovered else (180, 180, 200)
        lbl = self._font.render(symbol, True, fg)
        screen.blit(lbl, lbl.get_rect(center=rect.center))

    def draw(self, screen):
        # Fond semi-transparent arrondi
        bg = pg.Surface((self.W, self.H), pg.SRCALPHA)
        bg.fill((20, 20, 20, 160))
        screen.blit(bg, self.rect.topleft)
        pg.draw.rect(screen, (90, 90, 100), self.rect, 1, border_radius=6)

        # Flèche piste précédente
        self._draw_arrow(screen, self.prev_rect, "◀")

        # Icône muet / son
        icon = "♪" if self.audio.volume > 0 else "✕"
        lbl  = self._font.render(icon, True, (255, 255, 255))
        screen.blit(lbl, lbl.get_rect(center=self.icon_rect.center))

        # Rail gris
        pg.draw.rect(screen, (70, 70, 80), self.bar_rect, border_radius=5)

        # Remplissage bleu
        fill_w = int(self.audio.volume * self.bar_rect.width)
        if fill_w > 0:
            fill = pg.Rect(self.bar_rect.left, self.bar_rect.top, fill_w, self.bar_rect.height)
            pg.draw.rect(screen, (80, 160, 255), fill, border_radius=5)

        # Poignée
        hx, hy = self._volume_x(), self.bar_rect.centery
        pg.draw.circle(screen, (220, 220, 255), (hx, hy), 7)
        pg.draw.circle(screen, (80, 160, 255),  (hx, hy), 7, 2)
