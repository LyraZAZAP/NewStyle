# ========================================
# SCÈNE MENU PRINCIPAL
# Affiche après la connexion avec avatar et bouton "Nouvelle partie"
# ========================================

# === IMPORTS ===
import random  # Pour choisir thème et mannequin aléatoires
import os  # Pour vérifier l'existence des fichiers
import pygame as pg  # Pygame pour l'affichage et les événements
from scenes.base_scene import Scene  # Classe de base pour les scènes
from ui.widgets import Button  # Widget bouton réutilisable
from repositories import MannequinRepo  # Récupère les mannequins de la BD
from models import Mannequin  # Modèle de données mannequin
from config import MENU_BG_PATH  # Chemin du fond d'écran
from ui.music_disc import MusicDiscWidget  # Widget disque musical tournant
from config import DISC_IMG_PATH, DISC_BTN_PATH, TITLE_IMG_PATH  # Images du disque et titre

# === THÈMES DISPONIBLES ===
# Liste des (code_interne, libellé_affiché) pour le jeu
THEMES = [
    ("casual", "Casual"),      # Style décontracté
    ("soiree", "Soirée"),      # Tenue élégante
    ("colorful", "Colorful"),  # Style coloré
    ("chic", "Chic"),          # Style chic
]


def _load_background(path, size, fallback_color=(240, 240, 245)):
    """
    Charge et redimensionne une image de fond, ou retourne une surface unie si le fichier n'existe pas.
    
    Args:
        path (str): Chemin vers l'image de fond
        size (tuple): Taille cible (largeur, hauteur)
        fallback_color (tuple): Couleur de repli si l'image n'existe pas
    
    Returns:
        pygame.Surface: Image redimensionnée ou surface unie
    """
    if os.path.exists(path):
        img = pg.image.load(path)
        # Convertir pour optimiser le rendu (avec ou sans alpha selon l'image)
        img = img.convert() if img.get_alpha() is None else img.convert_alpha()
        return pg.transform.smoothscale(img, size)  # redimensionnement de qualité
    # Si l'image n'existe pas, créer une surface unie
    surf = pg.Surface(size)
    surf.fill(fallback_color)
    return surf


class MenuScene(Scene):  # Écran d'accueil / menu principal
    def __init__(self, game):
        """
        Initialise l'écran menu avec le titre, les boutons et le fond d'écran.
        
        Args:
            game (Game): Référence à l'objet jeu principal
        """
        super().__init__(game)  # conserve la référence au jeu
        self.title_font = pg.font.SysFont(None, 70)  # police grande pour le titre
        self.buttons = []  # liste des boutons interactifs du menu
        self.bg_offset = pg.Vector2(0, 0) # pour l'effet de parallaxe du fond d'écran que ça tremble pas
        # --- Callback pour le bouton "Nouvelle partie" ---
        def start_random():
            """
            Démarre une nouvelle partie avec un thème et un mannequin choisis aléatoirement.
            Appelé lors du clic sur le bouton "Nouvelle partie".
            """
            theme = random.choice(THEMES)  # choisit un thème au hasard dans la liste
            mannequins = MannequinRepo.all()  # récupère tous les mannequins de la BDD
            
            # Sécurité : si la BDD est vide, utiliser un mannequin par défaut
            default_mannequin = Mannequin(0, 'Lina', 'assets/mannequins/mannequin_base.png')
            m = random.choice(mannequins) if mannequins else default_mannequin
            
            # Transition vers la scène d'habillage avec le mannequin et thème sélectionnés
            self.game.goto_dress(m, theme)

        # Création du bouton "Nouvelle partie" (position, texte, callback)
        self.buttons.append(Button((412, 320, 200, 50), "Nouvelle partie", start_random))

        # --- Bouton "Quitter" ---
        def quit_game():
            """Quitte le jeu proprement."""
            self.game.running = False

        self.buttons.append(Button((412, 390, 200, 50), "Quitter", quit_game))

        # --- Bouton toggle plein écran (coin supérieur droit) ---
        self.fullscreen_btn = pg.Rect(self.game.w - 120, 10, 110, 40)  # rectangle cliquable
        self.font_small = pg.font.SysFont(None, 30)  # petite police pour le texte du bouton
        
                # --- Badge utilisateur (avatar + pseudo) ---
        self.avatar_surf = None
        self.pseudo_surf = None

        user = getattr(self.game, "current_user", None)

        if user:
            avatar_path = user.get("avatar_path", "assets/avatars/default.png")
            pseudo = user.get("display_name", "Invité")

            try:
                img = pg.image.load(avatar_path)
                img = img.convert_alpha() if img.get_alpha() is not None else img.convert()
                self.avatar_surf = pg.transform.smoothscale(img, (64, 64))
            except Exception as e:
                print("Erreur chargement avatar:", e)
                self.avatar_surf = None

            self.pseudo_surf = self.font_small.render(pseudo, True, (30, 30, 60))
        else:
            # pas connecté
            self.pseudo_surf = self.font_small.render("Invité", True, (30, 30, 60))


        # --- Chargement du fond d'écran ---
        # Charge l'image ou utilise une couleur unie par défaut si l'image n'existe pas
        self.bg = _load_background(MENU_BG_PATH, (self.game.w, self.game.h))
        
                # Fond parallax (image + grande que l'écran)
        self.bg_img = pg.image.load(MENU_BG_PATH)
        self.bg_img = self.bg_img.convert() if self.bg_img.get_alpha() is None else self.bg_img.convert_alpha()

        # on la rend un peu plus grande que la fenêtre (ex: +8%)
        scale = 1.08
        bw, bh = int(self.game.w * scale), int(self.game.h * scale)
        self.bg_scaled = pg.transform.smoothscale(self.bg_img, (bw, bh))

        # intensité du mouvement (en pixels max)
        self.parallax = 25
        
        # === CHARGEMENT DE L'IMAGE DU TITRE ===
        # Charge et redimensionne l'image du titre depuis assets/titles/
        try:
            # Charge l'image du titre
            title_img = pg.image.load(TITLE_IMG_PATH)
            # Optimise le rendu avec convert_alpha (avec transparence si besoin)
            title_img = title_img.convert_alpha() if title_img.get_alpha() is not None else title_img.convert()
            # Redimensionne le titre pour l'adapter au centre de l'écran
            # Largeur max : 600 pixels, hauteur : proportionnelle
            title_width = min(600, self.game.w - 40)  # Laisse 20px de marge de chaque côté
            # Calcule la hauteur proportionnelle pour garder les proportions
            img_ratio = title_img.get_height() / title_img.get_width()
            title_height = int(title_width * img_ratio)
            # Redimensionne avec qualité
            self.title_img = pg.transform.smoothscale(title_img, (title_width, title_height))
        except Exception as e:
            # Si le chargement échoue, crée un placeholder gris
            print(f"Erreur chargement titre image : {e}")
            self.title_img = None
        
        # Disque musical qui tourne en bas-gauche
        # Le bouton au centre permet de passer à la musique suivante
        self.music_disc = MusicDiscWidget(
            self.game,
            DISC_IMG_PATH,
            DISC_BTN_PATH,
            size=600,            # taille du disque en pixels
            anchor="bottomleft",   # positionnement dans le coin inférieur gauche
            margin=-175,           # marge depuis le bord (négatif pour décaler partiellement hors écran)
            speed_deg=60         # vitesse de rotation
        )

        

    def draw(self, screen):
        """
        Dessine tous les éléments visuels de l'écran menu.
        
        Args:
            screen surface principale du jeu
        """
        # --- Fond d'écran effet paralaxe ---
        mx, my = pg.mouse.get_pos()

        # centre de la fenêtre (0..w, 0..h) -> (-1..1)
        nx = (mx / self.game.w) * 2 - 1
        ny = (my / self.game.h) * 2 - 1

        # Décalage max = self.parallax
        dx = int(-nx * self.parallax)
        dy = int(-ny * self.parallax)

        # on centre l'image et on applique le décalage
        bw, bh = self.bg_scaled.get_size()
        x = (self.game.w - bw) // 2 + dx
        y = (self.game.h - bh) // 2 + dy

        screen.blit(self.bg_scaled, (x, y))
        
        self.music_disc.draw(screen)

        
                # --- Affichage avatar + pseudo en haut à gauche ---
        badge_x, badge_y = 20, 20  # position du badge (avatar + pseudo)

        if self.avatar_surf:
            screen.blit(self.avatar_surf, (badge_x, badge_y))

        if self.pseudo_surf:
            # pseudo sous l’avatar
            screen.blit(self.pseudo_surf, (badge_x, badge_y + 70))


        # --- Titre du jeu ---
        # Affiche l'image du titre à la place du texte "Style Dress"
        if self.title_img is not None:
            # Centre l'image du titre horizontalement
            title_rect = self.title_img.get_rect(center=(screen.get_width() // 2, 150)) 
            # Affiche l'image du titre
            screen.blit(self.title_img, title_rect)
        else:
            # Fallback : affiche du texte si l'image n'a pas pu être chargée
            title = self.title_font.render("Style Dress", True, (30, 30, 60))
            title_rect = title.get_rect(center=(screen.get_width() // 2, 120))
            # Encadré blanc semi-transparent pour lisibilité
            bg_rect = title_rect.inflate(40, 20)
            bg_surf = pg.Surface((bg_rect.width, bg_rect.height), pg.SRCALPHA)
            bg_surf.fill((255, 255, 255, 200))
            screen.blit(bg_surf, bg_rect.topleft)
            screen.blit(title, title_rect)

        # --- Boutons du menu ---
        for b in self.buttons:  # dessine tous les boutons (ici: "Nouvelle partie")
            b.draw(screen)

        # --- Bouton plein écran ---
        # Couleur change au survol (hover effect)
        color = (100, 150, 255) if self.fullscreen_btn.collidepoint(pg.mouse.get_pos()) else (249,216,251) 
        pg.draw.rect(screen, color, self.fullscreen_btn, border_radius=5)  # fond du bouton
        pg.draw.rect(screen, (255, 255, 255), self.fullscreen_btn, 2, border_radius=5)  # bordure blanche

        # Texte du bouton change selon l'état actuel (fenêtré ou plein écran)
        label = "Plein écran" if not self.game.is_fullscreen else "Fenêtré"
        text = self.font_small.render(label, True, (255, 255, 255))  # texte de couleur ( rose-violet clair)
        text_rect = text.get_rect(center=self.fullscreen_btn.center)  # centre le texte dans le bouton
        screen.blit(text, text_rect)
        

    def handle_event(self, event):
        """
        Traite les événements utilisateur (clics souris, touches clavier).
        
        Args:
            event (pygame.Event): Événement pygame à traiter
        """
        # --- Clic sur le bouton plein écran ---
        if self.music_disc.handle_event(event):
            return

        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:  # clic gauche
            if self.fullscreen_btn.collidepoint(event.pos):  # si clic sur le bouton fullscreen
                self.game.toggle_fullscreen()  # bascule fenêtre <-> plein écran
                return  # empêche le traitement des autres boutons
        
        # --- Transmet l'événement aux autres boutons du menu ---
        for b in self.buttons:  # parcourt tous les boutons (ex: "Nouvelle partie")
            b.handle(event)  # chaque bouton gère ses propres clics
            
    def update(self, dt):
        self.music_disc.update(dt)
