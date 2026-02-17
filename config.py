# ========================================
# CONFIGURATION DU JEU
# ========================================

# === DIMENSIONS DE LA FENÊTRE ===
WINDOW_WIDTH = 1024  # Largeur de la fenêtre en pixels
WINDOW_HEIGHT = 640  # Hauteur de la fenêtre en pixels

# === PERFORMANCE ===
FPS = 60  # Nombre d'images par seconde (60 FPS = 60 mises à jour par seconde)

# === BASE DE DONNÉES ===
DB_PATH = "data/game.db"  # Chemin vers le fichier de la base de données SQLite

# === TITRE ET COULEUR ===
TITLE = "Jeu de Dressing"  # Titre affiché dans la barre de la fenêtre
BACKGROUND_COLOR = (240, 240, 245)  # Couleur de fond par défaut (RGB : gris-bleu clair)

# === CHEMINS DES IMAGES DE FOND D'ÉCRAN ===
SIDEBAR_BG_PATH = "assets/backgrounds/sidebar_bg.png"  # Fond pour la zone de galerie (gauche)
STAGE_BG_PATH = "assets/backgrounds/stage_bg.png"  # Fond pour la zone mannequin (droite)
MENU_BG_PATH = "assets/backgrounds/menu_bg.png"  # Fond pour l'écran menu principal
RESULT_BG_PATH = "assets/backgrounds/stage_bg.png"  # Fond pour l'écran résultat

# === DISQUE MUSICAL (WIDGET UI) ===
DISC_IMG_PATH = "assets/ui/disque.png"  # Image du disque vinyl qui tourne
DISC_BTN_PATH = "assets/ui/bouton.png"  # Bouton au centre du disque (pour changer de musique)

# === LISTES DE MUSIQUES ===
# Chargement des fichiers musicaux depuis le dossier assets/musics/
MUSIC_TRACKS = [
    "assets/musics/I DO COKE.mp3",  # Musique 1
    "assets/musics/I Like It Rough.mp3",  # Musique 2
]

# === IMAGE DU TITRE ===
# Image affichée en haut du menu au lieu du texte
TITLE_IMG_PATH = "assets/titles/title_menu.png"
