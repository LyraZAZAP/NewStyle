# Scène principale d'habillage : galerie (gauche) + mannequin (droite)

import os
import pygame as pg
from typing import Dict
from scenes.base_scene import Scene
from repositories import CategoryRepo, GarmentRepo
from services import Outfit
from config import SIDEBAR_BG_PATH, STAGE_BG_PATH

SCROLL_SPEED = 40  # pixels par cran de molette


def _load_background(path, size, fallback_color):
    """Charge et redimensionne un fond d'écran, ou surface unie si fichier absent."""
    if os.path.exists(path):
        img = pg.image.load(path)
        img = img.convert() if img.get_alpha() is None else img.convert_alpha()
        return pg.transform.smoothscale(img, size)
    surf = pg.Surface(size)
    surf.fill(fallback_color)
    return surf


class Draggable:
    """Vêtement glissable dans la galerie (drag & drop)."""

    def __init__(self, garment, image, pos):
        self.garment     = garment
        self.thumb       = image           # vignette galerie (petite taille)
        self.image       = image           # image actuellement affichée
        self.stage_image = None            # image redimensionnée quand portée sur le mannequin
        self.base_pos    = pg.Vector2(pos) # position fixe dans la galerie
        self.pos         = pg.Vector2(pos) # position courante (change pendant le drag)
        self.grab        = False
        self.offset      = pg.Vector2(0, 0)  # décalage souris↔objet au moment du grab

    def rect(self):
        return self.image.get_rect(topleft=self.pos)


class DressScene(Scene):
    """Galerie de vêtements à glisser-déposer sur le mannequin."""

    def __init__(self, game, mannequin, theme):
        super().__init__(game)
        self.mannequin              = mannequin
        self.theme_code, self.theme_label = theme
        self.font = pg.font.SysFont(None, 24)
        self.big  = pg.font.SysFont(None, 36)

        self.categories   = CategoryRepo.all()
        self.outfit       = Outfit(self.categories)
        self.gallery_items: list              = []
        self.scroll_y                         = 0
        self.content_height                   = 0
        self.worn_items: Dict[int, Draggable] = {}

        self.scrollbar_dragging   = False
        self.scrollbar_drag_offset = 0

        # Zones de l'écran
        self.sidebar = pg.Rect(0,   0, 320,                  self.game.h)
        self.stage   = pg.Rect(320, 0, self.game.w - 320, self.game.h)

        self.sidebar_bg = _load_background(SIDEBAR_BG_PATH, (self.sidebar.width, self.sidebar.height), (250, 250, 255))
        self.stage_bg   = _load_background(STAGE_BG_PATH,   (self.stage.width,   self.stage.height),   (235, 240, 250))

        self.mannequin_img = self._safe_load(self.mannequin.base_sprite_path, size=(360, 520), fill=(230, 220, 220))

        # Mise en page de la galerie
        self.gallery_cols    = 1
        self.thumb_size      = (280, 280)
        self.gallery_padding = 20
        self.gallery_gap     = 0

        self._build_gallery()
        self._clamp_scroll()

    # --- Chargement d'images ---

    def _safe_load(self, path, size=(120, 120), fill=(200, 200, 210)):
        """Charge une image ou retourne un placeholder si le fichier est absent."""
        if os.path.exists(path):
            return pg.transform.smoothscale(pg.image.load(path).convert_alpha(), size)
        surf = pg.Surface(size, pg.SRCALPHA)
        surf.fill(fill)
        pg.draw.rect(surf, (120, 120, 140), surf.get_rect(), 2)
        return surf

    # --- Construction de la galerie ---

    def _build_gallery(self):
        """Construit la liste d'items de la galerie (labels + Draggables) à partir de la BD."""
        self.gallery_items.clear()
        pad, gap      = self.gallery_padding, self.gallery_gap
        tw, th        = self.thumb_size
        cols          = max(1, int(self.gallery_cols))
        y             = pad

        for cat in self.categories:
            label = self.big.render(cat.name.upper(), True, (40, 40, 70))
            self.gallery_items.append(("label", label, (pad, y)))
            y += 36

            x, col = pad, 0
            for g in GarmentRepo.by_category(cat.id):
                d = Draggable(g, self._safe_load(g.sprite_path, size=(tw, th)), (x, y))
                self.gallery_items.append(d)
                col += 1
                if col >= cols:
                    col, x = 0, pad
                    y += th + gap
                else:
                    x += tw + gap

            if col != 0:
                y += th + gap  # compléter la dernière ligne partielle
            y += gap * 2

        self.content_height = y

    def _clamp_scroll(self):
        max_scroll    = max(0, self.content_height - self.sidebar.height)
        self.scroll_y = max(0, min(self.scroll_y, max_scroll))

    # --- Gestion des événements ---

    def handle_event(self, event):
        if event.type == pg.MOUSEWHEEL:
            self._handle_scroll(event)
        elif event.type == pg.MOUSEBUTTONDOWN:
            self._handle_mouse_down(event)
        elif event.type == pg.MOUSEBUTTONUP and event.button == 1:
            self._handle_mouse_up(event)
        elif event.type == pg.MOUSEMOTION and self.scrollbar_dragging:
            self._update_scrollbar_drag(event.pos)
        elif event.type == pg.KEYDOWN and event.key == pg.K_RETURN:
            self._validate_outfit()

    def _handle_scroll(self, event):
        if self.sidebar.collidepoint(pg.mouse.get_pos()):
            self.scroll_y -= event.y * SCROLL_SPEED
            self._clamp_scroll()

    def _handle_mouse_down(self, event):
        if event.button == 1:
            if not self._try_start_scrollbar_drag(event.pos):
                self._start_drag(event)
        elif event.button == 3:
            self._try_remove_worn_at(event.pos)

    def _handle_mouse_up(self, event):
        if self.scrollbar_dragging:
            self.scrollbar_dragging = False
        else:
            self._stop_drag(event)

    def _start_drag(self, event):
        draggables = [i for i in self.gallery_items if isinstance(i, Draggable)]
        for item in reversed(draggables):
            draw_pos = pg.Vector2(item.pos) if item.grab else pg.Vector2(item.base_pos.x, item.base_pos.y - self.scroll_y)
            if item.image.get_rect(topleft=(int(draw_pos.x), int(draw_pos.y))).collidepoint(event.pos):
                item.grab   = True
                item.pos    = pg.Vector2(draw_pos)
                item.offset = pg.Vector2(event.pos) - item.pos
                break

    def _stop_drag(self, event):
        for item in [i for i in self.gallery_items if isinstance(i, Draggable) and i.grab]:
            item.grab = False
            if self.stage.collidepoint(event.pos):
                self._drop_on_stage(item)
            else:
                self._drop_outside_stage(item)
                item.image = item.thumb

    def _drop_outside_stage(self, item):
        if item.garment.id in self.worn_items:
            try:
                self.outfit.remove(item.garment)
            except Exception:
                pass
            del self.worn_items[item.garment.id]
        self._restore_to_gallery(item)
        item.pos = pg.Vector2(item.base_pos)

    def _drop_on_stage(self, item):
        cat_id = item.garment.category_id
        if self.outfit.can_add(item.garment):
            self.outfit.add(item.garment)
            self._apply_worn_visuals(item)
            self.worn_items[item.garment.id] = item
        else:
            # Remplace l'article existant de la même catégorie
            existing = self._find_worn_in_category(cat_id)
            if existing is not None:
                self.outfit.remove(existing.garment)
                self._restore_to_gallery(existing)
                self.worn_items.pop(existing.garment.id, None)
                self.outfit.add(item.garment)
                self._apply_worn_visuals(item)
                self.worn_items[item.garment.id] = item
            else:
                # Catégorie pleine sans remplaçable → retour sidebar
                item.pos = pg.Vector2(20, item.pos.y)

    def _find_worn_in_category(self, category_id):
        for it in self.worn_items.values():
            if it.garment.category_id == category_id:
                return it
        return None

    def _apply_worn_visuals(self, item):
        """Redimensionne le sprite à la taille du mannequin et positionne l'item dessus."""
        m_w, m_h    = self.mannequin_img.get_size()
        mannequin_x = self.stage.left + (self.stage.width - m_w) // 2 + 8
        item.stage_image = self._safe_load(item.garment.sprite_path, size=(m_w, m_h))
        item.pos         = pg.Vector2(mannequin_x, 80)

    def _restore_to_gallery(self, item):
        item.stage_image = None
        item.image       = item.thumb

    def _try_remove_worn_at(self, pos):
        """Retire via clic droit le vêtement porté sous le curseur (priorité au calque le plus haut)."""
        for it in sorted(self.worn_items.values(), key=lambda i: self._layer_for(i.garment), reverse=True):
            img  = it.stage_image if it.stage_image is not None else it.image
            rect = img.get_rect(topleft=(int(it.pos.x), int(it.pos.y)))
            if rect.collidepoint(pos):
                self.outfit.remove(it.garment)
                self._restore_to_gallery(it)
                del self.worn_items[it.garment.id]
                break

    # --- Validation ---

    def _validate_outfit(self):
        if not self.worn_items:
            return
        worn_garments = [item.garment for item in self.worn_items.values()]
        self.game.goto_result(self.mannequin, (self.theme_code, self.theme_label), self.outfit, worn_garments)

    # --- Mise à jour ---

    def update(self, dt):
        mouse = pg.mouse.get_pos()
        for item in [i for i in self.gallery_items if isinstance(i, Draggable) and i.grab]:
            item.pos = pg.Vector2(mouse) - item.offset

    # --- Dessin ---

    def draw(self, screen):
        self._draw_sidebar(screen)
        self._draw_gallery_items(screen)
        self._draw_stage(screen)
        self._draw_worn_items(screen)
        self._draw_scrollbar(screen)
        self._draw_hint(screen)

    def _draw_sidebar(self, screen):
        screen.blit(self.sidebar_bg, self.sidebar.topleft)

    def _draw_gallery_items(self, screen):
        for it in self.gallery_items:
            if isinstance(it, tuple) and it[0] == "label":
                _, surf, (x, y) = it
                draw_y = y - self.scroll_y
                if self.sidebar.top <= draw_y <= self.sidebar.bottom:
                    screen.blit(surf, (x, draw_y))
            elif isinstance(it, Draggable) and it.garment.id not in self.worn_items:
                if it.grab:
                    screen.blit(it.image, it.pos)
                else:
                    screen.blit(it.image, (it.base_pos.x, it.base_pos.y - self.scroll_y))

    def _draw_stage(self, screen):
        screen.blit(self.stage_bg,    self.stage.topleft)
        screen.blit(self.mannequin_img, (self.stage.left + 180, 80))

    def _draw_worn_items(self, screen):
        """Dessine les vêtements portés dans l'ordre des calques (shoes → accessories)."""
        for it in sorted(self.worn_items.values(), key=lambda i: self._layer_for(i.garment)):
            img = it.stage_image if it.stage_image is not None else it.image
            screen.blit(img, it.pos)

    def _draw_scrollbar(self, screen):
        if self.content_height <= self.sidebar.height:
            return
        view_ratio = self.sidebar.height / self.content_height
        thumb_h    = max(30, int(self.sidebar.height * view_ratio))
        max_scroll = self.content_height - self.sidebar.height
        thumb_y    = int((self.scroll_y / max_scroll) * (self.sidebar.height - thumb_h))
        rail  = pg.Rect(self.sidebar.right - 10, 10, 4,  self.sidebar.height - 20)
        thumb = pg.Rect(self.sidebar.right - 14, 10 + thumb_y, 12, thumb_h)
        pg.draw.rect(screen, (220, 220, 230), rail,  border_radius=2)
        pg.draw.rect(screen, (160, 160, 180), thumb, border_radius=4)

    def _draw_hint(self, screen):
        def _draw_label(surf, pos):
            r = surf.get_rect(topleft=pos)
            bg = pg.Surface(r.inflate(20, 10).size, pg.SRCALPHA)
            bg.fill((255, 255, 255, 200))
            screen.blit(bg, r.inflate(20, 10).topleft)
            screen.blit(surf, r)

        _draw_label(
            self.font.render("Molette = défiler | Entrée = valider", True, (30, 30, 60)),
            (self.stage.left + 20, self.game.h - 30),
        )
        title   = self.big.render(f"Thème: {self.theme_label}", True, (20, 20, 50))
        title_x = self.game.w - title.get_width() - 20
        _draw_label(title, (title_x, 20))

    # --- Ordre de superposition des calques ---

    def _category_name(self, garment) -> str:
        """Retourne le nom de la catégorie en majuscules à partir du category_id."""
        for c in self.categories:
            if c.id == garment.category_id:
                return c.name.upper()
        return ""

    def _layer_for(self, garment) -> int:
        """Indice de calque : 0 (fond) → 5 (avant). shoes < bottom < top < hair < face < accessories."""
        name = self._category_name(garment)

        def has(*tokens):
            return any(tok in name for tok in tokens)

        if has("SHOE", "CHAUSSURE", "FEET"):                                        return 0
        if has("BOTTOM", "BAS", "PANTS", "PANTALON", "SKIRT", "JUPE", "SHORT", "JEAN"): return 1
        if has("TOP", "HAUT", "SHIRT", "DRESS", "ROBE", "COAT", "JACKET", "PULL"):      return 2
        if has("HAIR", "CHEVEU", "HEAD", "CHAPEAU", "HAT"):                         return 3
        if has("FACE", "VISAGE", "MASK", "GLASSES", "LUNETTE"):                     return 4
        if has("ACCESSORY", "ACCESSOIRE", "ACC"):                                   return 5
        return 2  # défaut: traité comme un haut

    # --- Scrollbar interactive ---

    def _try_start_scrollbar_drag(self, pos) -> bool:
        if self.content_height <= self.sidebar.height:
            return False

        view_ratio = self.sidebar.height / self.content_height
        thumb_h    = max(30, int(self.sidebar.height * view_ratio))
        max_scroll = self.content_height - self.sidebar.height
        thumb_y    = int((self.scroll_y / max_scroll) * (self.sidebar.height - thumb_h)) if max_scroll > 0 else 0
        rail  = pg.Rect(self.sidebar.right - 10, 10, 4, self.sidebar.height - 20)
        thumb = pg.Rect(self.sidebar.right - 14, 10 + thumb_y, 12, thumb_h)

        if thumb.collidepoint(pos):
            self.scrollbar_dragging    = True
            self.scrollbar_drag_offset = pos[1] - thumb.top
            return True

        # Clic sur le rail → saut immédiat à la position cliquée
        in_rail = rail.collidepoint(pos) or (
            self.sidebar.right - 14 <= pos[0] <= self.sidebar.right - 2
            and 10 <= pos[1] <= self.sidebar.height - 10
        )
        if in_rail:
            rail_h         = self.sidebar.height - 20
            ratio          = (pos[1] - 10) / rail_h if rail_h > 0 else 0
            self.scroll_y  = int(ratio * max_scroll)
            self._clamp_scroll()
            self.scrollbar_dragging    = True
            self.scrollbar_drag_offset = thumb_h // 2
            return True

        return False

    def _update_scrollbar_drag(self, pos):
        if self.content_height <= self.sidebar.height:
            return
        view_ratio = self.sidebar.height / self.content_height
        thumb_h    = max(30, int(self.sidebar.height * view_ratio))
        max_scroll = self.content_height - self.sidebar.height
        rail_h     = self.sidebar.height - 20
        thumb_top  = max(0, min(pos[1] - 10 - self.scrollbar_drag_offset, rail_h - thumb_h))
        ratio      = thumb_top / (rail_h - thumb_h) if (rail_h - thumb_h) > 0 else 0
        self.scroll_y = int(ratio * max_scroll)
        self._clamp_scroll()

    # --- API publique de configuration de la galerie ---

    def set_gallery_layout(self, cols=None, thumb_size=None):
        """Recharge la galerie avec un nouveau nombre de colonnes ou une nouvelle taille de vignette."""
        if cols is not None:
            self.gallery_cols = max(1, int(cols))
        if thumb_size is not None:
            self.thumb_size = (int(thumb_size[0]), int(thumb_size[1]))
        self._build_gallery()
        self._clamp_scroll()
