# Structures de données du jeu

from dataclasses import dataclass
from typing import Optional


@dataclass
class Category:
    id: int
    name: str
    max_items: int = 1  # nb max de vêtements de cette catégorie par tenue


@dataclass
class Garment:
    id: int
    name: str
    category_id: int
    sprite_path: str
    score_theme: Optional[str] = None  # thème qui donne des points bonus (ex: "casual")
    price: int = 0


@dataclass
class Mannequin:
    id: int
    name: str
    base_sprite_path: str


@dataclass
class User:
    id: int
    username: str       # identifiant de connexion
    display_name: str   # pseudo affiché en jeu
    avatar_path: str
    created_at: Optional[str] = None
