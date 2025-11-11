import sqlite3  # bibliothèque SQLite intégrée
from pathlib import Path  # utilitaire pour manipuler les chemins


from config import DB_PATH  # chemin par défaut de la base défini dans config.py


SCHEMA = Path('data/schema.sql')  # chemin vers le fichier de schéma SQL
SEED = Path('data/seed_data.sql')  # chemin vers le fichier de données initiales


class Database:  # Classe pour gérer l'initialisation et la connexion à la DB
    def __init__(self, path: str = DB_PATH):  # Constructeur : path optionnel vers la DB en cas de besoin/problème
        self.path = path  # Stocke le chemin de la base
        Path('data').mkdir(exist_ok=True)  # Crée le dossier data si nécessaire ( mkdir = commande en linux pour generer le dossier )
        self._init_db()  # Initialise la base (schéma + seed si première exécution)


    def _init_db(self):
        # Toujours appliquer le schéma puis le seed (INSERT OR IGNORE rend l'opération idempotente)
        with sqlite3.connect(self.path) as con:
            con.executescript(SCHEMA.read_text(encoding='utf-8'))
            con.executescript(SEED.read_text(encoding='utf-8'))


    def connect(self):
        con = sqlite3.connect(self.path)
        con.row_factory = sqlite3.Row
        return con


DB = Database()  # Instanciation globale (singleton simple) de la base