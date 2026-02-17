# ========================================
# IMPORTS - Bibliothèques utilisées
# ========================================
import sqlite3  # Permet de gérer une base de données SQLite
from pathlib import Path  # Utilitaire pour manipuler les chemins de fichiers de manière robuste
import bcrypt  # Bibliothèque pour hasher et vérifier les mots de passe de manière sécurisée
from config import DB_PATH  # Importe le chemin par défaut de la base de données depuis config.py

# ========================================
# CHEMINS DES FICHIERS SQL
# ========================================
# Chemin vers le fichier de schéma SQL (structure des tables)
SCHEMA = Path('data/schema.sql')
# Chemin vers le fichier de données initiales (données pré-remplies)
SEED = Path('data/seed_data.sql')

# ========================================
# CLASSE DATABASE - Gestion de la base de données
# ========================================
class Database:
    """Classe pour gérer la connexion et les opérations sur la base de données."""
    
    def __init__(self, path: str = DB_PATH):
        """Initialise la base de données.
        
        Args:
            path (str): Chemin vers le fichier de la base de données
        """
        # Stocke le chemin de la base de données
        self.path = path
        # Initialise la connexion à None (pas encore connecté)
        self._connection = None
        # Crée le dossier 'data' s'il n'existe pas
        Path('data').mkdir(exist_ok=True)
        # Initialise la structure et les données de la base de données
        self._init_db()

    def _init_db(self):
        """Initialise la base de données en exécutant le schéma et les données initiales."""
        # Se connecte à la base de données (crée le fichier s'il n'existe pas)
        with sqlite3.connect(self.path) as con:
            # Exécute le fichier de schéma pour créer les tables
            con.executescript(SCHEMA.read_text(encoding='utf-8'))
            # Exécute le fichier de données initiales pour peupler les tables
            con.executescript(SEED.read_text(encoding='utf-8'))

            # Vérifie que la table users contient les colonnes nécessaires
            try:
                cur = con.execute("PRAGMA table_info(users)")
                cols = [r[1] for r in cur.fetchall()]
            except sqlite3.OperationalError:
                cols = []

            # Si une colonne manque, on l'ajoute en utilisant ALTER TABLE (avec valeur par défaut)
            if 'display_name' not in cols:
                con.execute("ALTER TABLE users ADD COLUMN display_name TEXT NOT NULL DEFAULT ''")
            if 'avatar_path' not in cols:
                con.execute("ALTER TABLE users ADD COLUMN avatar_path TEXT NOT NULL DEFAULT 'assets/avatars/default.png'")
            con.commit()

    def connect(self):
        """Établit une connexion à la base de données.
        
        Returns:
            sqlite3.Connection: La connexion à la base de données
        """
        # Crée une connexion à la base de données sqlite
        con = sqlite3.connect(self.path)
        # Configure le factory pour retourner des dictionnaires au lieu de tuples
        # Cela permet d'accéder aux colonnes par leur nom (ex: row['id'])
        con.row_factory = sqlite3.Row
        # Stocke la connexion en tant que variable d'instance
        self._connection = con
        return con

    def close(self):
        """Ferme la connexion à la base de données de manière sécurisée."""
        # Vérifie s'il existe une connexion active
        if self._connection:
            try:
                # Ferme la connexion
                self._connection.close()
                # Réinitialise la variable de connexion
                self._connection = None
            except Exception as e:
                # Affiche un message d'erreur si la fermeture échoue
                print(f"Erreur lors de la fermeture de la connexion DB : {e}")

        # Arrête le gestionnaire de SQLite
        try:
            sqlite3.shutdown()
        except Exception:
            # Ignore les erreurs lors de l'arrêt
            pass

    # ========================================
    # FONCTIONS UTILISATEUR - Authentification
    # ========================================

    def hash_password(self, password: str) -> bytes:
        """Hache un mot de passe de manière sécurisée avec bcrypt.
        
        Args:
            password (str): Le mot de passe à hasher
            
        Returns:
            bytes: Le mot de passe hashé
        """
        # Convertit le mot de passe en bytes et le hache avec bcrypt (salé automatiquement)
        return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

    def verify_password(self, password: str, password_hash: bytes) -> bool:
        """Vérifie si un mot de passe correspond à son hash.
        
        Args:
            password (str): Le mot de passe en clair à vérifier
            password_hash (bytes): Le hash du mot de passe stocké en base
            
        Returns:
            bool: True si le mot de passe est correct, False sinon
        """
        # Utilise bcrypt pour vérifier que le mot de passe correspond au hash
        return bcrypt.checkpw(password.encode("utf-8"), password_hash)

    def create_user(self, username: str, display_name: str, password: str, avatar_path: str = None):
        """Crée un nouvel utilisateur. `avatar_path` est optionnel.
        Si `avatar_path` est None, on utilise un avatar par défaut.
        """
        username = username.strip()
        display_name = display_name.strip()

        if len(username) < 3:
            return False, "Identifiant trop court (min 3)."
        if len(display_name) < 3:
            return False, "Pseudo trop court (min 3)."
        if len(password) < 6:
            return False, "Mot de passe trop court (min 6)."

        pw_hash = self.hash_password(password)

        # Utiliser un avatar par défaut si aucun n'est fourni
        if not avatar_path:
            avatar_path = 'assets/avatars/default.png'

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
            # on renvoie tout ce qui est utile au jeu
            return True, "Connexion réussie !", {
                "id": row["id"],
                "display_name": row["display_name"],
                "avatar_path": row["avatar_path"],
            }

        return False, "Mot de passe incorrect.", None



# ========================================
# INSTANCIATION GLOBALE
# ========================================
# Crée une instance globale de la base de données (utilisée dans toute l'application)
DB = Database()
