# ========================================
# DISQUE DE MUSIQUE - WIDGET INTERACTIF
# Widget affichant un disque vinyl tournant
# ========================================

# === IMPORTS ===
import pygame as pg  # Pygame pour le rendu graphique


# === CLASSE DISQUE MUSICAL ===
class MusicDiscWidget:
    """Widget affichant un disque vinyl tournant avec un bouton au centre."""
    
    def __init__(self, game, disc_path, button_path, size=220, anchor="topleft", margin=16, speed_deg=60):
        """Crée un widget disque musical."""
        self.game = game  # Référence au jeu
        self.size = size  # Taille du disque en pixels
        self.anchor = anchor  # Position du disque (topright, topleft, etc.)
        self.margin = margin  # Marge par rapport au bord
        self.speed_deg = speed_deg  # Vitesse de rotation en degrés par seconde
        self.angle = 0.0  # Angle de rotation actuel

        # Charge le disque en préservant ses proportions
        disc = pg.image.load(disc_path)
        disc = disc.convert_alpha() if disc.get_alpha() is not None else disc.convert()
        
        # Redimensionne en préservant les proportions
        # Calcule le facteur d'échelle en fonction du plus petit côté
        original_w, original_h = disc.get_size()
        ratio = original_w / original_h if original_w > 0 and original_h > 0 else 1
        
        # Redimensionne pour que l'image tienne dans le carré tout en gardant les proportions
        if original_w > original_h:
            # Image plus large que haute
            new_h = size
            new_w = int(new_h * ratio)
        else:
            # Image plus haute que large (ou carrée)
            new_w = size
            new_h = int(new_w / ratio)
        
        disc_resized = pg.transform.smoothscale(disc, (new_w, new_h))
        
        # Crée une surface carrée et centre l'image dessus
        self.disc_base = pg.Surface((size, size), pg.SRCALPHA)
        x_offset = (size - new_w) // 2  # Centre horizontalement
        y_offset = (size - new_h) // 2  # Centre verticalement
        self.disc_base.blit(disc_resized, (x_offset, y_offset))

        # Charge et rédimensionne le bouton (préserve aussi les proportions)
        btn = pg.image.load(button_path)
        btn = btn.convert_alpha() if btn.get_alpha() is not None else btn.convert()

        btn_size = int(size * 0.34)  # Bouton fait 34% de la taille du disque
        # Redimensionne le bouton en préservant ses proportions
        btn_original_w, btn_original_h = btn.get_size()
        btn_ratio = btn_original_w / btn_original_h if btn_original_w > 0 and btn_original_h > 0 else 1
        
        if btn_original_w > btn_original_h:
            btn_h = btn_size
            btn_w = int(btn_h * btn_ratio)
        else:
            btn_w = btn_size
            btn_h = int(btn_w / btn_ratio)
        
        btn_resized = pg.transform.smoothscale(btn, (btn_w, btn_h))
        
        # Centre le bouton sur un carré
        self.btn_surf = pg.Surface((btn_size, btn_size), pg.SRCALPHA)
        btn_x_offset = (btn_size - btn_w) // 2
        btn_y_offset = (btn_size - btn_h) // 2
        self.btn_surf.blit(btn_resized, (btn_x_offset, btn_y_offset))

        # Calcule la position du disque
        self.center = self._compute_center()
        # Rectangle du bouton au centre du disque
        self.btn_rect = self.btn_surf.get_rect(center=self.center)

    def _compute_center(self):
        """Calcule la position du centre du disque sur l'écran."""
        w, h = self.game.w, self.game.h  # Dimensions de l'écran
        r = self.size // 2  # Rayon du disque
        m = self.margin  # Marge

        # Positionne selon l'ancrage
        if self.anchor == "topleft":
            return (m + r, m + r)
        if self.anchor == "topright":
            return (w - m - r, m + r)
        if self.anchor == "bottomleft":
            return (m + r, h - m - r)
        # bottomright par défaut
        return (w - m - r, h - m - r)

    def on_resize(self):
        """Recalcule la position si la fenêtre est redimensionnée."""
        self.center = self._compute_center()
        self.btn_rect = self.btn_surf.get_rect(center=self.center)

    def update(self, dt):
        """Met à jour l'angle de rotation (appelé chaque frame)."""
        # dt = temps écoulé depuis la dernière frame
        # Augmente l'angle à chaque frame
        self.angle = (self.angle + self.speed_deg * dt) % 360

    def handle_event(self, event):
        """Gère les clics souris sur le bouton."""
        # Vérifie si clic gauche sur le bouton
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            if self.btn_rect.collidepoint(event.pos):
                # Passe à la piste suivante
                self.game.audio.next_track()
                return True
        return False

    def draw(self, screen):
        """Dessine le disque tournant et le bouton."""
        # Disque tournant : applique une rotation à l'image
        rotated = pg.transform.rotozoom(self.disc_base, -self.angle, 1.0)
        rect = rotated.get_rect(center=self.center)
        # Dessine le disque sur l'écran
        screen.blit(rotated, rect)

        # Dessine le bouton par-dessus (au centre du disque)
        screen.blit(self.btn_surf, self.btn_rect)
