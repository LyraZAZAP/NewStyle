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

    def create_user(self, username: str, password: str):
        """Crée un nouvel utilisateur dans la base de données.
        
        Args:
            username (str): Le nom d'utilisateur
            password (str): Le mot de passe en clair
            
        Returns:
            tuple: (succès: bool, message: str)
        """
        # Supprime les espaces au début et à la fin du pseudo
        username = username.strip()

        # Valide la longueur du pseudo
        if len(username) < 3:
            return False, "Pseudo trop court (min 3)."
        # Valide la longueur du mot de passe
        if len(password) < 6:
            return False, "Mot de passe trop court (min 6)."

        # Hache le mot de passe de manière sécurisée
        pw_hash = self.hash_password(password)

        try:
            # Crée une connexion et insère le nouvel utilisateur
            with sqlite3.connect(self.path) as con:
                con.execute(
                    "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                    (username, pw_hash)
                )
                # Valide la transaction (enregistre les changements)
                con.commit()
            return True, "Compte créé !"
        except sqlite3.IntegrityError:
            # Erreur si le pseudo existe déjà (contrainte unique)
            return False, "Ce pseudo est déjà utilisé."
        except Exception as e:
            # Capture toute autre erreur de base de données
            return False, f"Erreur DB: {e}"

    def authenticate(self, username: str, password: str):
        """Authentifie un utilisateur avec ses identifiants.
        
        Args:
            username (str): Le nom d'utilisateur
            password (str): Le mot de passe en clair
            
        Returns:
            tuple: (succès: bool, message: str, user_id: int ou None)
        """
        # Supprime les espaces au début et à la fin du pseudo
        username = username.strip()

        # Recherche l'utilisateur dans la base de données
        with sqlite3.connect(self.path) as con:
            # Configure le factory pour accéder aux colonnes par nom
            con.row_factory = sqlite3.Row
            # Récupère l'ID et le hash du mot de passe de l'utilisateur
            row = con.execute(
                "SELECT id, password_hash FROM users WHERE username = ?",
                (username,)
            ).fetchone()

        # Si l'utilisateur n'existe pas
        if row is None:
            return False, "Utilisateur introuvable.", None

        # Vérifie si le mot de passe est correct
        if self.verify_password(password, row["password_hash"]):
            return True, "Connexion réussie !", row["id"]

        # Si le mot de passe est incorrect
        return False, "Mot de passe incorrect.", None


# ========================================
# INSTANCIATION GLOBALE
# ========================================
# Crée une instance globale de la base de données (utilisée dans toute l'application)
DB = Database()
