INSERT OR IGNORE INTO category (name, max_items) VALUES -- Insère les catégories si elles n'existent pas
('top', 1), ('bottom', 1), ('shoes', 1), ('accessory', 4); -- catégories principales et nombre max d'éléments
('skin', 1), ('hair', 1) -- autres catégories (peuvent être pour peau/cheveux)


INSERT OR IGNORE INTO theme (code, label) VALUES -- Insère les thèmes de jeu si absents
('casual','Casual'), ('soiree','Soirée'), ('colorful','Colorful'), ('chic','Travail'); -- code et libellé du thème


INSERT OR IGNORE INTO mannequin (id, name, base_sprite_path) VALUES -- Insère des mannequins exemples
(1, 'Lina', 'assets/mannequins/mannequin_base.png'), -- mannequin id 1
(2, 'Noa', 'assets/mannequins/mannequin_base.png'); -- mannequin id 2


-- Exemples de vêtements (utilisent des placeholders rectangulaires dessinés par le code si le sprite manque)
INSERT OR IGNORE INTO garment (name, category_id, sprite_path, score_theme, price) -- Ajoute un vêtement si non présent
SELECT 'T-shirt Blanc', c.id, 'assets/clothes/tops/tshirt_white.png', 'casual', 10 FROM category c WHERE c.name='top'; -- T-shirt blanc pour 'top'
INSERT OR IGNORE INTO garment (name, category_id, sprite_path, score_theme, price) -- Autre vêtement
SELECT 'Chemise Noire', c.id, 'assets/clothes/tops/shirt_black.png', 'soiree', 20 FROM category c WHERE c.name='top'; -- Chemise noire pour soirées
INSERT OR IGNORE INTO garment (name, category_id, sprite_path, score_theme, price)
SELECT 'Jeans Bleu', c.id, 'assets/clothes/bottoms/jeans_blue.png', 'casual', 15 FROM category c WHERE c.name='bottom'; -- Jeans pour 'bottom'
INSERT OR IGNORE INTO garment (name, category_id, sprite_path, score_theme, price)
SELECT 'Jupe Rouge', c.id, 'assets/clothes/bottoms/skirt_red.png', 'soiree', 25 FROM category c WHERE c.name='bottom'; -- Jupe rouge pour soirées
INSERT OR IGNORE INTO garment (name, category_id, sprite_path, score_theme, price)
SELECT 'Baskets', c.id, 'assets/clothes/shoes/sneakers.png', 'sport', 10 FROM category c WHERE c.name='shoes'; -- Chaussures sport
INSERT OR IGNORE INTO garment (name, category_id, sprite_path, score_theme, price)
SELECT 'Talons', c.id, 'assets/clothes/shoes/heels.png', 'soiree', 30 FROM category c WHERE c.name='shoes'; -- Talons pour soirées
INSERT OR IGNORE INTO garment (name, category_id, sprite_path, score_theme, price)
SELECT 'Lunettes', c.id, 'assets/clothes/accessories/glasses.png', 'travail', 10 FROM category c WHERE c.name='accessory'; -- Accessoire lunettes
INSERT OR IGNORE INTO garment (name, category_id, sprite_path, score_theme, price)
SELECT 'Sac', c.id, 'assets/clothes/accessories/bag.png', 'soiree', 15 FROM category c WHERE c.name='accessory'; -- Accessoire sac