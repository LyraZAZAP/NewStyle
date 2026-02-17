# ========================================
# GESTIONNAIRE AUDIO / MUSIQUE
# Contrôle la lecture des musiques de fond
# ========================================

# === IMPORTS ===
import pygame as pg  # Pygame pour la gestion audio


# === CLASSE AUDIO MANAGER ===
class AudioManager:
    """Gère la lecture des musiques de fond du jeu."""
    
    def __init__(self, tracks, volume=0.6):
        """Initialise le gestionnaire avec une liste de pistes musical."""
        self.tracks = tracks[:]  # Copie la liste des fichiers de musique
        self.index = 0  # Index de la piste actuelle (commence par 0 = première piste)
        self.volume = volume  # Volume sonore (0.0 à 1.0)
        self.paused = False  # État pausé (False = en lecture)

        # Initialise le mixer pygame pour la musique (si non déjà initialisé)
        if not pg.mixer.get_init():
            pg.mixer.init()

        # Fixe le volume de la musique
        pg.mixer.music.set_volume(self.volume)

    def play(self, index=None):
        """Lance la lecture d'une piste (ou continue la piste actuelle)."""
        # Vérifie qu'il y a des pistes disponibles
        if not self.tracks:
            return
        
        # Si un index est fourni, on va à cette piste
        if index is not None:
            self.index = index % len(self.tracks)  # Modulo pour boucler si index > taille liste

        # Arrête la musique actuelle
        pg.mixer.music.stop()
        # Charge la piste sélectionnée
        pg.mixer.music.load(self.tracks[self.index])
        # Lance la lecture avec boucle infinie (-1)
        pg.mixer.music.play(-1)
        # Marque comme non pausé
        self.paused = False

    def next_track(self):
        """Passe à la piste suivante."""
        # Vérifie qu'il y a des pistes disponibles
        if not self.tracks:
            return
        
        # Passe à la piste suivante (ou revient à la première si c'était la dernière)
        self.index = (self.index + 1) % len(self.tracks)
        # Lance la lecture de la nouvelle piste
        self.play()

    def is_playing(self):
        """Retourne True si une musique est en cours de lecture."""
        # get_busy() = True si une musique joue actuellement
        # Vérifie aussi qu'on n'est pas en pause
        return pg.mixer.music.get_busy() and not self.paused

    def toggle_pause(self):
        """Bascule entre pause et lecture."""
        if self.paused:
            # Si on était en pause, on relance la lecture
            pg.mixer.music.unpause()
            self.paused = False
        else:
            # Si on jouait, on met en pause
            pg.mixer.music.pause()
            self.paused = True
