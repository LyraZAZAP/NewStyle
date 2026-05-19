# Connexion à la base de données SQLite et authentification utilisateurs

import sys
import sqlite3
from pathlib import Path
import bcrypt
from config import DB_PATH


def _resource(relative: str) -> Path:
    """Retourne le chemin d'une ressource en lecture seule.

    PyInstaller --onedir place les fichiers --add-data dans sys._MEIPASS
    (sous-dossier _internal/). On doit y lire schema.sql et seed_data.sql.
    En développement, on lit simplement depuis le répertoire courant.
    """
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        return Path(sys._MEIPASS) / relative
    return Path(relative)


SCHEMA = _resource('data/schema.sql')
SEED   = _resource('data/seed_data.sql')


class Database:
    """Gère la connexion SQLite et les opérations sur les utilisateurs."""

    def __init__(self, path: str = DB_PATH):
        self.path = path
        self._connection = None
        # Crée le dossier contenant game.db (chemin absolu quand frozen → dossier du .exe)
        Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self):
        db_exists = Path(self.path).exists()
        with sqlite3.connect(self.path) as con:
            # Crée les tables si elles n'existent pas encore
            con.executescript(SCHEMA.read_text(encoding='utf-8'))
            # Insère les données de départ uniquement à la première création
            if not db_exists:
                con.executescript(SEED.read_text(encoding='utf-8'))

            # Migration : ajoute les colonnes absentes pour les anciennes bases de données
            try:
                cols = [r[1] for r in con.execute("PRAGMA table_info(users)").fetchall()]
            except sqlite3.OperationalError:
                cols = []

            if 'display_name' not in cols:
                con.execute("ALTER TABLE users ADD COLUMN display_name TEXT NOT NULL DEFAULT ''")
            if 'avatar_path' not in cols:
                con.execute("ALTER TABLE users ADD COLUMN avatar_path TEXT NOT NULL DEFAULT 'assets/avatars/default.png'")
            if 'username' not in cols:
                # Ancienne colonne 'login' → renommer en 'username'
                if 'login' in cols:
                    con.execute("ALTER TABLE users ADD COLUMN username TEXT")
                    con.execute("UPDATE users SET username = login WHERE username IS NULL OR username = ''")
                else:
                    con.execute("ALTER TABLE users ADD COLUMN username TEXT NOT NULL DEFAULT ''")

            con.commit()

    def connect(self):
        """Ouvre une connexion (rows accessibles par nom de colonne)."""
        con = sqlite3.connect(self.path)
        con.row_factory = sqlite3.Row
        self._connection = con
        return con

    def close(self):
        if self._connection:
            try:
                self._connection.close()
                self._connection = None
            except Exception as e:
                print(f"Erreur fermeture DB : {e}")

    # --- Authentification ---

    def hash_password(self, password: str) -> bytes:
        return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

    def verify_password(self, password: str, password_hash: bytes) -> bool:
        return bcrypt.checkpw(password.encode("utf-8"), password_hash)

    def create_user(self, username: str, display_name: str, password: str, avatar_path: str = None):
        """Crée un utilisateur. Retourne (True, message) ou (False, erreur)."""
        username     = username.strip()
        display_name = display_name.strip()
        if len(username) < 3:
            return False, "Identifiant trop court (min 3)."
        if len(display_name) < 3:
            return False, "Pseudo trop court (min 3)."
        if len(password) < 6:
            return False, "Mot de passe trop court (min 6)."

        pw_hash     = self.hash_password(password)
        avatar_path = avatar_path or 'assets/avatars/default.png'

        try:
            with sqlite3.connect(self.path) as con:
                con.execute(
                    "INSERT INTO users (username, display_name, avatar_path, password_hash) VALUES (?, ?, ?, ?)",
                    (username, display_name, avatar_path, pw_hash)
                )
                con.commit()
            return True, "Compte créé !"
        except sqlite3.IntegrityError:
            return False, "Identifiant déjà utilisé."
        except Exception as e:
            return False, f"Erreur DB: {e}"

    def authenticate(self, username: str, password: str):
        """Vérifie les identifiants. Retourne (True, message, user_dict) ou (False, erreur, None)."""
        username = username.strip()
        with sqlite3.connect(self.path) as con:
            con.row_factory = sqlite3.Row
            row = con.execute(
                "SELECT id, display_name, avatar_path, password_hash FROM users WHERE username = ?",
                (username,)
            ).fetchone()

        if row is None:
            return False, "Utilisateur introuvable.", None

        if self.verify_password(password, row["password_hash"]):
            return True, "Connexion réussie !", {
                "id":           row["id"],
                "display_name": row["display_name"],
                "avatar_path":  row["avatar_path"],
            }
        return False, "Mot de passe incorrect.", None


# Instance globale partagée par toute l'application
DB = Database()
