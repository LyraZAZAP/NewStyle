from typing import List, Optional  # Types pour annotations (List, Optional)
from db import DB  # Instance globale de la DB définie dans db.py
from models import Category, Garment, Mannequin  # Dataclasses utilisées pour mapper les lignes


class CategoryRepo:  # Répertoire d'accès aux catégories
    @staticmethod  # Méthode statique, pas besoin d'instance
    def all() -> List[Category]:  # Retourne toutes les catégories
        with DB.connect() as con:  # Ouvre une connexion (context manager)
            rows = con.execute("SELECT * FROM category").fetchall()  # Récupère toutes les lignes ( rows ) de category, fetchall() = récupère toutes les lignes
        return [Category(**dict(r)) for r in rows]  # Mappe chaque ligne en dataclass Category


    @staticmethod  # Méthode utilitaire pour chercher par nom
    def by_name(name: str) -> Optional[Category]:  # Cherche une catégorie par son nom
        with DB.connect() as con:  # Ouvre une connexion
            r = con.execute("SELECT * FROM category WHERE name=?", (name,)).fetchone()  # Exécute la requête avec paramètre, r = result ou row ( abrevation de la ligne retournée  )
        return Category(**dict(r)) if r else None  # Retourne None si non trouvée


class GarmentRepo:  # Répertoire d'accès aux vêtements/articles
    @staticmethod
    def by_category(category_id: int) -> List[Garment]:  # Liste les vêtements d'une catégorie
        with DB.connect() as con:  # Ouvre une connexion
            rows = con.execute("SELECT * FROM garment WHERE category_id=?", (category_id,)).fetchall()  # Récupère les lignes filtrées, rows est different de row ( rows = plusieurs lignes )
        return [Garment(**dict(r)) for r in rows]  # Mappe les lignes en objets Garment


    @staticmethod
    def all() -> List[Garment]:  # Retourne tous les vêtements
        with DB.connect() as con:  # Ouvre une connexion
            rows = con.execute("SELECT * FROM garment").fetchall()  # Sélectionne tous les vêtements
        return [Garment(**dict(r)) for r in rows]  # Mappe en dataclasses


class MannequinRepo:  # Répertoire d'accès aux mannequins
    @staticmethod
    def all() -> List[Mannequin]:  # Retourne tous les mannequins
        with DB.connect() as con:  # Ouvre une connexion
            rows = con.execute("SELECT * FROM mannequin").fetchall()  # Récupère toutes les lignes de mannequin
        return [Mannequin(**dict(r)) for r in rows]  # Mappe en dataclasses Mannequin