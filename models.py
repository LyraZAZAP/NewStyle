# ========================================
# MODÈLES DE DONNÉES (DATACLASSES)
# Définition des structures de données utilisées dans le jeu
# ========================================

# === IMPORTS ===
from dataclasses import dataclass  # Décorateur pour créer des dataclasses (classes de données simples)
from typing import Optional  # Type optionnel (champ peut être None)


# === CATÉGORIES DE VÊTEMENTS ===
@dataclass  # Décorateur transforme la classe en dataclass avec __init__, __repr__, etc.
class Category:  # Représente une catégorie de vêtements (Top, Bottom, Shoes, etc.)
    id: int  # Identifiant unique de la catégorie
    name: str  # Nom de la catégorie (ex: 'Top', 'Bottom', 'Shoes')
    max_items: int = 1  # Nombre maximum de vêtements de cette catégorie dans une tenue (défaut : 1)


# === VÊTEMENTS ===
@dataclass  # Transforme la classe en dataclass
class Garment:  # Représente un vêtement/article du jeu
    id: int  # Identifiant unique du vêtement
    name: str  # Nom du vêtement (ex: 'Red T-Shirt', 'Blue Jeans')
    category_id: int  # Référence vers la catégorie (lien vers Category.id)
    sprite_path: str  # Chemin vers l'image/sprite du vêtement
    score_theme: Optional[str] = None  # Thème pour lequel ce vêtement donne des points (optionnel)
    price: int = 0  # Prix du vêtement en devises du jeu (défaut : 0)


# === MANNEQUINS ===
@dataclass  # Transforme la classe en dataclass
class Mannequin:  # Représente un mannequin (personnage) qu'on peut habiller
    id: int  # Identifiant unique du mannequin
    name: str  # Nom du mannequin (ex: 'Lina', 'Alex')
    base_sprite_path: str  # Chemin vers l'image de base du mannequin (sans vêtements)


# === UTILISATEURS ===
@dataclass  # Transforme la classe en dataclass
class User:  # Représente un compte utilisateur du jeu
    id: int  # Identifiant unique de l'utilisateur
    username: str  # Nom d'utilisateur unique (pour la connexion)
    display_name: str  # Nom d'affichage du joueur
    avatar_path: str  # Chemin vers l'avatar de l'utilisateur
    created_at: Optional[str] = None  # Date de création du compte