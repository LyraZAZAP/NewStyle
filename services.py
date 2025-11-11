from collections import defaultdict  # dict qui crée automatiquement une valeur par défaut pour les clés manquantes
from typing import Dict, List  # annotations de type
from models import Garment, Category  # dataclasses représentant vêtements et catégories


class Outfit:  # Représente une tenue composée de vêtements
    def __init__(self, categories: List[Category]):  # Initialise la tenue avec la liste des catégories
        self.max_by_cat = {c.id: c.max_items for c in categories}  # map id_categorie -> max_items autorisés
        self.items_by_cat: Dict[int, List[Garment]] = defaultdict(list)  # map id_categorie -> liste d'objets Garment


    def can_add(self, g: Garment) -> bool:  # Indique si on peut ajouter le vêtement g selon la limite par catégorie, g est un nom pour représenter un vêtement
        return len(self.items_by_cat[g.category_id]) < self.max_by_cat.get(g.category_id, 1)  # compare nombre actuel vs max 


    def add(self, g: Garment):  # Ajoute un vêtement à la tenue s'il est autorisé
        if self.can_add(g):
            self.items_by_cat[g.category_id].append(g)  # ajoute dans la liste correspondante


    def remove(self, g: Garment):  # Supprime un vêtement de la tenue s'il est présent
        if g in self.items_by_cat[g.category_id]:
            self.items_by_cat[g.category_id].remove(g)  # retire l'objet de la liste


    def all_items(self) -> List[Garment]:  # Retourne la liste plate de tous les vêtements de la tenue
        out = []  # liste résultat
        for _, lst in self.items_by_cat.items():  # parcourt chaque liste par catégorie
            out.extend(lst)  # ajoute les éléments dans la liste résultat
        return out  # renvoie tous les vêtements


class Scoring:  # Classe utilitaire pour calculer le score d'une tenue
    @staticmethod
    def score(theme_code: str, garments: List[Garment]) -> int:  # Calcule le score pour un thème donné
        base = 50  # score de base
        bonus = sum(15 for g in garments if g.score_theme == theme_code)  # +15 par vêtement correspondant au thème
        penalty = max(0, (len(garments) - 4)) * 5  # pénalité : 5 points par vêtement au-delà de 4 (surcharge d'accessoires)
        return max(0, base + bonus - penalty)  # retourne un score non-négatif