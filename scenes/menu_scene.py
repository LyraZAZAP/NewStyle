import random  # utilitaire pour choisir aléatoirement
import os  # pour vérifier l'existence des fichiers
import pygame as pg  # pygame importé sous le nom pg
from scenes.base_scene import Scene  # classe de base pour les scènes
from ui.widgets import Button  # widget bouton réutilisable
from repositories import MannequinRepo  # repo pour récupérer les mannequins
from models import Mannequin  # modèle de données mannequin
from config import MENU_BG_PATH  # chemin du fond d'écran menu

# Liste des thèmes disponibles : chaque tuple contient (code interne, libellé affiché)
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
        self.title_font = pg.font.SysFont(None, 56)  # police grande pour le titre
        self.buttons = []  # liste des boutons interactifs du menu

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

        # --- Bouton toggle plein écran (coin supérieur droit) ---
        self.fullscreen_btn = pg.Rect(self.game.w - 120, 10, 110, 40)  # rectangle cliquable
        self.font_small = pg.font.SysFont(None, 24)  # petite police pour le texte du bouton

        # --- Chargement du fond d'écran ---
        # Charge l'image ou utilise une couleur unie par défaut si l'image n'existe pas
        self.bg = _load_background(MENU_BG_PATH, (self.game.w, self.game.h))

    def draw(self, screen):
        """
        Dessine tous les éléments visuels de l'écran menu.
        
        Args:
            screen (pygame.Surface): Surface principale du jeu
        """
        # --- Fond d'écran ---
        screen.blit(self.bg, (0, 0))  # dessiner le fond en premier plan (arrière-plan)
        
        # --- Titre du jeu ---
        title = self.title_font.render("Regardez mon beau jeu", True, (30, 30, 60))  # rend le texte
        title_rect = title.get_rect(center=(screen.get_width() // 2, 120))  # centre horizontalement
        
        # Encadré blanc semi-transparent derrière le titre pour améliorer la lisibilité
        bg_rect = title_rect.inflate(40, 20)  # ajoute 20px de padding horizontal, 10px vertical
        bg_surf = pg.Surface((bg_rect.width, bg_rect.height), pg.SRCALPHA)  # surface avec alpha
        bg_surf.fill((255, 255, 255, 200))  # blanc avec transparence (alpha=200/255)
        screen.blit(bg_surf, bg_rect.topleft)  # dessiner l'encadré
        screen.blit(title, title_rect)  # dessiner le titre par-dessus

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
        text = self.font_small.render(label, True, (255, 255, 255))  # texte blanc
        text_rect = text.get_rect(center=self.fullscreen_btn.center)  # centre le texte dans le bouton
        screen.blit(text, text_rect)

    def handle_event(self, event):
        """
        Traite les événements utilisateur (clics souris, touches clavier).
        
        Args:
            event (pygame.Event): Événement pygame à traiter
        """
        # --- Clic sur le bouton plein écran ---
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:  # clic gauche
            if self.fullscreen_btn.collidepoint(event.pos):  # si clic sur le bouton fullscreen
                self.game.toggle_fullscreen()  # bascule fenêtre <-> plein écran
                return  # empêche le traitement des autres boutons
        
        # --- Transmet l'événement aux autres boutons du menu ---
        for b in self.buttons:  # parcourt tous les boutons (ex: "Nouvelle partie")
            b.handle(event)  # chaque bouton gère ses propres clics