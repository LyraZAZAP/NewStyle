from typing import List, Optional  # Types pour annotations (List, Optional)
from db import DB  # Instance globale de la DB définie dans db.py
from models import Category, Garment, Mannequin, User  # Dataclasses utilisées pour mapper les lignes
import bcrypt  # Bibliothèque pour hasher et vérifier les mots de passe
import json  # Pour exporter en JSON
from pathlib import Path  # Pour manipuler les chemins


class CategoryRepo:  # Répertoire d'accès aux catégories (utilise la BASE DE DONNÉES)
    @staticmethod  # Méthode statique, pas besoin d'instance
    def all() -> List[Category]:  # Retourne toutes les catégories de la table "category"
        # BASE DE DONNÉES : ouvre une connexion avec la table category
        with DB.connect() as con:  # Ouvre une connexion (context manager)
            # BASE DE DONNÉES : sélectionne TOUS les enregistrements de la table category
            rows = con.execute("SELECT * FROM category").fetchall()  # Récupère toutes les lignes ( rows ) de category, fetchall() = récupère toutes les lignes
        return [Category(**dict(r)) for r in rows]  # Mappe chaque ligne en dataclass Category


    @staticmethod  # Méthode utilitaire pour chercher par nom
    def by_name(name: str) -> Optional[Category]:  # Cherche une catégorie par son nom dans la BASE DE DONNÉES
        # BASE DE DONNÉES : ouvre une connexion
        with DB.connect() as con:  # Ouvre une connexion
            # BASE DE DONNÉES : sélectionne la catégorie avec un nom spécifique (utilise WHERE pour filtrer)
            r = con.execute("SELECT * FROM category WHERE name=?", (name,)).fetchone()  # Exécute la requête avec paramètre, r = result ou row ( abrevation de la ligne retournée  )
        return Category(**dict(r)) if r else None  # Retourne None si non trouvée


class GarmentRepo:  # Répertoire d'accès aux vêtements/articles (utilise la BASE DE DONNÉES)
    @staticmethod
    def by_category(category_id: int) -> List[Garment]:  # Liste les vêtements d'une catégorie depuis la BASE DE DONNÉES
        # BASE DE DONNÉES : ouvre une connexion à la table garment
        with DB.connect() as con:  # Ouvre une connexion
            # BASE DE DONNÉES : sélectionne tous les vêtements appartenant à une catégorie spécifique
            rows = con.execute("SELECT * FROM garment WHERE category_id=?", (category_id,)).fetchall()  # Récupère les lignes filtrées, rows est different de row ( rows = plusieurs lignes )
        return [Garment(**dict(r)) for r in rows]  # Mappe les lignes en objets Garment


    @staticmethod
    def all() -> List[Garment]:  # Retourne tous les vêtements de la BASE DE DONNÉES
        # BASE DE DONNÉES : ouvre une connexion à la table garment
        with DB.connect() as con:  # Ouvre une connexion
            # BASE DE DONNÉES : sélectionne TOUS les enregistrements de la table garment
            rows = con.execute("SELECT * FROM garment").fetchall()  # Sélectionne tous les vêtements
        return [Garment(**dict(r)) for r in rows]  # Mappe en dataclasses


class MannequinRepo:  # Répertoire d'accès aux mannequins (utilise la BASE DE DONNÉES)
    @staticmethod
    def all() -> List[Mannequin]:  # Retourne tous les mannequins de la BASE DE DONNÉES
        # BASE DE DONNÉES : ouvre une connexion à la table mannequin
        with DB.connect() as con:  # Ouvre une connexion
            # BASE DE DONNÉES : sélectionne TOUS les enregistrements de la table mannequin
            rows = con.execute("SELECT * FROM mannequin").fetchall()  # Récupère toutes les lignes de mannequin
        return [Mannequin(**dict(r)) for r in rows]  # Mappe en dataclasses Mannequin


class UserRepo:  # Répertoire d'accès aux utilisateurs (utilise la BASE DE DONNÉES)
    @staticmethod
    def all() -> List[User]:  # Retourne tous les utilisateurs enregistrés
        # BASE DE DONNÉES : ouvre une connexion à la table users
        with DB.connect() as con:  # Ouvre une connexion
            # BASE DE DONNÉES : sélectionne TOUS les utilisateurs SANS le hash du mot de passe (sécurité)
            rows = con.execute("SELECT id, username, display_name, avatar_path, created_at FROM users").fetchall()
        return [User(**dict(r)) for r in rows]  # Mappe en dataclasses User

    @staticmethod
    def by_id(user_id: int) -> Optional[User]:  # Cherche un utilisateur par son ID
        # BASE DE DONNÉES : ouvre une connexion
        with DB.connect() as con:  # Ouvre une connexion
            # BASE DE DONNÉES : sélectionne l'utilisateur avec cet ID
            r = con.execute("SELECT id, username, display_name, avatar_path, created_at FROM users WHERE id=?", (user_id,)).fetchone()
        return User(**dict(r)) if r else None  # Retourne None si non trouvé

    @staticmethod
    def by_username(username: str) -> Optional[User]:  # Cherche un utilisateur par son nom d'utilisateur
        # BASE DE DONNÉES : ouvre une connexion
        with DB.connect() as con:  # Ouvre une connexion
            # BASE DE DONNÉES : sélectionne l'utilisateur avec ce username
            r = con.execute("SELECT id, username, display_name, avatar_path, created_at FROM users WHERE username=?", (username,)).fetchone()
        return User(**dict(r)) if r else None  # Retourne None si non trouvé

    @staticmethod
    def create(username: str, display_name: str, password: str, avatar_path: str = "assets/avatars/default.png") -> Optional[User]:
        # Hashe le mot de passe avec bcrypt (sécurisé)
        password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
        
        try:
            # BASE DE DONNÉES : ouvre une connexion
            with DB.connect() as con:  # Ouvre une connexion
                # BASE DE DONNÉES : insère le nouvel utilisateur dans la table users
                con.execute(
                    "INSERT INTO users (username, display_name, password_hash, avatar_path) VALUES (?, ?, ?, ?)",
                    (username, display_name, password_hash, avatar_path)
                )
                con.commit()  # Valide la transaction
            # Récupère l'utilisateur créé
            return UserRepo.by_username(username)
        except Exception as e:
            print(f"Erreur lors de la création de l'utilisateur : {e}")
            return None

    @staticmethod
    def authenticate(username: str, password: str) -> Optional[User]:  # Vérifie les identifiants d'un utilisateur
        # BASE DE DONNÉES : ouvre une connexion
        with DB.connect() as con:  # Ouvre une connexion
            # BASE DE DONNÉES : récupère le hash du mot de passe de cet utilisateur
            r = con.execute("SELECT password_hash FROM users WHERE username=?", (username,)).fetchone()
        
        if r is None:
            return None  # Utilisateur non trouvé
        
        # Vérifie si le mot de passe fourni correspond au hash stocké
        password_hash = r['password_hash']
        if bcrypt.checkpw(password.encode(), password_hash):
            return UserRepo.by_username(username)  # Authentification réussie
        return None  # Mot de passe incorrect

    @staticmethod
    def export_to_json(filepath: str = "data/users_export.json") -> bool:
        """Exporte tous les utilisateurs en JSON pour consultation facile.
        
        Args:
            filepath (str): Chemin du fichier JSON (par défaut: data/users_export.json)
            
        Returns:
            bool: True si l'export a réussi, False sinon
        """
        try:
            users = UserRepo.all()
            
            # Convertit chaque User en dictionnaire
            users_data = []
            for user in users:
                users_data.append({
                    "id": user.id,
                    "username": user.username,
                    "display_name": user.display_name,
                    "avatar_path": user.avatar_path,
                    "created_at": user.created_at
                })
            
            # Crée le répertoire s'il n'existe pas
            Path(filepath).parent.mkdir(parents=True, exist_ok=True)
            
            # Écrit le JSON formaté (lisible)
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(users_data, f, indent=2, ensure_ascii=False)
            
            print(f"✓ Export réussi: {filepath} ({len(users)} utilisateurs)")
            return True
        except Exception as e:
            print(f"✗ Erreur lors de l'export JSON: {e}")
            return False

    @staticmethod
    def get_as_dict_list() -> List[dict]:
        """Retourne Les utilisateurs sous forme de liste de dictionnaires.
        
        Returns:
            List[dict]: Liste des utilisateurs au format dictionnaire
        """
        users = UserRepo.all()
        return [
            {
                "id": user.id,
                "username": user.username,
                "display_name": user.display_name,
                "avatar_path": user.avatar_path,
                "created_at": user.created_at
            }
            for user in users
        ]