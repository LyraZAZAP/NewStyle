# Gestion de la musique de fond

import pygame as pg


class AudioManager:
    """Lecture en boucle d'une liste de pistes musicales."""

    def __init__(self, tracks, volume=0.6):
        self.tracks = tracks[:]
        self.index  = 0
        self.volume = volume
        self.paused = False

        if not pg.mixer.get_init():
            pg.mixer.init()
        pg.mixer.music.set_volume(self.volume)

    def play(self, index=None):
        if not self.tracks:
            return
        if index is not None:
            self.index = index % len(self.tracks)
        pg.mixer.music.stop()
        pg.mixer.music.load(self.tracks[self.index])
        pg.mixer.music.play(-1)  # -1 = boucle infinie
        self.paused = False

    def next_track(self):
        if not self.tracks:
            return
        self.index = (self.index + 1) % len(self.tracks)
        self.play()

    def prev_track(self):
        if not self.tracks:
            return
        self.index = (self.index - 1) % len(self.tracks)
        self.play()

    def is_playing(self):
        return pg.mixer.music.get_busy() and not self.paused

    def toggle_pause(self):
        if self.paused:
            pg.mixer.music.unpause()
            self.paused = False
        else:
            pg.mixer.music.pause()
            self.paused = True
