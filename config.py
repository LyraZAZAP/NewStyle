# Configuration globale du jeu

import sys
import os

WINDOW_WIDTH  = 1024
WINDOW_HEIGHT = 640
FPS           = 60

# game.db doit être dans le dossier du .exe (persistant entre les lancements).
# Quand PyInstaller change le CWD vers _internal/, ce chemin relatif ne fonctionnerait plus,
# donc on construit un chemin absolu vers le dossier de l'exécutable.
if getattr(sys, 'frozen', False):
    DB_PATH = os.path.join(os.path.dirname(sys.executable), 'data', 'game.db')
else:
    DB_PATH = "data/game.db"

TITLE            = "Jeu de Dressing"
BACKGROUND_COLOR = (240, 240, 245)

# Fonds d'écran
SIDEBAR_BG_PATH = "assets/backgrounds/sidebar_bg.png"
STAGE_BG_PATH   = "assets/backgrounds/stage_bg.png"
MENU_BG_PATH    = "assets/backgrounds/menu_bg.png"
RESULT_BG_PATH  = "assets/backgrounds/stage_bg.png"

# Widget disque musical
DISC_IMG_PATH = "assets/ui/disque.png"
DISC_BTN_PATH = "assets/ui/bouton.png"

MUSIC_TRACKS = [
    "assets/musics/I DO COKE.mp3",
    "assets/musics/I Like It Rough.mp3",
    "assets/musics/404 (New Era).mp3",
    "assets/musics/Tila Tsoli - Bimbo Doll (Lyrics).mp3",
]

TITLE_IMG_PATH = "assets/titles/title_menu.png"
