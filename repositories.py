# Accès aux données — couche entre la BD et la logique métier

from typing import List, Optional
from db import DB
from models import Category, Garment, Mannequin, User
import bcrypt
import json
from pathlib import Path


class CategoryRepo:
    @staticmethod
    def all() -> List[Category]:
        with DB.connect() as con:
            rows = con.execute("SELECT * FROM category").fetchall()
        return [Category(**dict(r)) for r in rows]

    @staticmethod
    def by_name(name: str) -> Optional[Category]:
        with DB.connect() as con:
            r = con.execute("SELECT * FROM category WHERE name=?", (name,)).fetchone()
        return Category(**dict(r)) if r else None


class GarmentRepo:
    @staticmethod
    def by_category(category_id: int) -> List[Garment]:
        with DB.connect() as con:
            rows = con.execute("SELECT * FROM garment WHERE category_id=?", (category_id,)).fetchall()
        return [Garment(**dict(r)) for r in rows]

    @staticmethod
    def all() -> List[Garment]:
        with DB.connect() as con:
            rows = con.execute("SELECT * FROM garment").fetchall()
        return [Garment(**dict(r)) for r in rows]


class MannequinRepo:
    @staticmethod
    def all() -> List[Mannequin]:
        with DB.connect() as con:
            rows = con.execute("SELECT * FROM mannequin").fetchall()
        return [Mannequin(**dict(r)) for r in rows]


class UserRepo:
    @staticmethod
    def all() -> List[User]:
        # password_hash exclu intentionnellement pour des raisons de sécurité
        with DB.connect() as con:
            rows = con.execute(
                "SELECT id, username, display_name, avatar_path, created_at FROM users"
            ).fetchall()
        return [User(**dict(r)) for r in rows]

    @staticmethod
    def by_id(user_id: int) -> Optional[User]:
        with DB.connect() as con:
            r = con.execute(
                "SELECT id, username, display_name, avatar_path, created_at FROM users WHERE id=?",
                (user_id,)
            ).fetchone()
        return User(**dict(r)) if r else None

    @staticmethod
    def by_username(username: str) -> Optional[User]:
        with DB.connect() as con:
            r = con.execute(
                "SELECT id, username, display_name, avatar_path, created_at FROM users WHERE username=?",
                (username,)
            ).fetchone()
        return User(**dict(r)) if r else None

    @staticmethod
    def create(username: str, display_name: str, password: str,
               avatar_path: str = "assets/avatars/default.png") -> Optional[User]:
        password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
        try:
            with DB.connect() as con:
                con.execute(
                    "INSERT INTO users (username, display_name, password_hash, avatar_path) VALUES (?, ?, ?, ?)",
                    (username, display_name, password_hash, avatar_path)
                )
                con.commit()
            return UserRepo.by_username(username)
        except Exception as e:
            print(f"Erreur création utilisateur : {e}")
            return None

    @staticmethod
    def authenticate(username: str, password: str) -> Optional[User]:
        with DB.connect() as con:
            r = con.execute(
                "SELECT password_hash FROM users WHERE username=?", (username,)
            ).fetchone()
        if r is None:
            return None
        if bcrypt.checkpw(password.encode(), r['password_hash']):
            return UserRepo.by_username(username)
        return None

    @staticmethod
    def export_to_json(filepath: str = "data/users_export.json") -> bool:
        """Exporte tous les utilisateurs en JSON (sans mots de passe)."""
        try:
            users_data = [
                {
                    "id": u.id, "username": u.username,
                    "display_name": u.display_name, "avatar_path": u.avatar_path,
                    "created_at": u.created_at,
                }
                for u in UserRepo.all()
            ]
            Path(filepath).parent.mkdir(parents=True, exist_ok=True)
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(users_data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Erreur export JSON : {e}")
            return False
