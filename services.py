# Logique métier : gestion de tenue et calcul du score

from collections import defaultdict
from typing import Dict, List
from models import Garment, Category


class Outfit:
    """Tenue portée par le mannequin — gère les quotas par catégorie."""

    def __init__(self, categories: List[Category]):
        self.max_by_cat = {c.id: c.max_items for c in categories}
        self.items_by_cat: Dict[int, List[Garment]] = defaultdict(list)

    def can_add(self, g: Garment) -> bool:
        return len(self.items_by_cat[g.category_id]) < self.max_by_cat.get(g.category_id, 1)

    def add(self, g: Garment):
        if self.can_add(g):
            self.items_by_cat[g.category_id].append(g)

    def remove(self, g: Garment):
        lst = self.items_by_cat[g.category_id]
        if g in lst:
            lst.remove(g)

    def all_items(self) -> List[Garment]:
        out = []
        for lst in self.items_by_cat.values():
            out.extend(lst)
        return out


class Scoring:
    @staticmethod
    def score(theme_code: str, garments: List[Garment]) -> int:
        """Score = 50 de base + 15 par vêtement au bon thème - 5 par vêtement au-delà de 4."""
        base     = 50
        matching = sum(15 for g in garments if g.score_theme == theme_code)
        penalty  = max(0, len(garments) - 4) * 5
        return max(0, base + matching - penalty)
