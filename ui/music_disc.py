# Widget disque vinyl tournant (clic sur le bouton central → piste suivante)

import pygame as pg


class MusicDiscWidget:
    """Disque vinyl animé avec bouton central pour changer de musique."""

    def __init__(self, game, disc_path, button_path, size=220,
                 anchor="topleft", margin=16, speed_deg=60):
        self.game      = game
        self.size      = size
        self.anchor    = anchor
        self.margin    = margin
        self.speed_deg = speed_deg
        self.angle     = 0.0

        self.disc_base = self._load_centered(disc_path, size)
        btn_size       = int(size * 0.34)
        self.btn_surf  = self._load_centered(button_path, btn_size)

        self.center   = pg.Vector2(self._compute_center())
        self.btn_rect = self.btn_surf.get_rect(center=self.center)

    def _load_centered(self, path, size):
        """Charge une image et la centre dans un carré en préservant ses proportions."""
        img = pg.image.load(path)
        img = img.convert_alpha() if img.get_alpha() is not None else img.convert()
        ow, oh  = img.get_size()
        ratio   = ow / oh if oh else 1
        nw, nh  = (size, int(size / ratio)) if ow > oh else (int(size * ratio), size)
        resized = pg.transform.smoothscale(img, (nw, nh))
        surf    = pg.Surface((size, size), pg.SRCALPHA)
        surf.blit(resized, ((size - nw) // 2, (size - nh) // 2))
        return surf

    def _compute_center(self):
        w, h = self.game.w, self.game.h
        r, m = self.size // 2, self.margin
        if self.anchor == "topleft":     return (m + r, m + r)
        if self.anchor == "topright":    return (w - m - r, m + r)
        if self.anchor == "bottomright": return (w - m - r, h - m - r)
        return (m + r, h - m - r)  # bottomleft (défaut)

    def on_resize(self):
        self.center   = pg.Vector2(self._compute_center())
        self.btn_rect = self.btn_surf.get_rect(center=self.center)

    def update(self, dt):
        self.angle = (self.angle + self.speed_deg * dt) % 360

    def handle_event(self, event):
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            if self.btn_rect.collidepoint(event.pos):
                self.game.audio.next_track()
                return True
        return False

    def draw(self, screen):
        rotated = pg.transform.rotozoom(self.disc_base, -self.angle, 1.0)
        screen.blit(rotated, rotated.get_rect(center=self.center))
        # Recalcule la hitbox après rotation (taille inchangée, position identique)
        self.btn_rect = self.btn_surf.get_rect(center=self.center)
        screen.blit(self.btn_surf, self.btn_rect)
