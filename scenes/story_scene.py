import os  # importer le module pour vérifier l'existence de fichiers
import random  # importer random pour le tremblement d'écran
import pygame as pg  # importer pygame sous l'alias pg pour gérer l'affichage
from scenes.base_scene import Scene  # importer la classe de base des scènes

def _load_image(path, size=None, fallback_color=(220, 220, 240)):
    """Charge une image, la redimensionne si nécessaire et fournit un fallback."""
    if os.path.exists(path):  # si le fichier existe sur disque
        image = pg.image.load(path)  # charger l'image avec pygame
        image = image.convert_alpha() if image.get_alpha() is not None else image.convert()  # optimiser l'image pour le rendu
        if size is not None:  # si une taille cible est donnée
            image = pg.transform.smoothscale(image, size)  # redimensionner l'image
        return image  # retourner l'image chargée

    surf = pg.Surface(size if size is not None else (100, 100), pg.SRCALPHA)  # créer une surface vide si l'image est absente
    surf.fill(fallback_color)  # remplir la surface d'une couleur de repli
    return surf  # retourner la surface de secours


class StoryScene(Scene):  # définition de la scène visual novel
    """Scène simple qui affiche un fond, un personnage et une barre de texte."""

    def __init__(self, game, mannequin, theme):  # constructeur de la scène
        super().__init__(game)  # appeler le constructeur de Scene
        self.mannequin = mannequin  # stocker le mannequin sélectionné
        self.theme = theme  # stocker le thème choisi
        self.dialogue_index = 0  # index du dialogue affiché

        self.dialogues = [  # liste des lignes de dialogue
            f"Tu viens d'enter en école de styliste, après le bac ( de JUSTESSE )",  #ta propre pensée
            f"Une seule règle, soit stylé",  
            "En marchant vers ton école, tu vois beaucoup d'élèves, tous habillé de façon très orignaux.",  
            "Tu remarques, emo.. scene.. goth.. classic.. lolita.. etc etc"  
        ]

        self.background = _load_image("assets/backgrounds/school.png", (self.game.w, self.game.h), fallback_color=(180, 200, 240))  # charger le fond d'école
        self.bar_image = _load_image("assets/bar/bar_text_purple.png")  # charger l'image de la barre de texte à sa taille native
        self.bar_rect = self.bar_image.get_rect(midbottom=(self.game.w // 2, self.game.h - 5))  # positionner la barre au ras du bord bas
        self.text_area_rect = pg.Rect(self.bar_rect.left + 40, self.bar_rect.top + 80, self.bar_rect.width - 80, self.bar_rect.height - 95)  # zone de texte plus basse dans la barre
        self.juliette_image = _load_image("assets/characteres/juliette_mouth_closed.png", size=(int(self.game.h * 0.84), int(self.game.h * 0.84)))  # charger l'image de Juliette
        self.juliette_rect = self.juliette_image.get_rect(midbottom=(self.game.w // 2, self.game.h - 40))  # placer Juliette derrière la barre

        self.title_font = pg.font.SysFont(None, 42)  # police pour le titre
        self.text_font = pg.font.SysFont(None, 32)  # police pour le dialogue
        self.prompt_font = pg.font.SysFont(None, 24)  # police pour le prompt

        self.text_bar_height = self.bar_rect.height  # hauteur de la barre de texte calculée à partir de l'image
        self.text_bar_rect = pg.Rect(self.bar_rect.left, self.bar_rect.top, self.bar_rect.width, self.bar_rect.height)  # rectangle de la barre de dialogue
        self.juliette_visible = False  # Juliette n'apparaît que lorsque les textes sont finis
        self.shake_timer = 0.0  # minuterie de l'effet de tremblement
        self.shake_duration = 0.4  # durée du tremblement en secondes
        self.shake_intensity = 8  # intensité du tremblement en pixels

    def handle_event(self, event):  # gestion des événements
        """Avance le dialogue ou quitte la scène après le tremblement de Juliette."""
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:  # clic gauche
            if self.juliette_visible and self.shake_timer <= 0.0:  # si Juliette est visible et le tremblement fini
                self.game.goto_dress(self.mannequin, self.theme)  # aller à la scène d'habillage
            else:
                self._next_dialogue()  # sinon passer au dialogue suivant
        elif event.type == pg.KEYDOWN and event.key in (pg.K_RETURN, pg.K_SPACE):  # touche Entrée ou Espace
            if self.juliette_visible and self.shake_timer <= 0.0:
                self.game.goto_dress(self.mannequin, self.theme)
            else:
                self._next_dialogue()  # passer au dialogue suivant

    def update(self, dt):  # mise à jour par frame
        """Met à jour le tremblement de l'écran si Juliette vient d'apparaître."""
        if self.shake_timer > 0.0:  # réduire la minuterie de tremblement
            self.shake_timer = max(0.0, self.shake_timer - dt)

    def draw(self, screen):  # dessin de la scène
        """Dessine le fond, le personnage et la barre de dialogue."""
        screen.blit(self.background, (0, 0))  # afficher le fond à l'origine

        shake_x, shake_y = 0, 0
        if self.juliette_visible and self.shake_timer > 0.0:  # appliquer un petit tremblement lorsque Juliette arrive
            amplitude = int(self.shake_intensity * (self.shake_timer / self.shake_duration))
            shake_x = random.randint(-amplitude, amplitude)
            shake_y = random.randint(-amplitude, amplitude)

        # Dessine Juliette derrière la barre de texte si elle est visible.
        if self.juliette_visible:
            juliette_rect = self.juliette_rect.move(shake_x, shake_y)
            screen.blit(self.juliette_image, juliette_rect)  # afficher Juliette en arrière-plan de la barre

        # Affiche l'image de la barre de texte sous le texte.
        bar_rect = self.bar_rect.move(shake_x, shake_y)
        screen.blit(self.bar_image, bar_rect)  # dessiner la barre d'UI graphique

        title = self.title_font.render("toi", True, (255, 255, 255))  # rendre le titre de l'écran
        screen.blit(title, (bar_rect.left + 30, bar_rect.top + 18))  # dessiner le titre dans la barre

        message = self.dialogues[self.dialogue_index]  # récupérer la ligne de dialogue actuelle
        text = self.text_font.render(message, True, (245, 245, 245))  # rendre le texte du dialogue
        screen.blit(text, (bar_rect.left + 40, bar_rect.top + 80))  # afficher le dialogue plus bas dans la barre

        prompt = self.prompt_font.render("Cliquez ou appuyez sur Entrée pour continuer", True, (200, 200, 220))  # rendre le prompt d'action
        prompt_rect = prompt.get_rect()  # obtenir le rectangle du prompt
        prompt_rect.bottomright = (bar_rect.right - 20, bar_rect.bottom - 15)  # aligner le prompt dans la barre
        screen.blit(prompt, prompt_rect)  # dessiner le prompt

    def _next_dialogue(self):  # méthode interne pour avancer dans le dialogue
        """Avance le dialogue ou affiche Juliette quand le texte est terminé."""
        if self.juliette_visible:  # si Juliette est déjà visible, on attend un clic pour changer de scène
            return

        if self.dialogue_index < len(self.dialogues) - 1:  # si il reste encore des textes à afficher
            self.dialogue_index += 1  # passer à la ligne suivante
        else:
            self.juliette_visible = True  # afficher Juliette après le dernier texte
            self.shake_timer = self.shake_duration  # lancer le tremblement de l'écran
