PRAGMA foreign_keys = ON; -- Active les contraintes de clés étrangères pour la base


CREATE TABLE IF NOT EXISTS category (  -- Table des catégories d'articles
id INTEGER PRIMARY KEY AUTOINCREMENT, -- Identifiant unique auto-incrémenté
name TEXT UNIQUE NOT NULL, -- Nom de la catégorie (doit être unique et non nul)
max_items INTEGER NOT NULL DEFAULT 1 -- Nombre max d'éléments sélectionnables par catégorie (par défaut 1)
); -- Fin de la table category


CREATE TABLE IF NOT EXISTS garment ( -- Table des vêtements/articles
id INTEGER PRIMARY KEY AUTOINCREMENT, -- Identifiant unique de l'article
name TEXT NOT NULL, -- Nom de l'article (non nul)
category_id INTEGER NOT NULL, -- Référence vers la catégorie (clé étrangère)
sprite_path TEXT NOT NULL, -- Chemin du fichier image/sprite pour l'article
score_theme TEXT DEFAULT NULL, -- Thème favori associé (ex: 'soirée','sport','casual','travail')
price INTEGER DEFAULT 0, -- Prix de l'article (par défaut 0)
FOREIGN KEY(category_id) REFERENCES category(id) ON DELETE CASCADE -- Contrainte FK: supprime l'article si la catégorie est supprimée
); -- Fin de la table garment


CREATE TABLE IF NOT EXISTS mannequin ( -- Table des mannequins
id INTEGER PRIMARY KEY AUTOINCREMENT, -- Identifiant unique du mannequin
name TEXT NOT NULL, -- Nom du mannequin (non nul)
base_sprite_path TEXT NOT NULL -- Chemin du sprite de base du mannequin
); -- Fin de la table mannequin


CREATE TABLE IF NOT EXISTS theme ( -- Table des thèmes
id INTEGER PRIMARY KEY AUTOINCREMENT, -- Identifiant unique du thème
code TEXT UNIQUE NOT NULL, -- Code du thème (ex: 'casual','soirée','sport','travail'), unique
label TEXT NOT NULL -- Libellé lisible du thème
); -- Fin de la table theme


CREATE TABLE IF NOT EXISTS run_result ( -- Table des résultats d'une session/partie
id INTEGER PRIMARY KEY AUTOINCREMENT, -- Identifiant unique du résultat
mannequin_id INTEGER NOT NULL, -- Référence au mannequin utilisé
theme_id INTEGER NOT NULL, -- Référence au thème évalué
score INTEGER NOT NULL, -- Score obtenu
money_earned INTEGER NOT NULL, -- Argent gagné durant la session
created_at TEXT DEFAULT (datetime('now')), -- Timestamp de création (valeur par défaut: maintenant)
FOREIGN KEY(mannequin_id) REFERENCES mannequin(id), -- FK vers mannequin
FOREIGN KEY(theme_id) REFERENCES theme(id) -- FK vers theme
); -- Fin de la table run_result