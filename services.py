# ========================================
# SERVICES - LOGIQUE MÉTIER DU JEU
# Classes pour gérer les tenues et le scoring
# ========================================

# === IMPORTS ===
from collections import defaultdict  # Dictionnaire qui crée automatiquement des valeurs par défaut
from typing import Dict, List  # Annotations de type : Dict (dictionnaire), List (liste)
from models import Garment, Category  # Importe les modèles de données


# === GESTION DES TENUES ===
class Outfit:  # Classe qui représente la tenue actuelle du mannequin
    def __init__(self, categories: List[Category]):
        """Initialise une tenue vide avec les catégories du jeu."""
        # Crée un dictionnaire {id_categorie -> nombre_max_articles}
        self.max_by_cat = {c.id: c.max_items for c in categories}
        # Crée un dictionnaire {id_categorie -> liste_de_vêtements}
        self.items_by_cat: Dict[int, List[Garment]] = defaultdict(list)

    def can_add(self, g: Garment) -> bool:
        """Vérifie si on peut ajouter un vêtement à la tenue."""
        # Compte combien de vêtements de cette catégorie sont déjà portés
        current_count = len(self.items_by_cat[g.category_id])
        # Récupère la limite maximum pour cette catégorie
        max_allowed = self.max_by_cat.get(g.category_id, 1)
        # Retourne True si on peut en ajouter un de plus
        return current_count < max_allowed

    def add(self, g: Garment):
        """Ajoute un vêtement à la tenue s'il est autorisé."""
        # Vérifie d'abord si c'est possible
        if self.can_add(g):
            # Ajoute le vêtement à la liste de sa catégorie
            self.items_by_cat[g.category_id].append(g)

    def remove(self, g: Garment):
        """Retire un vêtement de la tenue s'il est présent."""
        # Récupère la liste des vêtements de cette catégorie
        category_items = self.items_by_cat[g.category_id]
        # Retire le vêtement s'il est dans la liste
        if g in category_items:
            category_items.remove(g)

    def all_items(self) -> List[Garment]:
        """Retourne la liste complète de tous les vêtements portés."""
        out = []  # Liste résultat vide
        # Parcourt chaque liste de vêtements par catégorie
        for _, lst in self.items_by_cat.items():
            # Ajoute tous les vêtements de cette catégorie à la liste résultat
            out.extend(lst)
        # Retourne tous les vêtements mélangés
        return out


# === CALCUL DU SCORE ===
class Scoring:  # Classe utilitaire qui calcule le score d'une tenue
    @staticmethod  # Méthode statique (pas besoin d'instance de la classe)
    def score(theme_code: str, garments: List[Garment]) -> int:
        """Calcule le score d'une tenue selon le thème."""
        base = 50  # Score de base que tout le monde reçoit
        # Compte les vêtements avec le bon thème : +15 points pour chaque
        matching = sum(15 for g in garments if g.score_theme == theme_code)
        # Pénalité si trop de vêtements : -5 points par vêtement au-delà de 4
        penalty = max(0, (len(garments) - 4)) * 5
        # Retourne le score final (jamais négatif)
        return max(0, base + matching - penalty)