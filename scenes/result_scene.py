# ========================================
# SCÈNE DE RÉSULTAT
# Affiche le score et l'aperçu final après validation de la tenue
# ========================================

# === IMPORTS ===
import os  # Pour vérifier l'existence des fichiers
import pygame as pg  # Pygame pour l'affichage
from scenes.base_scene import Scene  # Classe de base pour les scènes
from services import Scoring  # Service de calcul de score
from config import RESULT_BG_PATH  # Chemin du fond d'écran résultat


def _load_background(path, size, fallback_color=(240, 240, 250)):
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


class ResultScene(Scene):  # Écran affichant le résultat après validation de la tenue
    def __init__(self, game, mannequin, theme, outfit, worn_garments):
        """
        Initialise l'écran de résultat avec le score, l'aperçu final et le fond d'écran.
        
        Args:
            game (Game): Référence à l'objet jeu principal
            mannequin (Mannequin): Mannequin utilisé dans la partie
            theme (tuple): (code_theme, libellé_theme) - ex: ("casual", "Casual")
            outfit (Outfit): Objet tenue contenant la logique métier
            worn_garments (list): Liste des vêtements portés (objets Garment)
        """
        super().__init__(game)  # conserve la référence au jeu
        self.mannequin = mannequin  # mannequin utilisé
        self.theme_code, self.theme_label = theme  # décompose le tuple thème
        self.outfit = outfit  # objet Outfit pour calcul du score
        self.font = pg.font.SysFont(None, 32)  # police moyenne pour les titres
        self.small_font = pg.font.SysFont(None, 24)  # petite police pour les détails

        # --- Zones d'affichage (panneaux gauche et droit) ---
        self.left_panel = pg.Rect(0, 0, self.game.w // 2, self.game.h)  # moitié gauche (score)
        self.right_panel = pg.Rect(self.game.w // 2, 0, self.game.w // 2, self.game.h)  # moitié droite (mannequin)

        # --- Chargement du fond d'écran ---
        self.bg = _load_background(RESULT_BG_PATH, (self.game.w, self.game.h))

        # --- Chargement du mannequin de base ---
        # Taille standard du mannequin (360x520px)
        self.mannequin_img = self._safe_load(mannequin.base_sprite_path, size=(360, 520))

        # --- Tri et redimensionnement des vêtements portés ---
        # Les vêtements sont triés par calque (shoes -> accessories) pour un affichage correct
        self.worn_garments = []
        for garment in sorted(worn_garments, key=lambda g: self._layer_for(g)):
            # Redimensionner chaque vêtement à la taille du mannequin (360x520)
            img = self._safe_load(garment.sprite_path, size=(360, 520))
            self.worn_garments.append(img)

        # --- Calcul du score et de l'argent gagné ---
        # Utilise le service Scoring pour évaluer la tenue selon le thème
        self.score = Scoring.score(self.theme_code, self.outfit.all_items())
        # Conversion simple du score en argent (score / 10 * 5)
        self.money = int(self.score / 10) * 5

    def _safe_load(self, path, size=(360, 520)):
        """
        Charge et redimensionne une image, ou retourne un placeholder si le fichier n'existe pas.
        
        Args:
            path (str): Chemin vers l'image
            size (tuple): Taille cible (largeur, hauteur)
        
        Returns:
            pygame.Surface: Image redimensionnée ou placeholder gris avec bordure
        """
        if os.path.exists(path):
            img = pg.image.load(path).convert_alpha()  # charge avec canal alpha
            return pg.transform.smoothscale(img, size)  # redimensionne proprement
        # Si le fichier est manquant, crée un placeholder gris avec bordure
        surf = pg.Surface(size, pg.SRCALPHA)
        surf.fill((230, 220, 220))  # fond gris clair
        pg.draw.rect(surf, (120, 120, 140), surf.get_rect(), 2)  # bordure gris foncé
        return surf

    def _layer_for(self, garment) -> int:
        """
        Détermine l'ordre de superposition d'un vêtement selon sa catégorie.
        Réutilise la même logique que DressScene pour cohérence visuelle.
        
        Args:
            garment (Garment): Vêtement à évaluer
        
        Returns:
            int: Indice de calque (0=fond -> 5=avant)
                0: chaussures, 1: bas, 2: haut, 3: cheveux, 4: visage, 5: accessoires
        """
        # Récupère le nom du vêtement et le convertit en majuscules pour comparaison
        name = getattr(garment, 'name', '').upper()
        
        # Détecte la catégorie par mots-clés dans le nom
        if any(tok in name for tok in ["SHOE", "CHAUSSURE"]):
            return 0  # chaussures (fond)
        if any(tok in name for tok in ["BOTTOM", "BAS", "PANTS", "PANTALON", "SKIRT", "JUPE"]):
            return 1  # bas (pantalon, jupe)
        if any(tok in name for tok in ["TOP", "HAUT", "SHIRT", "DRESS", "ROBE"]):
            return 2  # haut (t-shirt, robe)
        if any(tok in name for tok in ["HAIR", "CHEVEU", "HEAD"]):
            return 3  # cheveux
        if any(tok in name for tok in ["FACE", "VISAGE"]):
            return 4  # visage (masques, lunettes)
        if any(tok in name for tok in ["ACCESSORY", "ACCESSOIRE"]):
            return 5  # accessoires (avant-plan)
        return 2  # défaut: considéré comme un haut

    def handle_event(self, event):
        """
        Traite les événements utilisateur (touches clavier uniquement sur cet écran).
        
        Args:
            event (pygame.Event): Événement pygame à traiter
        """
        if event.type == pg.KEYDOWN:  # touche pressée
            if event.key == pg.K_r:  # touche R
                self.game.goto_menu()  # retour au menu principal
            if event.key == pg.K_n:  # touche N (nouvelle partie - placeholder)
                self.game.goto_menu()  # pour l'instant, renvoie aussi au menu

    def update(self, dt):
        """
        Met à jour la logique de la scène (aucune logique active sur cet écran).
        
        Args:
            dt (float): Temps écoulé depuis la dernière frame (en secondes)
        """
        pass  # écran statique, pas de logique à mettre à jour

    def draw(self, screen):
        """
        Dessine tous les éléments visuels de l'écran résultat.
        
        Args:
            screen (pygame.Surface): Surface principale du jeu
        """
        # --- Fond d'écran ---
        screen.blit(self.bg, (0, 0))  # dessiner le fond en premier

        # --- Panneau gauche: informations (score, argent, instructions) ---
        
        # Titre avec thème
        title = self.font.render(f"Résultat — thème {self.theme_label}", True, (20, 20, 50))
        title_rect = title.get_rect(topleft=(20, 20))
        # Encadré blanc semi-transparent pour améliorer la lisibilité
        bg_rect = title_rect.inflate(20, 10)  # padding: 10px horizontal, 5px vertical
        bg_surf = pg.Surface((bg_rect.width, bg_rect.height), pg.SRCALPHA)  # surface avec alpha
        bg_surf.fill((255, 255, 255, 200))  # blanc avec 200/255 d'opacité
        screen.blit(bg_surf, bg_rect.topleft)
        screen.blit(title, title_rect)

        # Score obtenu
        score_text = self.small_font.render(f"Score: {self.score}", True, (50, 50, 80))
        score_rect = score_text.get_rect(topleft=(20, 80))
        bg_rect = score_rect.inflate(20, 10)
        bg_surf = pg.Surface((bg_rect.width, bg_rect.height), pg.SRCALPHA)
        bg_surf.fill((255, 255, 255, 200))
        screen.blit(bg_surf, bg_rect.topleft)
        screen.blit(score_text, score_rect)

        # Argent gagné
        mo = self.small_font.render(f"Argent gagné: {self.money}", True, (30, 30, 60))
        mo_rect = mo.get_rect(topleft=(40, 160))
        bg_rect = mo_rect.inflate(20, 10)
        bg_surf = pg.Surface((bg_rect.width, bg_rect.height), pg.SRCALPHA)
        bg_surf.fill((255, 255, 255, 200))
        screen.blit(bg_surf, bg_rect.topleft)
        screen.blit(mo, mo_rect)

        # Instruction pour retour au menu
        hint = self.small_font.render("R = Retour menu", True, (60, 60, 80))
        hint_rect = hint.get_rect(topleft=(40, 220))
        bg_rect = hint_rect.inflate(20, 10)
        bg_surf = pg.Surface((bg_rect.width, bg_rect.height), pg.SRCALPHA)
        bg_surf.fill((255, 255, 255, 200))
        screen.blit(bg_surf, bg_rect.topleft)
        screen.blit(hint, hint_rect)

        # --- Panneau droit: mannequin habillé (aperçu final) ---
        
        # Calcul de la position pour centrer le mannequin dans le panneau droit
        mannequin_x = self.right_panel.centerx - self.mannequin_img.get_width() // 2
        mannequin_y = 80  # marge supérieure

        # Dessiner le mannequin de base en premier (arrière-plan)
        screen.blit(self.mannequin_img, (mannequin_x, mannequin_y))

        # Superposer les vêtements portés dans l'ordre des calques (shoes -> accessories)
        # Les vêtements ont déjà été triés dans __init__
        for garment_img in self.worn_garments:
            screen.blit(garment_img, (mannequin_x, mannequin_y))  # même position que le mannequin