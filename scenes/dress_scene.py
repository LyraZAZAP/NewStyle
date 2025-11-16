import os  # opérations système (ex: vérifier l'existence d'un fichier)
import shutil  # pour supprimer récursivement les __pycache__
import pygame as pg  # wrapper pygame importé sous le nom pg
from typing import Dict  # annotation de type pour dictionnaires
from scenes.base_scene import Scene  # classe de base pour les scènes
from repositories import CategoryRepo, GarmentRepo  # accès aux données catégories/vêtements
from services import Outfit  # logique de tenue (Outfit)

SCROLL_SPEED = 40  # Vitesse de défilement de la galerie

class Draggable:  # Petit objet qui représente un vêtement draggable (glissable)
    def __init__(self, garment, image, pos):
        self.garment = garment  # dataclass Garment associée
        self.thumb = image  # vignette pour la galerie
        self.image = image  # surface pygame contenant le sprite/aperçu (alias)
        self.stage_image = None  # image utilisée quand l'article est porté (taille du mannequin)
        self.base_pos = pg.Vector2(pos)  # position de base dans la galerie
        self.pos = pg.Vector2(pos)  # position flottante (x,y)
        self.grab = False  # True si l'utilisateur tient l'objet
        self.offset = pg.Vector2(0,0)  # distance entre la souris et le coin supérieur gauche


    def rect(self):  # Retourne le rect (position/tailles) de l'image à la position courante
        r = self.image.get_rect(topleft=self.pos)
        return r


class DressScene(Scene):  # Écran d'habillage
    def __init__(self, game, mannequin, theme):
        super().__init__(game)  # conserve la référence vers l'objet jeu principal
        self.mannequin = mannequin  # mannequin sélectionné
        self.theme_code, self.theme_label = theme  # code et libellé du thème courant
        self.font = pg.font.SysFont(None, 24)  # petite police
        self.big = pg.font.SysFont(None, 36)  # police plus grande


        # Charge catégories & vêtements
        self.categories = CategoryRepo.all()  # récupère toutes les catégories
        self.outfit = Outfit(self.categories)  # objet Outfit qui gère la tenue
        self.gallery_items = [] # liste d'objets pour la galerie (Draggable ou labels)
        self.scroll_y = 0  # décalage vertical de la galerie
        self.content_height = 0  # hauteur totale du contenu de la galerie
        self.worn_items: Dict[int, Draggable] = {} # vêtements portés, clé = garment.id

        # État du scrollbar drag
        self.scrollbar_dragging = False
        self.scrollbar_drag_offset = 0

        # Surfaces (zones de l'écran)
        self.sidebar = pg.Rect(0, 0, 320, self.game.h)  # zone de gauche (galerie)
        self.stage = pg.Rect(320, 0, self.game.w-320, self.game.h)  # zone principale (mannequin)


        # Nettoie les __pycache__ éventuels pour éviter les modules dupliqués
        try:
            self._clean_pycache()
        except Exception:
            # ne pas empêcher le lancement en cas d'erreur sur la suppression
            pass

        # Mannequin / background (placeholder si fichier manquant)
        self.mannequin_img = self._safe_load(self.mannequin.base_sprite_path, size=(360,520), fill=(230,220,220))

        # Paramètres de mise en page de la galerie
        self.gallery_cols = 1           # mettre à 1 pour une seule image par ligne
        self.thumb_size = (280, 280)    # taille agrandie des vignettes (au lieu de 140x140)
        self.gallery_padding = 20       # marge intérieure (gauche/haut)
        self.gallery_gap = 0            # espacement entre vignettes (0 = pas d'écart)

        self._build_gallery()  # construit la galerie d'images à partir des catégories
        self._clamp_scroll()  # ajuste le décalage de la galerie


    def _safe_load(self, path, size=(120,120), fill=(200,200,210)):
        """Charge une image si elle existe, sinon retourne un placeholder simple."""
        if os.path.exists(path):
            img = pg.image.load(path).convert_alpha()
            return pg.transform.smoothscale(img, size)  # redimensionne proprement
        # Si le fichier est manquant, crée une surface remplie utilisée comme placeholder
        surf = pg.Surface(size, pg.SRCALPHA)
        surf.fill(fill)
        pg.draw.rect(surf, (120,120,140), surf.get_rect(), 2)
        return surf


    def _build_gallery(self):
        """Construit la galerie en respectant la taille des vignettes et le nombre de colonnes."""
        self.gallery_items.clear()
        pad = self.gallery_padding
        gap = self.gallery_gap
        tw, th = self.thumb_size
        cols = max(1, int(self.gallery_cols))

        y = pad
        for cat in self.categories:
            label = self.big.render(cat.name.upper(), True, (40,40,70))
            self.gallery_items.append(("label", label, (pad, y)))
            y += 36  # espace après le titre

            x = pad
            col = 0
            garments = GarmentRepo.by_category(cat.id)
            for g in garments:
                # éviter doublons
                # (les ids sont uniques par catégorie; si besoin, ajouter un set global)
                img = self._safe_load(g.sprite_path, size=(tw, th))
                d = Draggable(g, img, (x, y))
                self.gallery_items.append(d)

                col += 1
                if col >= cols:
                    col = 0
                    x = pad
                    y += th + gap
                else:
                    x += tw + gap

            # séparation entre catégories
            if col != 0:
                y += th + gap  # compléter la dernière ligne partielle
            y += gap * 2

        self.content_height = y

    def _clamp_scroll(self):
        max_scroll = max(0, self.content_height - self.sidebar.height)
        if self.scroll_y < 0:
            self.scroll_y = 0
        elif self.scroll_y > max_scroll:
            self.scroll_y = max_scroll

    def handle_event(self, event):
        if event.type == pg.MOUSEWHEEL:
            if self.sidebar.collidepoint(pg.mouse.get_pos()):
                self.scroll_y -= event.y * SCROLL_SPEED
                self._clamp_scroll()
            return
        
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            # Vérifier si clic sur scrollbar
            if self._try_start_scrollbar_drag(event.pos):
                return
            self._start_drag(event)

        elif event.type == pg.MOUSEBUTTONUP and event.button == 1:
            if self.scrollbar_dragging:
                self.scrollbar_dragging = False
                return
            self._stop_drag(event)

        elif event.type == pg.MOUSEMOTION:
            if self.scrollbar_dragging:
                self._update_scrollbar_drag(event.pos)
                return

        # Retirer un vêtement porté via clic droit (optionnel mais utile pour changer de tenue)
        elif event.type == pg.MOUSEBUTTONDOWN and event.button == 3:
            self._try_remove_worn_at(event.pos)

        elif event.type == pg.KEYDOWN and event.key == pg.K_RETURN:
            self._validate_outfit()

    # Réassure la présence des handlers de drag (écrase toute ancienne définition si nécessaire)
    def _start_drag(self, event):
        """Commence le drag sur l’item le plus haut sous le curseur (galerie)."""
        draggables = [i for i in self.gallery_items if isinstance(i, Draggable)]
        for item in reversed(draggables):
            draw_pos = pg.Vector2(item.pos) if item.grab else pg.Vector2(item.base_pos.x, item.base_pos.y - self.scroll_y)
            rect = item.image.get_rect(topleft=(int(draw_pos.x), int(draw_pos.y)))
            if rect.collidepoint(event.pos):
                item.grab = True
                item.pos = pg.Vector2(draw_pos)
                item.offset = pg.Vector2(event.pos) - item.pos
                break

    def _stop_drag(self, event):
        """Termine le drag: pose sur la scène si dans le stage, sinon retour/cleanup."""
        grabbed = [i for i in self.gallery_items if isinstance(i, Draggable) and i.grab]
        for item in grabbed:
            item.grab = False
            if self.stage.collidepoint(event.pos):
                self._drop_on_stage(item)
            else:
                self._drop_outside_stage(item)
                # Option: remettre l’image de vignette pour la galerie
                item.image = item.thumb

    def _drop_outside_stage(self, item):
        """Remet l'item dans la galerie s'il n'est pas déposé sur la scène."""
        # Si l'item était porté, le retirer de la tenue
        if item.garment.id in self.worn_items:
            try:
                self.outfit.remove(item.garment)
            except Exception:
                pass
            del self.worn_items[item.garment.id]
        # Restaurer l'affichage galerie
        self._restore_to_gallery(item)
        # Replacer logiquement à sa position de base (pour cohérence lors d'un prochain drag)
        item.pos = pg.Vector2(item.base_pos)

    # Helpers pour catégorie / remplacement
    def _get_category_id(self, garment):
        return getattr(garment, "category_id", None)

    def _find_worn_in_category(self, category_id):
        if category_id is None:
            return None
        for it in self.worn_items.values():
            if self._get_category_id(it.garment) == category_id:
                return it
        return None

    def _apply_worn_visuals(self, item):
        """Affecte stage_image et positionne l'item sur le mannequin."""
        m_img = self.mannequin_img
        m_w, m_h = m_img.get_width(), m_img.get_height()
        mannequin_x = self.stage.left + (self.stage.width - m_w) // 2 + 8
        mannequin_y = 80
        item.stage_image = self._safe_load(item.garment.sprite_path, size=(m_w, m_h))
        item.pos = pg.Vector2(mannequin_x, mannequin_y)

    def _restore_to_gallery(self, item):
        """Réinitialise l'item pour la galerie (sortie du mannequin)."""
        item.stage_image = None
        item.image = item.thumb

    def _try_remove_worn_at(self, pos):
        """Retire l'item porté cliqué (clic droit) si collision."""
        # Parcourt du haut vers le bas pour cliquer l'item visible au-dessus
        for it in sorted(self.worn_items.values(), key=lambda i: self._layer_for(i.garment), reverse=True):
            img = it.stage_image if getattr(it, 'stage_image', None) is not None else it.image
            rect = img.get_rect(topleft=(int(it.pos.x), int(it.pos.y)))
            if rect.collidepoint(pos):
                # enlever de l'outfit + remettre en galerie
                self.outfit.remove(it.garment)
                self._restore_to_gallery(it)
                del self.worn_items[it.garment.id]
                break

    def _drop_on_stage(self, item):
        """Try to add the item to the outfit and position it, otherwise return to sidebar.

        This variant allows replacing existing item from the same category.
        """
        cat_id = self._get_category_id(item.garment)
        if self.outfit.can_add(item.garment):
            self.outfit.add(item.garment)
            self._apply_worn_visuals(item)
            self.worn_items[item.garment.id] = item
        else:
            # Essayer de remplacer l'article existant de la même catégorie
            existing = self._find_worn_in_category(cat_id)
            if existing is not None:
                # retirer l'existant
                self.outfit.remove(existing.garment)
                self._restore_to_gallery(existing)
                if existing.garment.id in self.worn_items:
                    del self.worn_items[existing.garment.id]
                # ajouter le nouveau
                self.outfit.add(item.garment)
                self._apply_worn_visuals(item)
                self.worn_items[item.garment.id] = item
            else:
                # Pas possible de remplacer -> retour sidebar
                item.pos = pg.Vector2(20, item.pos.y)

    def update(self, dt):
        # Met à jour la position des objets en cours de drag
        mouse = pg.mouse.get_pos()
        for item in [i for i in self.gallery_items if isinstance(i, Draggable) and i.grab]:
            item.pos = pg.Vector2(mouse) - item.offset


    def _draw_sidebar(self, screen):
        """Draw the sidebar background."""
        pg.draw.rect(screen, (250,250,255), self.sidebar)

    def _draw_gallery_items(self, screen):
        """Draw gallery labels and draggable items in the sidebar."""
        for it in self.gallery_items:
            if isinstance(it, tuple) and it[0] == "label":
                surf, (x, y) = it[1], it[2]
                draw_y = y - self.scroll_y
                if self.sidebar.top <= draw_y <= self.sidebar.bottom:
                    screen.blit(surf, (x, draw_y))
            elif isinstance(it, Draggable) and it.garment.id not in self.worn_items:
                if it.grab:
                    screen.blit(it.image, it.pos)
                else:
                    draw_pos = (it.base_pos.x, it.base_pos.y - self.scroll_y)
                    screen.blit(it.image, draw_pos)

    def _draw_stage(self, screen):
        """Draw the stage background and mannequin."""
        pg.draw.rect(screen, (235,240,250), self.stage)
        screen.blit(self.mannequin_img, (self.stage.left + 180, 80))

    def _draw_worn_items(self, screen):
        """Draw items currently worn by the mannequin en respectant l'ordre des calques."""
        items = sorted(self.worn_items.values(), key=lambda it: self._layer_for(it.garment))
        for it in items:
            img = it.stage_image if getattr(it, 'stage_image', None) is not None else it.image
            screen.blit(img, it.pos)

    # --- Helpers d'ordre de superposition ---
    def _category_name(self, garment) -> str:
        """Retourne le nom de catégorie en MAJ, via category_id sinon via attributs textuels."""
        cid = getattr(garment, "category_id", None)
        if cid is not None:
            for c in self.categories:
                if getattr(c, "id", None) == cid:
                    return str(getattr(c, "name", "")).upper()
        # fallback: lire des champs textuels usuels
        for attr in ("category", "type", "name"):
            val = getattr(garment, attr, None)
            if isinstance(val, str):
                return val.upper()
        return ""

    def _layer_for(self, garment) -> int:
        """
        Renvoie l'indice de calque (0=fond -> 5=avant) selon la catégorie:
        shoes(0) < bottom(1) < top(2) < hair(3) < face(4) < accessories(5)
        """
        name = self._category_name(garment)

        def has(*tokens):
            return any(tok in name for tok in tokens)

        if has("SHOE", "CHAUSSURE", "FEET"):
            return 0  # shoes
        if has("BOTTOM", "BAS", "PANTS", "PANTALON", "SKIRT", "JUPE", "SHORT", "JEAN"):
            return 1  # bottom
        if has("TOP", "HAUT", "SHIRT", "DRESS", "ROBE", "COAT", "MANTEAU", "JACKET", "VESTE", "SWEATER", "PULL"):
            return 2  # top
        if has("HAIR", "CHEVEU", "HEAD", "CHAPEAU", "HAT"):
            return 3  # hair
        if has("FACE", "VISAGE", "MASK", "MASQUE", "GLASSES", "LUNETTE"):
            return 4  # face
        if has("ACCESSORY", "ACCESSOIRE", "ACC"):
            return 5  # accessories

        return 2  # défaut: milieu (top)

    def _draw_scrollbar(self, screen):
        """Draw the scrollbar thumb in the sidebar."""
        if self.content_height > self.sidebar.height:
            view_ratio = self.sidebar.height / self.content_height
            thumb_h = max(30, int(self.sidebar.height * view_ratio))
            max_scroll = self.content_height - self.sidebar.height
            thumb_y = int((self.scroll_y / max_scroll) * (self.sidebar.height - thumb_h))
            rail = pg.Rect(self.sidebar.right - 10, 10, 4, self.sidebar.height - 20)
            thumb = pg.Rect(self.sidebar.right - 14, 10 + thumb_y, 12, thumb_h)
            pg.draw.rect(screen, (220,220,230), rail, border_radius=2)
            pg.draw.rect(screen, (160,160,180), thumb, border_radius=4)

    def _draw_hint(self, screen):
        """Draw the hint text at the bottom of the stage."""
        hint = self.font.render("Molette = défiler | Entrée = valider", True, (30,30,60))
        screen.blit(hint, (self.stage.left + 20, self.game.h - 30))
        
        # Afficher le thème en haut à droite de la scène
        title = self.big.render(f"Thème: {self.theme_label}", True, (20,20,50))
        title_x = self.game.w - title.get_width() - 20
        screen.blit(title, (title_x, 20))

    def draw(self, screen):
        self._draw_sidebar(screen)
        self._draw_gallery_items(screen)
        self._draw_stage(screen)
        self._draw_worn_items(screen)
        self._draw_scrollbar(screen)
        self._draw_hint(screen)
    # Nouvelle méthode : supprime récursivement tous les dossiers __pycache__ sous le dossier du module
    def _clean_pycache(self):
        """
        Parcourt le dossier parent (le package NewStyle) et supprime tous les répertoires __pycache__.
        Permet d'éviter que des modules chargés depuis des chemins différents créent des doublons.
        """
        # on prend le dossier parent (le package NewStyle)
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        for root, dirs, files in os.walk(base_dir):
            for d in dirs:
                if d == "__pycache__":
                    full = os.path.join(root, d)
                    try:
                        shutil.rmtree(full)
                    except Exception:
                        # ignorer les erreurs de suppression pour ne pas casser l'init
                        pass

    def _validate_outfit(self):
        """Valide la tenue actuelle et déclenche la transition vers l'écran de fin."""
        # Vérifie qu'au moins un vêtement a été sélectionné
        if len(self.worn_items) == 0:
            print("Veuillez sélectionner au moins un vêtement.")
            return

        # Affiche la tenue validée (debug)
        print(f"Tenue validée avec {len(self.worn_items)} vêtement(s):")
        for garment_id, item in self.worn_items.items():
            print(f"  - {item.garment.name if hasattr(item.garment, 'name') else 'Inconnu'} (ID: {garment_id})")

        # Extraire les garments depuis worn_items
        worn_garments = [item.garment for item in self.worn_items.values()]
        
        # Déclenche la transition vers l'écran de résultat avec la liste des vêtements
        self.game.goto_result(self.mannequin, (self.theme_code, self.theme_label), self.outfit, worn_garments)

    def set_gallery_layout(self, cols: int | None = None, thumb_size: tuple[int, int] | None = None):
        """Change la mise en page du catalogue et reconstruit la galerie.
        Exemple: self.set_gallery_layout(1, (260, 260)) ou self.set_gallery_layout(2, (180, 180)).
        """
        if cols is not None:
            self.gallery_cols = max(1, int(cols))
        if thumb_size is not None:
            self.thumb_size = (int(thumb_size[0]), int(thumb_size[1]))
        self._build_gallery()
        self._clamp_scroll()

    def _try_start_scrollbar_drag(self, pos) -> bool:
        """Démarre le drag de scrollbar si clic sur thumb, ou jump si clic sur rail. Retourne True si traité."""
        if self.content_height <= self.sidebar.height:
            return False

        view_ratio = self.sidebar.height / self.content_height
        thumb_h = max(30, int(self.sidebar.height * view_ratio))
        max_scroll = self.content_height - self.sidebar.height
        thumb_y = int((self.scroll_y / max_scroll) * (self.sidebar.height - thumb_h)) if max_scroll > 0 else 0

        rail = pg.Rect(self.sidebar.right - 10, 10, 4, self.sidebar.height - 20)
        thumb = pg.Rect(self.sidebar.right - 14, 10 + thumb_y, 12, thumb_h)

        # Clic sur le thumb: drag
        if thumb.collidepoint(pos):
            self.scrollbar_dragging = True
            self.scrollbar_drag_offset = pos[1] - thumb.top
            return True

        # Clic sur le rail: jump à la position
        if rail.collidepoint(pos) or (self.sidebar.right - 14 <= pos[0] <= self.sidebar.right - 2 and 10 <= pos[1] <= self.sidebar.height - 10):
            # Calculer le scroll_y correspondant au clic
            rail_h = self.sidebar.height - 20
            click_y = pos[1] - 10
            ratio = click_y / rail_h if rail_h > 0 else 0
            self.scroll_y = int(ratio * max_scroll)
            self._clamp_scroll()
            # Commencer le drag pour suivre la souris
            self.scrollbar_dragging = True
            self.scrollbar_drag_offset = thumb_h // 2
            return True

        return False

    def _update_scrollbar_drag(self, pos):
        """Met à jour scroll_y en fonction du mouvement de la souris pendant le drag."""
        if self.content_height <= self.sidebar.height:
            return

        view_ratio = self.sidebar.height / self.content_height
        thumb_h = max(30, int(self.sidebar.height * view_ratio))
        max_scroll = self.content_height - self.sidebar.height
        rail_h = self.sidebar.height - 20

        # Calculer la position du thumb en fonction de la souris
        thumb_top = pos[1] - 10 - self.scrollbar_drag_offset
        thumb_top = max(0, min(thumb_top, rail_h - thumb_h))

        # Convertir en scroll_y
        ratio = thumb_top / (rail_h - thumb_h) if (rail_h - thumb_h) > 0 else 0
        self.scroll_y = int(ratio * max_scroll)
        self._clamp_scroll()
