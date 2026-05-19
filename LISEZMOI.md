# NewStyle - Jeu de Dressing

Jeu Pygame où les joueurs **créent un compte**, **se connectent** et **habillent un mannequin** selon un thème pour obtenir un score.

---

## Lancer le jeu

### Sur n'importe quelle machine (sans Python ni git)

**1 — Construire l'exe (une seule fois sur ta machine) :**
```
Double-cliquer sur build_exe.bat
```

**2 — Copier et lancer :**
Copier le dossier `dist\NewStyle\` sur la machine cible et lancer `NewStyle.exe`.

### Sur une machine avec Python

```
Double-cliquer sur run.bat
```
Le script crée le `.venv` et installe les dépendances automatiquement si besoin.

---

## Structure du projet

```
NewStyle/
├── main.py               ← LANCER LE JEU (point d'entrée)
├── config.py             ← Paramètres du jeu (taille écran, chemins, etc.)
│
├── db.py                 ← Base de données (utilisateurs, vêtements)
├── models.py             ← Structures de données (Category, Garment, Mannequin)
├── repositories.py       ← Accès aux données de la BD
├── services.py           ← Logique métier (gestion tenue, scoring)
│
├── scenes/               ← Les différents écrans du jeu
│   ├── base_scene.py     ← Classe de base (modèle)
│   ├── login_scene.py    ← Écran connexion
│   ├── register_scene.py ← Écran inscription
│   ├── story_scene.py    ← Visual novel d'introduction
│   ├── menu_scene.py     ← Écran menu principal
│   ├── dress_scene.py    ← Écran habillage (le principal !)
│   └── result_scene.py   ← Écran résultat/score
│
├── ui/                   ← Composants d'interface
│   ├── widgets.py        ← Boutons
│   ├── theme.py          ← Couleurs et styles
│   └── music_disc.py     ← Disque musical tournant
│
├── audio_manager.py      ← Gestion de la musique
├── data/                 ← Base de données
│   ├── schema.sql        ← Structure des tables
│   ├── seed_data.sql     ← Données initiales
│   └── game.db           ← Fichier BD (créé automatiquement)
│
├── assets/               ← Images, sprites, musiques
│   ├── backgrounds/
│   ├── mannequins/
│   ├── clothes/
│   ├── avatars/
│   ├── titles/
│   ├── ui/
│   └── musics/
│
├── run.bat               ← Lance le jeu (auto-installe si besoin)
└── build_exe.bat         ← Construit l'executable portable
```

---

## Flux du jeu

```
1. LANCEMENT          → Fenêtre Pygame + écran de login
2. AUTHENTIFICATION   → Connexion ou création de compte
3. VISUAL NOVEL       → Introduction narrative
4. MENU               → "Nouvelle partie" choisit thème + mannequin aléatoires
5. HABILLAGE          → Glisse-dépose des vêtements sur le mannequin
6. RÉSULTAT           → Score, argent gagné, retour au menu
```

---

## Base de données

### Table `users` (utilisateurs)
```
id            → Identifiant unique
username      → Identifiant de connexion ("alice")
display_name  → Pseudo affiché ("Alice Cool")
avatar_path   → Chemin vers l'avatar
password_hash → Mot de passe chiffré (bcrypt)
created_at    → Date de création
```

### Table `garments` (vêtements)
```
id          → Identifiant unique
name        → Nom du vêtement ("Red T-Shirt")
category_id → Catégorie (1=Top, 2=Bottom...)
sprite_path → Fichier image
theme_tags  → Thème bonus ("casual", "soiree"...)
base_score  → Points de base
```

---

## Comment jouer

1. **Créer un compte** — Identifiant, Pseudo, Mot de passe, Avatar
2. **Menu principal** — Bouton "Nouvelle partie"
3. **Habiller le mannequin** — Glisse des vêtements sur le mannequin
4. **Valider** — Appuyer sur ENTRÉE

### Raccourcis clavier
| Touche | Action |
|---|---|
| Molette | Défiler la galerie |
| Clic droit | Retirer un vêtement |
| Entrée | Valider la tenue |
| R | Retour au menu (résultat) |
| F11 / Alt+Entrée | Plein écran |
| TAB | Champ suivant (login/inscription) |

### Ordre des calques
```
1. Chaussures (fond)
2. Bas
3. Haut
4. Cheveux
5. Visage
6. Accessoires (avant)
```

### Calcul du score
```
Score  = points_de_base + bonus_thème - pénalité
Argent = Score / 10 × 5
```

---

## Concepts clés

### Pattern Repository
`repositories.py` isole l'accès à la base de données :
- `CategoryRepo.all()` — Toutes les catégories
- `GarmentRepo.by_category(id)` — Vêtements d'une catégorie
- `MannequinRepo.all()` — Tous les mannequins

### Sécurité des mots de passe
Mots de passe hachés avec **bcrypt** — jamais stockés en clair.

### Scènes (Écrans)
Chaque écran hérite de `BaseScene` :
- `handle_event()` — Traite les clics/touches
- `update()` — Met à jour la logique
- `draw()` — Affiche à l'écran

---

## Technologies

- **Python 3.11+**
- **Pygame 2.5+** — Rendu graphique
- **SQLite3** — Base de données locale
- **bcrypt** — Chiffrement sécurisé

---

## Lire le code dans cet ordre

1. `config.py` — Les paramètres
2. `models.py` — Les types de données
3. `db.py` — Connexion à la BD
4. `repositories.py` — Requêtes SQL
5. `services.py` — Calcul des scores
6. `ui/widgets.py` — Boutons
7. `scenes/base_scene.py` — Modèle de scène
8. `scenes/login_scene.py` → `register_scene.py` → `menu_scene.py`
9. `scenes/dress_scene.py` — Habillage (le plus complexe !)
10. `scenes/result_scene.py` — Résultat
11. `main.py` — Orchestration
12. `audio_manager.py` + `ui/music_disc.py` — Musique
