from dataclasses import dataclass  # utilitaire pour créer des classes de données immutables/structurées
from typing import Optional  # type optionnel pour indiquer qu'un champ peut être None


@dataclass  # transforme la classe en dataclass (ajoute __init__, __repr__, etc.)
class Category:  # Représente une catégorie d'articles (top, bottom, etc.)
    id: int  # Identifiant unique de la catégorie
    name: str  # Nom de la catégorie (ex: 'top')
    max_items: int = 1  # Nombre max d'éléments sélectionnables pour cette catégorie (défaut 1)


@dataclass  # Dataclass représentant un vêtement/article
class Garment:  # Représente un vêtement disponible dans le jeu
    id: int  # Identifiant unique du vêtement
    name: str  # Nom lisible du vêtement
    category_id: int  # Référence vers l'id de la catégorie (category.id)
    sprite_path: str  # Chemin vers le sprite/image de l'article
    score_theme: Optional[str] = None  # Thème pour lequel l'article apporte des points (ou None)
    price: int = 0  # Prix de l'article (par défaut 0)


@dataclass  # Dataclass pour un mannequin (personnage habillé)
class Mannequin:  # Représente un mannequin exemple ou jouable
    id: int  # Identifiant du mannequin
    name: str  # Nom du mannequin
    base_sprite_path: str  # Chemin vers le sprite de base du mannequin