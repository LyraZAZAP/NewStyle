PRAGMA foreign_keys = ON; -- Active la gestion des clés étrangères dans SQLite (sinon elles ne sont pas appliquées)

CREATE TABLE IF NOT EXISTS category ( -- Crée la table "category" si elle n'existe pas déjà
  id INTEGER PRIMARY KEY AUTOINCREMENT,-- Colonne "id" : entier, clé primaire, valeur auto-incrémentée
  name TEXT UNIQUE NOT NULL,-- Colonne "name" : texte, obligatoire, et doit être unique (pas deux catégories avec le même nom)
  max_items INTEGER NOT NULL DEFAULT 1-- Colonne "max_items" : entier, obligatoire, valeur par défaut = 1 (nombre max d’objets dans cette catégorie)

);-- Fin de la définition de la table "category"

CREATE TABLE IF NOT EXISTS garment (-- Crée la table "garment" (vêtements) si elle n'existe pas d
  id INTEGER PRIMARY KEY AUTOINCREMENT,-- Colonne "id" : entier, clé primaire, auto-incrémentée
  name TEXT NOT NULL,-- Colonne "name" : nom du vêtement, texte obligatoire
  category_id INTEGER NOT NULL,-- Colonne "category_id" : référence à la catégorie, entier obligatoire
  sprite_path TEXT NOT NULL,-- Colonne "sprite_path" : chemin de l’image/du sprite du vêtement, texte obligatoire
  score_theme TEXT DEFAULT NULL,-- Colonne "score_theme" : thème de score associé (optionnel, peut être NULL)
  price INTEGER DEFAULT 0,-- Colonne "price" : prix du vêtement, entier, par défaut 0
  FOREIGN KEY(category_id) REFERENCES category(id) ON DELETE CASCADE-- Déclare "category_id" comme clé étrangère vers "category(id)" :
);-- si une catégorie est supprimée, tous les vêtements de cette catégorie sont aussi supprimés (CASCADE)
-- Fin de la définition de la table "garment"

CREATE TABLE IF NOT EXISTS mannequin (-- Crée la table "mannequin" si elle n'existe pas déjà
  id INTEGER PRIMARY KEY AUTOINCREMENT,-- Colonne "id" : entier, clé primaire, auto-incrémentée
  name TEXT NOT NULL,-- Colonne "name" : nom du mannequin, texte obligatoire
  base_sprite_path TEXT NOT NULL --Colonne "base_sprite_path" : chemin de l’image de base du mannequin, texte obligatoire
);-- Fin de la définition de la table "mannequin"

CREATE TABLE IF NOT EXISTS theme (-- Crée la table "theme" si elle n'existe pas déjà
  id INTEGER PRIMARY KEY AUTOINCREMENT,-- Colonne "id" : entier, clé primaire, auto-incrémentée
  code TEXT UNIQUE NOT NULL,-- Colonne "code" : code du thème, texte, obligatoire et unique (identifiant technique)
  label TEXT NOT NULL-- Colonne "label" : libellé du thème (nom lisible), texte obligatoire
);

CREATE TABLE IF NOT EXISTS run_result (-- Crée la table "run_result" pour stocker le résultat d’une run / partie si elle n'existe pas déjà
  id INTEGER PRIMARY KEY AUTOINCREMENT,-- Colonne "id" : entier, clé primaire, auto-incrémentée
  mannequin_id INTEGER NOT NULL,-- Colonne "mannequin_id" : référence au mannequin utilisé, entier obligatoire
  theme_id INTEGER NOT NULL,-- Colonne "theme_id" : référence au thème, entier obligatoire
  score INTEGER NOT NULL,-- Colonne "score" : score obtenu, entier obligatoire
  money_earned INTEGER NOT NULL,-- Colonne "money_earned" : argent gagné pendant cette run, entier obligatoire
  created_at TEXT DEFAULT (datetime('now')),-- Colonne "created_at" : date/heure de création, texte, par défaut = date/heure actuelle (datetime('now') dans SQLite)

  FOREIGN KEY(mannequin_id) REFERENCES mannequin(id),-- Déclare "mannequin_id" comme clé étrangère vers "mannequin(id)"
  FOREIGN KEY(theme_id) REFERENCES theme(id)-- Déclare "theme_id" comme clé étrangère vers "theme(id)"
);-- Fin de la définition de la table "run_result"

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    display_name TEXT NOT NULL,
    avatar_path TEXT NOT NULL DEFAULT 'assets/avatars/default.png',
    password_hash BLOB NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
