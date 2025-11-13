import os  # opérations système (ex: vérifier l'existence d'un fichier)
import pygame as pg  # wrapper pygame importé sous le nom pg
from typing import Dict  # annotation de type pour dictionnaires
from scenes.base_scene import Scene  # classe de base pour les scènes
from repositories import CategoryRepo, GarmentRepo  # accès aux données catégories/vêtements
from services import Outfit  # logique de tenue (Outfit)

SCROLL_SPEED = 40  # Vitesse de défilement de la galerie

class Draggable:  # Petit objet qui représente un vêtement draggable (glissable)
    def __init__(self, garment, image, pos):
        self.garment = garment  # dataclass Garment associée
        self.image = image  # surface pygame contenant le sprite/aperçu
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


        # Surfaces (zones de l'écran)
        self.sidebar = pg.Rect(0, 0, 320, self.game.h)  # zone de gauche (galerie)
        self.stage = pg.Rect(320, 0, self.game.w-320, self.game.h)  # zone principale (mannequin)


        # Mannequin / background (placeholder si fichier manquant)
        self.mannequin_img = self._safe_load(self.mannequin.base_sprite_path, size=(360,520), fill=(230,220,220))
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
        """Remplit self.gallery_items avec des labels de catégories et des Draggable pour chaque vêtement."""
        y = 20
        for cat in self.categories:
            garments = GarmentRepo.by_category(cat.id)  # récupère les vêtements de la catégorie
            label = self.big.render(cat.name.upper(), True, (40,40,70))  # rend le titre de la catégorie
            self.gallery_items.append(("label", label, (20, y)))  # stocke un tuple pour le label
            y += 36
            x = 20
            for g in garments:
                img = self._safe_load(g.sprite_path, size=(80,80))  # charge ou placeholder
                d = Draggable( g, img, (x, y))  # crée un objet Draggable IMPORTANT  
                self.gallery_items.append(d)  # ajoute à la galerie
                x += 90
                max_x = max(max_x, x)
                if x > 220:  # passe à la ligne si dépassement de la largeur
                    x = 20
                    y += 90
            y += 100
        self.content_height = y  # hauteur totale du contenu de la galerie
    
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
            return # ignore les autres events de souris dans la sidebar
        
        # Simplified dispatcher for input events
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            mouse = pg.Vector2(event.pos)
            for item in reversed([i for i in self.gallery_items if isinstance(i, Draggable)]):
                displayed_pos = item.pos if item.grab else (pg.Vector2(item.pos.x, item.pos.y - self.scroll_y))
                r = item.image.get_rect(topleft=displayed_pos)
                if r.collidepoint(mouse):
                    item.grab = True
                    item.offset = mouse - display_pos
                    display_pos = item.pos if item.grab else (pg.Vector2(item.base_pos.x, item.base_pos.y - self.scroll_y))
                    r = item.image.get_rect(topleft=display_pos)
                    if r.collidepoint(mouse):
                        item.grab = True
                        item.offset = mouse - display_pos
                        item.offset = mouse - display_pos
                        break

        elif event.type == pg.MOUSEBUTTONUP and event.button == 1:
            for item in [i for i in self.gallery_items if isinstance(i, Draggable) and i.grab]:
                item.grab = False
                if self.stage.collidepoint(event.pos):
                    if self.outfit.can_add(item.garment):
                        self.outfit.add(item.garment)
                        item.pos = pg.Vector2(520, 120)  # position simple sur la scène
                        self.worn_items[item.garment.id] = item
                    else:
                        # replacer dans la galerie à sa position de base (pos de base déjà stockée dans item.pos? non)
                        # On ne change rien: la position "base" est le tuple stocké lors de la création (item.pos initiale),
                        # mais comme on l’a écrasée pendant le drag, on la remet à sa base logique:
                        pass
                else:
                    item.pos = pg.Vector2(item.base_pos.x, item.base_pos.y - self.scroll_y)
                    pass



    def _start_drag(self, event):
        """Begin dragging the topmost draggable under the cursor."""
        draggables = [i for i in self.gallery_items if isinstance(i, Draggable)]
        for item in reversed(draggables):
            if item.rect().collidepoint(event.pos):
                item.grab = True
                item.offset = pg.Vector2(event.pos) - item.pos  # calcule l'offset souris->image
                break

    def _stop_drag(self, event):
        """Handle release: place on stage, return to sidebar or remove from outfit."""
        grabbed = [i for i in self.gallery_items if isinstance(i, Draggable) and i.grab]
        for item in grabbed:
            item.grab = False
            if self.stage.collidepoint(event.pos):
                self._drop_on_stage(item)
            else:
                self._drop_outside_stage(item)

    def _drop_on_stage(self, item):
        """Try to add the item to the outfit and position it, otherwise return to sidebar."""
        if self.outfit.can_add(item.garment):
            self.outfit.add(item.garment)  # ajoute le vêtement à la tenue
            # position autour du mannequin (exemple)
            item.pos = pg.Vector2(520, 120)
            self.worn_items[item.garment.id] = item  # mémorise comme porté
        else:
            # Repositionner dans la sidebar si quota atteint
            item.pos = pg.Vector2(20, item.pos.y)

    def _drop_outside_stage(self, item):
        """Remove the item from the outfit if dropped outside the stage."""
        self.outfit.remove(item.garment)
        if item.garment.id in self.worn_items:
            del self.worn_items[item.garment.id]


    def update(self, dt):
        # Met à jour la position des objets en cours de drag
        mouse = pg.mouse.get_pos()
        for item in [i for i in self.gallery_items if isinstance(i, Draggable) and i.grab]:
            item.pos = pg.Vector2(mouse) - item.offset


    def draw(self, screen):
        # Sidebar
        pg.draw.rect(screen, (250,250,255), self.sidebar)
        title = self.big.render(f"Thème: {self.theme_label}", True, (20,20,50)) #a changer
        screen.blit(title, (20, self.game.h - 40)) #a changer

        for it in self.gallery_items:
            if isinstance(it, tuple) and it[0] == "label":
                surf, (x, y) = it[1], it[2]
                draw_y = y - self.scroll_y
                if self.sidebar.top <= draw_y <= self.sidebar.bottom:
                    screen.blit(surf, (x, draw_y))
            elif isinstance(it, Draggable):
                if it.grab:
                    screen.blit(it.image, it.pos)
                else:
                    draw_pos = (it.base_pos.x, it.base_pos.y - self.scroll_y)
                    screen.blit(it.image, draw_pos)

        pg.draw.rect(screen, (235,240,250), self.stage)
        screen.blit(self.mannequin_img, (self.stage.left + 180, 80))

        # Items portés par-dessus le mannequin
        for it in self.worn_items.values():
            screen.blit(it.image, it.pos)

        # Barre de scroll (thumb) dans la sidebar (optionnel)
        if self.content_height > self.sidebar.height:
            view_ratio = self.sidebar.height / self.content_height
            thumb_h = max(30, int(self.sidebar.height * view_ratio))
            max_scroll = self.content_height - self.sidebar.height
            thumb_y = int((self.scroll_y / max_scroll) * (self.sidebar.height - thumb_h))
            rail = pg.Rect(self.sidebar.right - 10, 10, 4, self.sidebar.height - 20)
            thumb = pg.Rect(self.sidebar.right - 14, 10 + thumb_y, 12, thumb_h)
            pg.draw.rect(screen, (220,220,230), rail, border_radius=2)
            pg.draw.rect(screen, (160,160,180), thumb, border_radius=4)
        
        hint = self.font.render("Molette = défiler | Entrée = valider", True, (30,30,60))
        screen.blit(hint, (self.stage.left + 20, self.game.h - 30))
