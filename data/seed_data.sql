-- Catégories
INSERT OR IGNORE INTO category (name, max_items) VALUES ('top', 1);
INSERT OR IGNORE INTO category (name, max_items) VALUES ('bottom', 1);
INSERT OR IGNORE INTO category (name, max_items) VALUES ('shoes', 1);
INSERT OR IGNORE INTO category (name, max_items) VALUES ('accessory', 4);

-- Thèmes
INSERT OR IGNORE INTO theme (code, label) VALUES ('casual','Casual');
INSERT OR IGNORE INTO theme (code, label) VALUES ('soiree','Soirée');
INSERT OR IGNORE INTO theme (code, label) VALUES ('sport','Sport');
INSERT OR IGNORE INTO theme (code, label) VALUES ('travail','Travail');

-- Mannequins
INSERT OR IGNORE INTO mannequin (id, name, base_sprite_path) VALUES (1, 'Lina', 'assets/mannequins/mannequin_base.png');
INSERT OR IGNORE INTO mannequin (id, name, base_sprite_path) VALUES (2, 'Noa', 'assets/mannequins/mannequin_base.png');

-- Vêtements (référencent les catégories par sous-requête)
INSERT OR IGNORE INTO garment (name, category_id, sprite_path, score_theme, price)
VALUES ('T-shirt Blanc', (SELECT id FROM category WHERE name='top'), 'assets/clothes/tops/tshirt_white.png', 'casual', 10);

INSERT OR IGNORE INTO garment (name, category_id, sprite_path, score_theme, price)
VALUES ('Chemise Noire', (SELECT id FROM category WHERE name='top'), 'assets/clothes/tops/shirt_black.png', 'soiree', 20);

INSERT OR IGNORE INTO garment (name, category_id, sprite_path, score_theme, price)
VALUES ('Jeans Bleu', (SELECT id FROM category WHERE name='bottom'), 'assets/clothes/bottoms/jeans_blue.png', 'casual', 15);

INSERT OR IGNORE INTO garment (name, category_id, sprite_path, score_theme, price)
VALUES ('Jupe Rouge', (SELECT id FROM category WHERE name='bottom'), 'assets/clothes/bottoms/skirt_red.png', 'soiree', 25);

INSERT OR IGNORE INTO garment (name, category_id, sprite_path, score_theme, price)
VALUES ('Baskets', (SELECT id FROM category WHERE name='shoes'), 'assets/clothes/shoes/sneakers.png', 'sport', 10);

INSERT OR IGNORE INTO garment (name, category_id, sprite_path, score_theme, price)
VALUES ('Talons', (SELECT id FROM category WHERE name='shoes'), 'assets/clothes/shoes/heels.png', 'soiree', 30);

INSERT OR IGNORE INTO garment (name, category_id, sprite_path, score_theme, price)
VALUES ('Lunettes', (SELECT id FROM category WHERE name='accessory'), 'assets/clothes/accessories/glasses.png', 'travail', 10);

INSERT OR IGNORE INTO garment (name, category_id, sprite_path, score_theme, price)
VALUES ('Sac', (SELECT id FROM category WHERE name='accessory'), 'assets/clothes/accessories/bag.png', 'soiree', 15);
