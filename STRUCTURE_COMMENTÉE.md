# 📚 STRUCTURE COMPLÈTE DU JEU - GUIDE DE LECTURE

## Vue d'ensemble
Ce jeu Pygame est un **jeu de dressing interactif** où le joueur crée un compte, se connecte et habille un mannequin sur un thème.

---

## 📂 ORGANISATION DES FICHIERS

### 🔧 Fichiers de Configuration
#### **config.py**
- **Rôle** : Centralise tous les paramètres du jeu
- **WINDOW_WIDTH/HEIGHT** : Dimensions de la fenêtre (1024 × 640)
- **FPS** : Vitesse du jeu (60 images/seconde)
- **DB_PATH** : Chemin de la base de données ("data/game.db")
- **Chemins images** : Fonds d'écran, disque musical, musiques

---

### 🗄️ BASE DE DONNÉES

#### **db.py** - Classe Database
**Responsabilité** : Gérer toute communication avec la base de données SQLite

**Principales méthodes** :
```
create_user(username, display_name, password, avatar_path)
  → Crée un nouvel utilisateur dans la table "users"
  → Hash le mot de passe avec bcrypt (sécurité)
  → Retourne (ok, message)

authenticate(username, password)
  → Cherche l'utilisateur par username
  → Vérifie le mot de passe avec bcrypt
  → Retourne (ok, message, user_dict)

hash_password(password)
  → Convertit un mot de passe en hash sécurisé

verify_password(password, password_hash)
  → Vérifie si un mot de passe correspond à son hash
```

**Table users** (base de données) :
```
id                  → Identifiant unique
username            → Nom de connexion (ex: "alice")
display_name        → Pseudo affiché (ex: "Alice Cool")
avatar_path         → Chemin vers l'image de l'avatar
password_hash       → Mot de passe chiffré
created_at          → Date de création du compte
```

#### **repositories.py** - Accès aux données métier
**Rôle** : Repository Pattern (isoler l'accès à la base de données)

```
CategoryRepo.all()           → Récupère toutes les catégories (Top, Bottom, Shoes...)
CategoryRepo.by_name(name)   → Cherche une catégorie par nom

GarmentRepo.all()            → Tous les vêtements
GarmentRepo.by_category()    → Vêtements d'une catégorie

MannequinRepo.all()          → Tous les mannequins
```

---

### 📊 Modèles de données

#### **models.py** - Dataclasses
Structures de données simples (objets qui représentent les données)

```
Category
├─ id: int                → Identifiant unique
├─ name: str             → Nom (ex: "Top")
└─ max_items: int        → Nombre max (ex: 1 pour "Top")

Garment
├─ id: int               → Identifiant unique
├─ name: str             → Nom du vêtement (ex: "Red T-Shirt")
├─ category_id: int      → Catégorie (lien vers Category)
├─ sprite_path: str      → Chemin vers l'image
├─ score_theme: str      → Thème bonus (ex: "casual")
└─ price: int            → Prix (non utilisé)

Mannequin
├─ id: int               → Identifiant unique
├─ name: str             → Nom (ex: "Lina")
└─ base_sprite_path: str → Chemin vers l'image de base
```

---

### 🎮 Logique Métier

#### **services.py**

**Classe Outfit** (Gestion de la tenue)
```
Représente la tenue actuelle du mannequin

can_add(garment)        → Peut-on ajouter ce vêtement ? 
                        → Vérifie les limites par catégorie

add(garment)            → Ajoute un vêtement à la tenue
remove(garment)         → Retire un vêtement
all_items()             → Récupère tous les vêtements portés
```

**Classe Scoring** (Calcul du score)
```
score(theme_code, garments)  → Calcule le score
├─ Score de base      : +50 points
├─ Bonus thème        : +15 points par vêtement correspondant
├─ Pénalité surcharge : -5 points par vêtement au-délà de 4
└─ Résultat           : score total (minimum 0)
```

---

### 🎨 Interface Utilisateur

#### **ui/widgets.py** - Button
```
Classe Button : Bouton cliquable simple
├─ rect           : Rectangle de positionnement
├─ text           : Texte du bouton
├─ on_click       : Fonction appelée au clic
└─ draw(screen)   : Dessine le bouton
```

#### **ui/music_disc.py** - MusicDiscWidget
```
Widget affichant un disque vinyl tournant
├─ disc_base      : Image du disque
├─ btn_surf       : Bouton au centre
├─ angle          : Angle de rotation actuel
├─ update(dt)     : Fait tourner le disque
└─ draw(screen)   : Dessine le disque + bouton
```

#### **audio_manager.py** - AudioManager
```
Gère la lecture des musiques de fond
├─ tracks         : Liste des fichiers musicaux
├─ index          : Piste actuelle
├─ play()         : Lance la lecture
├─ next_track()   : Piste suivante
└─ toggle_pause() : Pause/Lecture
```

---

### 🎪 Scènes (Écrans du jeu)

#### **scenes/base_scene.py** - Scene (classe de base)
```
Classe abstraite (modèle) pour toutes les scènes

handle_event(event)  → Traite les clics souris, touches clavier
update(dt)           → Met à jour la logique (appelé 60 fois/sec)
draw(screen)         → Dessine à l'écran (appelé 60 fois/sec)
```

#### **scenes/login_scene.py** - Écran de connexion
```
Permet à l'utilisateur de se connecter

Éléments :
├─ Champs texte : username, password
├─ Boutons : Connexion, Inscription, Retour menu
└─ Background : assets/backgrounds/login.png

Logique :
└─ Au clic "Connexion" → DB.authenticate()
                      → Si OK → Affiche avatar + pseudo
                      → Navigue vers le menu
```

#### **scenes/register_scene.py** - Écran de création de compte
```
Permet au joueur de créer un compte

Éléments :
├─ Champs : username, display_name, password
├─ Sélection d'avatar : Parcourir assets/avatars/
├─ Boutons : < Avatar, Avatar >, Créer le compte, Retour
└─ Background : assets/backgrounds/register.png

Logique :
└─ Au clic "Créer le compte" → DB.create_user()
                              → Si OK → DB.authenticate() automatiquement
                              → Affiche avatar + pseudo
                              → Navigue vers le menu
```

#### **scenes/menu_scene.py** - Menu principal
```
Écran d'accueil après connexion

Éléments :
├─ Titre : "Style Dress"
├─ Badge utilisateur : Avatar (64×64) + Pseudo
├─ Disque musical : MusicDiscWidget (coin en haut à droite)
├─ Bouton : "Nouvelle partie"
├─ Bouton : "Plein écran" / "Fenêtré"
└─ Background : assets/backgrounds/menu_bg.png
              + Effet parallaxe (bouge avec la souris)

Logique :
└─ Au clic "Nouvelle partie" → Choisit thème et mannequin aléatoires
                              → Navigue vers DressScene
```

#### **scenes/dress_scene.py** - Écran d'habillage (PRINCIPAL)
```
Écran où le joueur habille le mannequin

Zones :
├─ SIDEBAR (gauche, 320 pixels)
│  └─ Galerie de vêtements avec scrollbar
│     ├─ Affichage par catégorie (Top, Bottom, Shoes, etc.)
│     ├─ Vignettes redimensionnables (280×280)
│     └─ Drag & drop des vêtements
│
└─ STAGE (droite, 704 pixels)
   └─ Mannequin habillé
      ├─ Mannequin de base (360×520)
      ├─ Vêtements superposés par calques
      └─ Ordre de calques : Shoes → Bottom → Top → Hair → Face → Accessories

Logique :
├─ Molette souris     → Scroll galerie
├─ Glisser-déposer    → Ajouter vêtement
├─ Clic droit         → Retirer vêtement
├─ Remplacement auto  → Si catégorie pleine, remplace l'ancien
└─ Entrée             → Valide tenue → Navigue vers ResultScene
```

**Classe Draggable** (Objet glissable dans la galerie)
```
Représente un vêtement qu'on peut glisser
├─ garment      : L'objet Garment
├─ thumb        : Vignette originale (galerie)
├─ stage_image  : Image redimensionnée si portée (360×520)
├─ pos          : Position actuelle
└─ grab         : True si l'utilisateur le tient
```

#### **scenes/result_scene.py** - Écran de résultat
```
Affiche le score après validation de la tenue

Zones :
├─ PANNEAU GAUCHE
│  ├─ Titre + thème
│  ├─ Score obtenu
│  ├─ Argent gagné (score/10 × 5)
│  └─ Instruction : "R = Retour menu"
│
└─ PANNEAU DROIT
   └─ Mannequin habillé (aperçu final)

Logique :
├─ Appel Scoring.score() → Calcule le score
├─ Argent gagné = score / 10 * 5
└─ Touche R             → Retour au menu (loop)
```

---

### 💻 Fichier Principal

#### **main.py** - Game (Classe principale du jeu)
```
Gère la boucle principale, les événements globaux et la navigation

Attributs :
├─ screen        : Surface pygame (l'écran)
├─ clock         : Horloge pygame (60 FPS)
├─ scene         : Scène actuelle (login, menu, dress, etc.)
├─ current_user_id       : ID de l'utilisateur connecté
├─ current_username      : Pseudo de l'utilisateur
├─ current_avatar        : Chemin vers avatar
└─ audio        : Gestionnaire audio (musiques)

Méthodes principales :
├─ set_scene(name)           → Navigue vers une scène
├─ goto_login/menu/dress/result()  → Alias pour set_scene()
├─ toggle_fullscreen()       → Bascule fenêtre/plein écran
├─ cleanup()                 → Ferme DB avant quitter
└─ run()                     → Boucle principale du jeu
                            ├─ Gère les événements (60×/sec)
                            ├─ Appelle scene.update(dt)
                            ├─ Appelle scene.draw(screen)
                            ├─ Affiche avatar + pseudo (top-left)
                            └─ Bascule écran avec F11 ou Alt+Enter
```

---

### 📊 Structure de la base de données

```
data/
├─ schema.sql     : Création des tables (exécuté une fois)
├─ seed_data.sql  : Données initiales (catégories, mannequins, vêtements)
└─ game.db        : Fichier SQLite (créé automatiquement)

Tables dans game.db :
├─ category       : Catégories de vêtements
├─ garment        : Vêtements avec images et scores
├─ mannequin      : Mannequins disponibles
├─ theme          : Thèmes (casual, soiree, etc.)
├─ run_result     : Historique des parties (scores)
└─ users          : Utilisateurs (connexion/inscription)
```

---

## 🔄 Flux d'exécution (Vue d'ensemble)

```
1. LANCEMENT
   └─ main.py :: Game().run()
      └─ db.py :: DB.init() → Crée/charge la base de données
      └─ set_scene("login") → Affiche LoginScene

2. AUTHENTIFICATION
   ├─ LoginScene : Utilisateur tape identifiant + mot de passe
   │  └─ Clique "Connexion" → DB.authenticate()
   │     ├─ DB cherche utilisateur dans table users
   │     ├─ Vérifie mot de passe avec bcrypt
   │     └─ Retourne id, display_name, avatar_path
   │
   └─ RegisterScene : Nouvel utilisateur → DB.create_user()
      └─ Hash le mot de passe
      └─ Insère dans table users
      └─ Auto-authentifie

3. MENU
   └─ MenuScene : Affiche avatar + pseudo
      ├─ Disque musical tourne (ui/music_disc.py)
      ├─ Bouton "Nouvelle partie" → Choisit thème/mannequin aléatoires
      └─ Clique → Navigue vers DressScene

4. HABILLAGE (CŒUR DU JEU)
   └─ DressScene
      ├─ Chargement des vêtements → repositories.all()
      │  └─ DB.connect() → SELECT * FROM garment
      ├─ Galerie de vêtements à gauche
      ├─ Mannequin à droite
      ├─ Glisser-déposer des vêtements
      ├─ Outfit.add() / remove()  → Gère la tenue
      ├─ Molette pour scroller
      └─ Entrée → Valide
         └─ Navigue vers ResultScene

5. RÉSULTAT
   └─ ResultScene
      ├─ Affiche mannequin habillé
      ├─ Appel Scoring.score()
      │  └─ Calcule : base + bonus thème - pénalité
      ├─ Montre score et argent gagné
      └─ Touche R → Retour au menu (boucle)

6. FERMETURE
   └─ main.py :: Game.cleanup()
      ├─ DB.close() → Fermeture connexion DB
      └─ Supprime data/game.db (optionnel)
```

---

## 📝 Points clés à comprendre

### Commerce de données (Base de données ↔ Code)
```
Inscription :
   RegisterScene
   └─ Utilisateur tape données
      └─ DB.create_user()
         └─ Stocke dans users table

Connexion :
   LoginScene
   └─ Utilisateur tape identifiant + mot de passe
      └─ DB.authenticate()
         └─ Cherche dans users table
         └─ Retourne données utilisateur

Habillage :
   DressScene
   └─ Affiche galerie
      └─ GarmentRepo.all()
         └─ SELECT * FROM garment (BD)
         └─ Mappe dans dataclasses Garment
         └─ Affiche sur écran
```

### Sécurité (Mots de passe)
```
Inscription :
   Mot de passe en clair typé par utilisateur
   → hash_password() avec bcrypt
   → hash stocké en base (jamais le mot de passe clair)

Connexion :
   Mot de passe en clair typé par utilisateur
   → verify_password() compare avec hash en base
   → Retourne True/False
```

### Affichage et architecture
```
1. Boucle principale (main.py)
   - Appelle scene.update(dt)     → Mise à jour logique
   - Appelle scene.draw(screen)   → Affichage

2. Chaque scène sait se dessiner
   - LoginScene :: draw()  → Affiche champs + boutons
   - MenuScene :: draw()   → Affiche titre + badge + disque
   - DressScene :: draw()  → Affiche sidebar + mannequin + vêtements
   - ResultScene :: draw() → Affiche score + mannequin final

3. Pattern MVC léger
   - Models (models.py)       → Données (Category, Garment, Mannequin)
   - Repositories (repositories.py) → Accès BD
   - Services (services.py)   → Logique métier (Outfit, Scoring)
   - Views (scenes/)          → Affichage (chaque scène)
   - Controllers (main.py)    → Navigation
```

---

## 🚀 Comment tester

### 1. Lancer le jeu
```bash
py main.py
```

### 2. Créer un compte (Inscription)
- Cliquer "Inscription"
- Remplir :
  - Identifiant : "alice" (doit être unique)
  - Pseudo affichage : "Alice Cool"
  - Mot de passe : "password123"
  - Sélectionner avatar (< Avatar, Avatar >)
- Cliquer "Créer le compte"
- → Avatar + pseudo s'affichent top-left

### 3. Accéder au menu
- Compte créé, auto-connexion
- Avatar + pseudo visible en haut-left
- Disque musical tourne en haut-right

### 4. Nouvelle partie
- Cliquer "Nouvelle partie"
- Thème aléatoire (Casual, Soirée, etc.)
- Mannequin aléatoire

### 5. Habiller
- Galerie à gauche
- Glisser des vêtements vers le mannequin
- Respecto l'ordre des calques : Shoes → Bottom → Top → Hair → Face → Accessories
- Entrée pour valider

### 6. Résultat
- Affiche score + argent
- R pour retour menu (boucler)

---

## 📌 Fichiers importants à comprendre

**LIRE EN CETE ORDRE** :
1. **config.py** - Les paramètres
2. **models.py** - Les structures de données
3. **db.py** - Connexion à la BD + utilisateurs
4. **repositories.py** - Récupérer les données de jeu
5. **services.py** - Logique de tenue et score
6. **ui/*.py** - Petits widgets
7. **scenes/base_scene.py** - Modèle des scènes
8. **scenes/login_scene.py** - Authentification
9. **scenes/menu_scene.py** - Accueil
10. **scenes/dress_scene.py** - Habillage (complexe)
11. **scenes/result_scene.py** - Résultat
12. **main.py** - Orchestration globale
13. **audio_manager.py** - Musiques

---

**Chaque fichier Python a maintenant des commentaires clairs et simples sur chaque ligne ! 🎉**
