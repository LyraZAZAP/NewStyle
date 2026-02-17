# 🎮 NewStyle - Jeu de Dressing

## Qu'est-ce que c'est ?
Un jeu Pygame où les joueurs **créent un compte**, **se connectent** et **habillent un mannequin** selon un thème pour obtenir un score.

---

## 📂 Comment est organisé le projet ?

### Structure simple
```
NewStyle/
├── main.py              ← LANCER LE JEU (point d'entrée)
├── config.py            ← Paramètres du jeu (taille écran, chemins, etc.)
│
├── db.py                ← Base de données (utilisateurs, vêtements)
├── models.py            ← Structures de données (Category, Garment, Mannequin)
├── repositories.py      ← Accès aux données de la BD
├── services.py          ← Logique métier (gestion tenue, scoring)
│
├── scenes/              ← Les différents écrans du jeu
│   ├── base_scene.py    ← Classe de base (modèle)
│   ├── login_scene.py   ← Écran connexion
│   ├── register_scene.py ← Écran inscription
│   ├── menu_scene.py    ← Écran menu principal
│   ├── dress_scene.py   ← Écran habillage (le principal !)
│   └── result_scene.py  ← Écran résultat/score
│
├── ui/                  ← Composants d'interface
│   ├── widgets.py       ← Boutons
│   └── music_disc.py    ← Disque musical tournant
│
├── audio_manager.py     ← Gestion de la musique
├── data/                ← Base de données
│   ├── schema.sql       ← Structure des tables
│   ├── seed_data.sql    ← Données initiales
│   └── game.db          ← Fichier BD (créé automatiquement)
│
└── assets/              ← Images, sprites, musiques
    ├── backgrounds/
    ├── mannequins/
    ├── clothes/
    ├── avatars/
    └── music/
```

---

## 🎯 Flux du jeu (ce qui se passe)

```
1. LANCEMENT
   Exécute main.py
   → Crée fenêtre Pygame
   → Affiche l'écran de login

2. AUTHENTIFICATION
   Utilisateur se connecte (DB.authenticate)
   OU crée un compte (DB.create_user)
   → Avatar + Pseudo s'affichent en haut-left

3. MENU (après connexion)
   Affiche avatar + pseudo
   Bouton "Nouvelle partie"
   → Choisit thème et mannequin aléatoires

4. HABILLAGE (CŒUR DU JEU)
   Gauche : Galerie de vêtements
   Droite : Mannequin à habiller
   → Glisse-dépose les vêtements
   → Les vêtements se superposent

5. RÉSULTAT
   Affiche le score obtenu
   → Retour au menu (boucle)
```

---

## 🔐 Base de données

### Table `users` (utilisateurs)
```
id          → Identifiant (1, 2, 3...)
username    → Identifiant connexion ("alice")
display_name → Pseudo affiché ("Alice Cool")
avatar_path → Chemin vers l'avatar
password_hash → Mot de passe chiffré (bcrypt)
created_at  → Date création
```

### Table `garment` (vêtements)
```
id          → Identifiant (1, 2, 3...)
name        → Nom du vêtement ("Red T-Shirt")
category_id → Catégorie (1=Top, 2=Bottom...)
sprite_path → Fichier image
score_theme → Thème bonus ("casual", "soiree"...)
```

---

## 🕹️ Comment jouer

1. **Lancer le jeu**
   ```bash
   py main.py
   ```

2. **Créer un compte (Inscription)**
   - Cliquer "Inscription"
   - Remplir : Identifiant, Pseudo, Mot de passe
   - Sélectionner un avatar (< Avatar, Avatar >)
   - Cliquer "Créer le compte"

3. **Menu principal**
   - Avatar + Pseudo affiché en haut-left
   - Bouton "Nouvelle partie"

4. **Habiller le mannequin**
   - Glisse des vêtements de la galerie vers le mannequin
   - Respecte l'ordre : Chaussures → Bas → Haut → Cheveux → Visage → Accessoires
   - Appuyer sur ENTRÉE pour valider

5. **Résultat**
   - Score = base (50) + bonus thème (15×) - pénalité (5×vêtements>4)
   - Argent = Score / 10 × 5
   - Appuyer R pour retour menu

---

## 🔑 Concepts clés

### Pattern Repository
Les fichiers `repositories.py` isolent l'accès à la base de données :
- `CategoryRepo.all()` → Toutes les catégories
- `GarmentRepo.by_category()` → Vêtements d'une catégorie
- `MannequinRepo.all()` → Tous les mannequins

### Sécurité des mots de passe
- Mots de passe chiffré avec **bcrypt**
- Jamais stocké en clair en base de données
- À la connexion : vérification avec `bcrypt.checkpw()`

### Scènes (Écrans)
Chaque écran = une classe qui hérite de `Scene` :
- `handle_event()` → Traite les clics/touches
- `update()` → Met à jour la logique
- `draw()` → Affiche à l'écran

### Systématique de calques (Dress Scene)
L'ordre de superposition des vêtements :
```
1. Chaussures (fond)
2. Bas
3. Haut
4. Cheveux
5. Visage
6. Accessoires (avant)
```

---

## 💾 Technologie

- **Python 3.11+**
- **Pygame 2.6** - Rendu graphique
- **SQLite3** - Base de données
- **bcrypt** - Chiffrement sécurisé

---

## 📖 Lire le code dans cet ordre

Pour comprendre le projet facilement :

1. **config.py** - Les paramètres
2. **models.py** - Les types de données
3. **db.py** - Connexion à la BD
4. **repositories.py** - Requêtes SQL
5. **services.py** - Calcul scores
6. **ui/widgets.py** - Boutons
7. **scenes/base_scene.py** - Modèle de scène
8. **scenes/login_scene.py** - Login
9. **scenes/register_scene.py** - Registration
10. **scenes/menu_scene.py** - Menu
11. **scenes/dress_scene.py** - Habillage (complexe !)
12. **scenes/result_scene.py** - Résultat
13. **main.py** - Orchestration
14. **audio_manager.py** - Musique
15. **ui/music_disc.py** - Widget disque

---

## ⚡ Raccourcis clavier

- **F11** ou **Alt+Enter** : Plein écran
- **TAB** : Passer au champ suivant (login/register)
- **ENTRÉE** : Valider (login/register/dress)
- **Molette souris** : Scroller la galerie
- **Clic droit** : Retirer un vêtement
- **R** : Retour au menu (résultat)

---

## 📝 Tous les fichiers Python sont commentés

✅ **Chaque ligne a son commentaire** pour expliquer :
- Les imports
- Les variables
- Les fonctions
- La logique

👉 Voir le fichier `STRUCTURE_COMMENTÉE.md` pour un guide détaillé !

---

**Bon jeu ! 🎮✨**
